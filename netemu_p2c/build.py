from pathlib import Path
import struct, json, hashlib, subprocess, sys, os, runpy

H = Path(__file__).resolve().parent
ROOT = H.parent
LLVM = Path(r'C:\Program Files\LLVM\bin')
BASE = ROOT / 'local_only' / 'stock.elf'
SHA = '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'
ORIGINAL_SELF = ROOT / 'local_only' / 'stock_ps2_netemu.self'
SELF_SHA = 'bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a'

for d in ['build', 'evidence', 'tmp']:
    (H / d).mkdir(exist_ok=True)
(ROOT / 'local_only' / 'p2c').mkdir(parents=True, exist_ok=True)

def headers(e):
    po, so = struct.unpack_from('>QQ', e, 32)
    pn = struct.unpack_from('>H', e, 56)[0]
    sn = struct.unpack_from('>H', e, 60)[0]
    return po, so, [list(struct.unpack_from('>IIQQQQQQ', e, po + 56 * i)) for i in range(pn)], [list(struct.unpack_from('>IIQQQQIIQQ', e, so + 64 * i)) for i in range(sn)]

def vaoff(e, a):
    for p in headers(e)[2]:
        if p[0] == 1 and p[3] <= a < p[3] + p[5]:
            return p[2] + a - p[3]
    raise ValueError(hex(a))

def symtab(path):
    from elftools.elf.elffile import ELFFile
    with open(path, 'rb') as f:
        e = ELFFile(f)
        return {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}

def branch(pc, to):
    return struct.pack('>I', 0x48000001 | ((to - pc) & 0x3fffffc))

def make_entries(syms):
    a = runpy.run_path(str(H / 'ppcasm.py'))
    code = bytearray(0xc0)  # 192 bytes for trampolines (0x4800..0x48C0)

    # 1. native_alloc at 0x4800 (target stock 0x0b9848, TOC 0x751280)
    # 2. native_clock at 0x4840 (target stock 0x0b9cd0, jump)
    # 3. get_r2       at 0x4860 (mr r3, 2; blr)
    # 4. entry_menu   at 0x4880 (target s4_menu, TOC syms['.TOC.'])
    entries = [
        ('native_alloc', 0x4800, 0x0b9848, False),
        ('native_clock', 0x4840, 0x0b9cd0, 'jump'),
        ('get_r2',       0x4860, 0,        'raw_r2'),
        ('entry_menu',   0x4880, syms['s4_menu'], True),
    ]
    for name, pc, target, payload in entries:
        if payload == 'jump':
            source = f'b {target:#x}\n'
        elif payload == 'raw_r2':
            source = 'mr r3,r2\nblr\n'
        else:
            toc = syms['.TOC.'] if payload else 0x751280
            if name == 'entry_menu':
                source = (
                    f'mflr r0\n'
                    f'std r0,16(r1)\n'
                    f'stdu r1,-128(r1)\n'
                    f'std r2,120(r1)\n'
                    f'mr r4,r2\n'
                    f'lis r12,{(target+0x8000)>>16}\n'
                    f'addi r12,r12,{((target+0x8000)&0xffff)-0x8000}\n'
                    f'lwz r3,44(r24)\n'
                    f'bl {target}\n'
                    f'mr r4,r3\n'
                    f'ld r2,120(r1)\n'
                    f'addi r1,r1,128\n'
                    f'ld r0,16(r1)\n'
                    f'mtlr r0\n'
                    f'blr\n'
                )
            else:
                source = (
                    f'mflr r0\n'
                    f'std r0,16(r1)\n'
                    f'stdu r1,-128(r1)\n'
                    f'std r2,120(r1)\n'
                    f'lis r2,{(toc+0x8000)>>16}\n'
                    f'addi r2,r2,{((toc+0x8000)&0xffff)-0x8000}\n'
                    f'lis r12,{(target+0x8000)>>16}\n'
                    f'addi r12,r12,{((target+0x8000)&0xffff)-0x8000}\n'
                    f'bl {target}\n'
                    f'nop\n'
                    f'ld r2,120(r1)\n'
                    f'addi r1,r1,128\n'
                    f'ld r0,16(r1)\n'
                    f'mtlr r0\n'
                    f'blr\n'
                )
        asm = a['Assembler'](pc)
        asm.asm(source)
        b, rows = asm.finish()
        assert len(b) <= 64, f'{name} trampoline exceeds 64 bytes'
        code[pc - 0x4800 : pc - 0x4800 + len(b)] = b
        syms[name] = pc
    return bytes(code)

