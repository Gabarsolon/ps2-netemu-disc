"""Local-only minimal BC168 control; no console/network/install operations.

Run with python -B. All generated files stay in local_only/autoreturn.
Does NOT import or run the optical experiment's build.py.
"""
from pathlib import Path
import hashlib
import json
import runpy
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'local_only/autoreturn'
LLVM = Path(r'C:\Program Files\LLVM\bin')
ELF_SHA = '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'
SELF_SHA = 'bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a'
SLOT, END, HOOK, NATIVE_TOC = 0x4800, 0x7ff0, 0xbc168, 0x751280

def digest(data):
    return hashlib.sha256(data).hexdigest()

def phdrs(data):
    off = struct.unpack_from('>Q', data, 32)[0]
    return [struct.unpack_from('>IIQQQQQQ', data, off + 56*i)
            for i in range(struct.unpack_from('>H', data, 56)[0])]

def vaoff(data, address):
    for p in phdrs(data):
        if p[0] == 1 and p[3] <= address < p[3]+p[5]:
            return p[2]+address-p[3]
    raise ValueError(hex(address))

def run(args):
    p = subprocess.run([str(x) for x in args], cwd=HERE,
                       capture_output=True, text=True)
    with (OUT/'build.log').open('a', encoding='utf-8') as f:
        f.write(subprocess.list2cmdline([str(x) for x in args])+'\n'+p.stdout+p.stderr)
    if p.returncode:
        raise RuntimeError(p.stdout+p.stderr)

def asm(source, pc):
    a = runpy.run_path(str(HERE/'ppcasm.py'))['Assembler'](pc)
    a.asm(source)
    return a.finish()

def trampoline(pc, target, toc):
    # Exact generic ELFv2 C-entry / native-TOC pattern from Buzz build.
    source = (f'mflr r0\nstd r0,16(r1)\nstdu r1,-128(r1)\n'
              f'std r2,120(r1)\nlis r2,{(toc+0x8000)>>16}\n'
              f'addi r2,r2,{((toc+0x8000)&0xffff)-0x8000}\n'
              f'lis r12,{(target+0x8000)>>16}\n'
              f'addi r12,r12,{((target+0x8000)&0xffff)-0x8000}\n'
              f'bl {target}\nnop\nld r2,120(r1)\naddi r1,r1,128\n'
              f'ld r0,16(r1)\nmtlr r0\nblr\n')
    code, rows = asm(source, pc)
    assert len(code) <= 64
    return code, rows