def build_p2c():
    print(f"\n==================================================")
    print(f"Building P2C Diagnostic Probe (ps2_netemu_p2c)...")
    print(f"==================================================")

    original = BASE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SHA, "stock.elf SHA256 mismatch"
    orig_self = ORIGINAL_SELF.read_bytes()
    assert hashlib.sha256(orig_self).hexdigest() == SELF_SHA, "stock SELF SHA256 mismatch"

    # Mailbox at 0x930F20 must be all-zero in stock (96 bytes)
    assert not any(original[vaoff(original, 0x930f20) : vaoff(original, 0x930f20) + 96]), "mailbox not zero"

    # Linker script: payload starts at 0x48C0
    linker = '''OUTPUT_FORMAT(elf64-powerpc)
ENTRY(s4_menu)
SECTIONS {
  . = 0x48C0;
  .text : { *(.text) *(.text.*) }
  .rodata : { *(.rodata*) }
  . = ALIGN(8);
  .toc : { *(.toc*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
native_alloc = 0x4800;
native_clock = 0x4840;
get_r2 = 0x4860;
'''
    ld_path = H / 'build' / 'link_p2c.ld'
    ld_path.write_text(linker)

    # Compile C payload to LLVM IR
    flags = [
        '--target=powerpc64-unknown-linux-gnu', '-mcpu=970', '-mabi=elfv2',
        '-mno-altivec', '-mno-vsx', '-msoft-float', '-ffreestanding',
        '-fno-builtin', '-fno-stack-protector', '-fno-pic',
        '-fno-asynchronous-unwind-tables', '-fno-unwind-tables',
        '-Oz', '-fno-vectorize', '-fno-slp-vectorize',
        '-Wall', '-Wno-unused-function', '-Wextra', '-Werror',
        '-S', '-emit-llvm'
    ]
    def run(args):
        r = subprocess.run([str(x) for x in args], cwd=H, capture_output=True, text=True)
        with (H / 'evidence' / 'build_p2c.log').open('a') as f:
            f.write(' '.join(str(x) for x in args) + '\n' + r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)

    print("Compiling probe.c to LLVM IR with Clang...")
    ll_out = H / 'build' / 'probe_p2c.ll'
    run([LLVM / 'clang.exe', *flags, 'src/probe.c', '-o', str(ll_out)])
    ll_out.write_text(ll_out.read_text().replace(', target_mem: none', ''))

    # Run IR provenance audit
    print("Running IR pointer provenance audit...")
    ir_auditor = runpy.run_path(str(H / 'audit_ir.py'))
    ir_auditor['audit'](ll_out)

    # Compile LLVM IR to object code via llvmlite
    import llvmlite.binding as llvm
    llvm.initialize_all_targets()
    llvm.initialize_all_asmprinters()
    module = llvm.parse_assembly(ll_out.read_text())
    module.verify()
    tm = llvm.Target.from_triple(module.triple).create_target_machine(
        cpu='970', features='-altivec,-vsx', reloc='static', codemodel='small', abiname='elfv2'
    )
    obj = bytearray(tm.emit_object(module))
    assert struct.unpack_from('>I', obj, 48)[0] == 2, "ELFv2 ABI expected"
    (H / 'build' / 'probe_p2c.o').write_bytes(obj)
    (H / 'build' / 'probe_p2c_compiler.s').write_text(tm.emit_assembly(module))

    # Link payload
    print("Linking payload with lld...")
    payload_elf = H / 'build' / 'payload_p2c.elf'
    payload_bin = H / 'build' / 'payload_p2c.bin'
    run([LLVM / 'ld.lld.exe', '-m', 'elf64ppc', '-T', str(ld_path), '--no-undefined',
         '--Map=build/probe_p2c.map', 'build/probe_p2c.o', '-o', str(payload_elf)])
    run([LLVM / 'llvm-objcopy.exe', '-O', 'binary', str(payload_elf), str(payload_bin)])

    syms = symtab(payload_elf)
    from elftools.elf.elffile import ELFFile
    with open(payload_elf, 'rb') as f:
        pe = ELFFile(f)
        opd = pe.get_section_by_name('.opd')
        ob = opd.data() if opd else b''
        oa = opd['sh_addr'] if opd else 0
        for name, address in list(syms.items()):
            if oa <= address < oa + len(ob):
                syms[name + '_descriptor'] = address
                syms[name] = struct.unpack_from('>Q', ob, address - oa)[0]

    b_trampolines = make_entries(syms)
    p_bin = payload_bin.read_bytes()
    code = bytearray(0xc0 + len(p_bin))
    code[:0xc0] = b_trampolines
    code[0xc0:] = p_bin
    assert 0x4800 + len(code) <= 0x7FF0, f"Code exceeds cave: {hex(0x4800 + len(code))}"
    print(f"Total cave code size: {len(code)} bytes / 14320 bytes ({len(code)*100/14320:.1f}%)")

    # Patch original stock ELF (in-place: shift = 0)
    e = bytearray(original)
    po, so, ph, sh = headers(e)

    patches = []
    def patch(o, b, why, expected=None):
        old = bytes(e[o : o + len(b)])
        assert expected is None or old == expected, f"{why}: expected {expected.hex() if expected else None}, got {old.hex()}"
        e[o : o + len(b)] = b
        patches.append(dict(file_offset=hex(o), length=len(b), original=old.hex(), new=b.hex(), purpose=why))

    # 1. Patch code slot at va 0x4800
    code_file_off = vaoff(e, 0x4800)
    patch(code_file_off, bytes(code), 'PPC64 diagnostic payload in code slot (P2C)', bytes(len(code)))

    # 2. Hook menu-row selector at 0x270FFC
    hook_file_off = vaoff(e, 0x270FFC)
    patch(hook_file_off, branch(0x270FFC, syms['entry_menu']), 'Hook menu-row selector at 0x270FFC', bytes.fromhex('e882cea8'))

    # Verify no unexpected shifts or corruption
    assert len(e) == len(original)
    assert headers(e)[2] == ph

    # Write patched ELF to local_only/p2c/
    out_elf = ROOT / 'local_only' / 'p2c' / 'ps2_netemu_p2c.elf'
    out_elf.write_bytes(e)
    elf_sha = hashlib.sha256(e).hexdigest()
    print(f"Patched ELF written: {out_elf} ({len(e)} bytes, sha256={elf_sha})")

    # Repack SELF
    out_self = ROOT / 'local_only' / 'p2c' / 'ps2_netemu_p2c.self'
    print(f"Repacking SELF to {out_self}...")
    pack = runpy.run_path(str(H / 'resign_self_installed.py'))
    pack['main'](out_elf, out_self)
    self_sha = hashlib.sha256(out_self.read_bytes()).hexdigest()
    print(f"Repacked SELF: {out_self} ({out_self.stat().st_size} bytes, sha256={self_sha})")

    # Round trip verification: decrypt with selfdec.py
    print("Verifying SELF round-trip with selfdec.py...")
    roundtrip_elf = ROOT / 'local_only' / 'p2c' / 'roundtrip_p2c.elf'
    dec = runpy.run_path(str(H / 'selfdec.py'))
    key_vault = Path(r'C:\Users\remus\ps3buzz-console\raw_capture_debug11\dependencies\dl\key_vault.cpp')
    dec['main'](str(key_vault), str(out_self), str(roundtrip_elf))

    rt_data = roundtrip_elf.read_bytes()
    assert len(rt_data) == len(e), f"Roundtrip ELF length mismatch: {len(rt_data)} vs {len(e)}"
    assert hashlib.sha256(rt_data).hexdigest() == elf_sha, "Roundtrip ELF SHA256 mismatch!"
    print("SELF round-trip verified: decrypted ELF matches patched ELF byte for byte!")

    # Summary table
    table = dict(
        variant='P2C',
        elf_sha256=elf_sha,
        self_sha256=self_sha,
        code_size=len(code),
        symbols=syms,
        patches=patches
    )
    (H / 'evidence' / 'p2c_patch_table.json').write_text(json.dumps(table, indent=2))
    return table

if __name__ == '__main__':
    build_p2c()