def build():
    # Validate original files and ignore rules before producing binary output.
    original = (ROOT/'local_only/stock.elf').read_bytes()
    template = (ROOT/'local_only/stock_ps2_netemu.self').read_bytes()
    assert digest(original) == ELF_SHA and digest(template) == SELF_SHA
    assert subprocess.run(['git', 'check-ignore', '-q', 'local_only/autoreturn/payload.o'],
                          cwd=ROOT).returncode == 0
    assert original[vaoff(original, HOOK):vaoff(original, HOOK)+4].hex() == 'f821fec1'
    assert not any(original[vaoff(original, SLOT):vaoff(original, SLOT)+END-SLOT])
    assert not any(original[vaoff(original, 0x930f20):vaoff(original, 0x930f20)+96])
    OUT.mkdir(parents=True, exist_ok=True)
    flags = ['--target=powerpc64-unknown-linux-gnu', '-mcpu=970', '-mbig-endian',
             '-mabi=elfv2', '-mno-altivec', '-mno-vsx', '-msoft-float',
             '-ffreestanding', '-fno-builtin', '-fno-stack-protector', '-fno-pic',
             '-fno-asynchronous-unwind-tables', '-fno-unwind-tables',
             '-Oz', '-fno-vectorize', '-fno-slp-vectorize', '-Wall', '-Wextra',
             '-Werror', '-S', '-emit-llvm']
    run([LLVM/'clang.exe', *flags, HERE/'src/autoreturn.c', '-o', OUT/'payload.ll'])
    ll = (OUT/'payload.ll').read_text().replace(', target_mem: none', '')
    (OUT/'payload.ll').write_text(ll)
    auditor = runpy.run_path(str(HERE/'audit_ir.py'))
    audit = auditor['audit'](OUT/'payload.ll')
    import llvmlite.binding as llvm
    llvm.set_option('autoreturn', '-disable-ppc-ctrloops')
    llvm.initialize_all_targets()
    llvm.initialize_all_asmprinters()
    module = llvm.parse_assembly(ll)
    module.verify()
    tm = llvm.Target.from_triple(module.triple).create_target_machine(
        cpu='970', features='-altivec,-vsx', reloc='static',
        codemodel='small', abiname='elfv2')
    obj = tm.emit_object(module)
    assert struct.unpack_from('>I', obj, 48)[0] == 2, 'ELFv2 required'
    (OUT/'payload.o').write_bytes(obj)
    (OUT/'payload_compiler.s').write_text(tm.emit_assembly(module))
    linker = '''OUTPUT_FORMAT(elf64-powerpc)
ENTRY(autoreturn_refresh)
SECTIONS {
 . = 0x4900;
 .text : { *(.text .text.*) }
 .rodata : { *(.rodata .rodata.*) }
 . = ALIGN(8);
 .toc : { *(.toc .toc.*) }
 .data : { *(.data .data.*) }
 .bss : { *(.bss .bss.*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
native_refresh = 0x4840;
native_clock = 0x4880;
'''
    (OUT/'link.ld').write_text(linker)
    run([LLVM/'ld.lld.exe', '-m', 'elf64ppc', '-T', OUT/'link.ld', '--no-undefined',
         '--Map='+str(OUT/'payload.map'), OUT/'payload.o', '-o', OUT/'payload.elf'])
    from elftools.elf.elffile import ELFFile
    with (OUT/'payload.elf').open('rb') as f:
        pe = ELFFile(f)
        syms = {s.name: s['st_value'] for s in pe.get_section_by_name('.symtab').iter_symbols()}
        for name in ['.bss', '.data', '.sdata', '.sbss', '.opd']:
            sec = pe.get_section_by_name(name)
            assert sec is None or sec['sh_size'] == 0, ('mutable/ELFv1 section', name)
        sections = [s for s in pe.iter_sections() if s['sh_flags'] & 2 and s['sh_size']]
        assert all(0x4900 <= s['sh_addr'] < s['sh_addr']+s['sh_size'] <= END for s in sections)
    run([LLVM/'llvm-objcopy.exe', '-O', 'binary', OUT/'payload.elf', OUT/'payload.bin'])
    body = (OUT/'payload.bin').read_bytes()
    code = bytearray(0x100) + body
    entries = [('entry_refresh', 0x4800, syms['autoreturn_refresh'], syms['.TOC.']),
               ('native_refresh', 0x4840, 0x48c0, NATIVE_TOC),
               ('native_clock', 0x4880, 0xb9cd0, NATIVE_TOC)]
    listing = []
    for name, pc, target, toc in entries:
        blob, rows = trampoline(pc, target, toc)
        code[pc-SLOT:pc-SLOT+len(blob)] = blob
        listing.extend(rows)
        syms[name] = pc
    # Relocate ONLY the verified stack update; resume the untouched body.
    relocated, rows = asm('stdu r1,-320(r1)\nb 0xbc16c\n', 0x48c0)
    assert relocated[:4] == bytes.fromhex('f821fec1')
    code[0xc0:0xc8] = relocated
    listing.extend(rows)
    assembly_audit = auditor['audit_assembly'](OUT/'payload_compiler.s', listing)
    assert SLOT+len(code) <= END
    patch, _ = asm('b 0x4800', HOOK)  # tail hook preserves original caller LR
    final = bytearray(original)
    off = vaoff(original, SLOT)
    final[off:off+len(code)] = code
    hookoff = vaoff(original, HOOK)
    final[hookoff:hookoff+4] = patch
    assert len(final) == len(original) and phdrs(final) == phdrs(original)
    assert all(a == b or off <= i < off+len(code) or hookoff <= i < hookoff+4
               for i, (a, b) in enumerate(zip(original, final)))
    # Auditable source/assembly inputs; no native body stores claimed audited.
    (OUT/'trampolines.json').write_text(json.dumps(listing, indent=2)+'\n')
    (OUT/'ps2_netemu_autoreturn.elf').write_bytes(final)
    pack = runpy.run_path(str(HERE/'resign_self_installed.py'))
    pack['main'](OUT/'ps2_netemu_autoreturn.elf', OUT/'ps2_netemu_autoreturn.self')
    assert (OUT/'ps2_netemu_autoreturn.roundtrip.elf').read_bytes() == final
    table = dict(status='BUILT_OFFLINE_NOT_HARDWARE_TESTED',
                 stock_elf_sha256=ELF_SHA, stock_self_sha256=SELF_SHA,
                 elf_sha256=digest(final), self_sha256=digest((OUT/'ps2_netemu_autoreturn.self').read_bytes()),
                 code_bytes=len(code), code_end=hex(SLOT+len(code)), symbols=syms,
                 ir_audit=audit, assembly_audit=assembly_audit['status'],
                 source_sha256=digest((HERE/'src/autoreturn.c').read_bytes()),
                 payload_ir_sha256=digest(ll.encode()),
                 payload_object_sha256=digest(obj),
                 segment_headers_unchanged=True, only_code_and_one_hook_changed=True,
                 decrypt_roundtrip_exact=True, ppc_validation='NOT RUN: sole JVM occupied',
                 hardware='NOT TESTED: periodic controller-free execution and reason-only return UNKNOWN')
    (OUT/'build_review.json').write_text(json.dumps(table, indent=2)+'\n')
    print(json.dumps(table, indent=2))
    return table

if __name__ == '__main__':
    build()
