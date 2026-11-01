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
(ROOT / 'local_only' / 'p8').mkdir(parents=True, exist_ok=True)

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

def make_hcall_wrapper(stock_elf_bytes):
    """Construct generic safe hypercall wrapper (180 bytes) at 0x4800 (sc 0 at 0x4858).
    29 instructions are byte-for-byte identical to the stock helper (0x111eb8).
    Extended in P2 with 0x7D284B78 (mr r8, r9) at offset 0x48 to pass 6th parameter.
    """
    stock_off = 0x121eb8  # va 0x111eb8 in stock.elf
    stock_bytes = stock_elf_bytes[stock_off : stock_off + 180]
    assert len(stock_bytes) == 180, f"Expected 180 bytes, got {len(stock_bytes)}"

    wrapper = bytearray(stock_bytes)

    changes = {
        0x04: 0x60000000,  # nop (replaces stock lo32 extraction)
        0x08: 0x60000000,  # nop (replaces stock hi32 extraction)
        0x18: 0x3FC00093,  # lis r30, 0x93
        0x1C: 0x3BDE0F70,  # addi r30, r30, 0x0f70 (r30 = 0x930F70 = &raw_val1)
        0x20: 0x3BFE0008,  # addi r31, r30, 8      (r31 = 0x930F78 = &raw_val2)
        0x24: 0x7C6B1B78,  # mr r11, r3           (r11 = num)
        0x28: 0x7C832378,  # mr r3, r4            (r3 = a1)
        0x38: 0x7CA42B78,  # mr r4, r5            (r4 = a2)
        0x3C: 0x7CC53378,  # mr r5, r6            (r5 = a3)
        0x40: 0x7CE63B78,  # mr r6, r7            (r6 = a4)
        0x44: 0x7D074378,  # mr r7, r8            (r7 = a5)
        0x48: 0x7D284B78,  # mr r8, r9            (r8 = a6)  [P2 extension]
        0x4C: 0x60000000,  # nop
        0x50: 0x60000000,  # nop
        0xA8: 0x60000000,  # nop (replaces panic arg)
        0xAC: 0x60000000,  # nop (replaces panic branch)
        0xB0: 0x60000000,  # nop (identical to stock)
    }

    for off, val in changes.items():
        struct.pack_into('>I', wrapper, off, val)

    ident = sum(1 for i in range(0, 180, 4) if wrapper[i:i+4] == stock_bytes[i:i+4])
    assert ident == 29, f"Expected 29 identical instructions, got {ident}"

    sc_val, = struct.unpack_from('>I', wrapper, 0x58)
    assert sc_val == 0x44000002, f"Expected sc 0 at +0x58, got {hex(sc_val)}"

    return bytes(wrapper)

def make_entries(syms, stock_elf_bytes):
    import runpy
    a = runpy.run_path(str(H / 'ppcasm.py'))
    code = bytearray(0x300)  # 768 bytes for wrapper + trampolines (0x4800..0x4B00)

    # 1. lv1_hcall at 0x4800 (180 bytes, 0x4800..0x48b4, sc 0 at 0x4858)
    b_wrapper = make_hcall_wrapper(stock_elf_bytes)
    assert len(b_wrapper) == 180
    code[0x00 : 0x00 + len(b_wrapper)] = b_wrapper
    syms['lv1_hcall'] = 0x4800

    # 2. Trampolines for stock functions and entry hook
    entries = [
        ('repo_read',             0x48C0, 0x111eb8, False),
        ('native_clock',          0x4900, 0x0b9cd0, 'jump'),
        ('native_alloc',          0x4920, 0x0b9848, False),
        ('stock_ufs_open',        0x4960, 0x1ecc5c, False),
        ('stock_ufs_close',       0x49A0, 0x1ecb10, False),
        ('stock_raw_read',        0x49E0, 0x1ed5cc, False),
        ('stock_raw_write',       0x4A20, 0x1ed458, False),
        ('stock_hdd_cache_flush', 0x4A60, 0x12cc98, False),
        ('get_r2',                0x4AA0, 0,        'raw_r2'),
        ('entry_menu',            0x4AC0, syms['s4_menu'], True),
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
                    f'lis r2,{(toc+0x8000)>>16}\n'
                    f'addi r2,r2,{((toc+0x8000)&0xffff)-0x8000}\n'
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
        assert len(b) <= 64, f'{name} trampoline exceeds 64 bytes (got {len(b)})'
        code[pc - 0x4800 : pc - 0x4800 + len(b)] = b
        syms[name] = pc
    return bytes(code)

def build_variant(variant_name, variant_code):
    print(f"\n==================================================")
    print(f"BUILDING P8 VARIANT {variant_name} (Code {variant_code})")
    print(f"==================================================")

    original = BASE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SHA, "stock.elf SHA256 mismatch"

    # Linker script targeting 0x4B00
    ld_script = """
    OUTPUT_FORMAT("elf64-powerpc")
    OUTPUT_ARCH(powerpc:common64)
    SECTIONS {
        . = 0x4B00;
        .text : {
            *(.text .text.*)
        }
        .rodata : {
            *(.rodata .rodata.*)
        }
        .data : {
            *(.data .data.*)
        }
        .opd : {
            *(.opd)
        }
        .toc : {
            *(.toc .toc.*)
        }
        .bss : {
            *(.bss .bss.*)
        }
    }
    repo_read = 0x48c0;
    native_clock = 0x4900;
    native_alloc = 0x4920;
    stock_ufs_open = 0x4960;
    stock_ufs_close = 0x49a0;
    stock_raw_read = 0x49e0;
    stock_raw_write = 0x4a20;
    stock_hdd_cache_flush = 0x4a60;
    get_r2 = 0x4aa0;
    lv1_hcall = 0x4800;
    """
    ld_path = H / 'build' / f'payload_p8_{variant_name}.ld'
    ld_path.write_text(ld_script)

    flags = [
        '-target', 'powerpc64-unknown-linux-gnu',
        '-mcpu=970',
        '-mbig-endian',
        '-mabi=elfv2',
        '-ffreestanding',
        '-fno-builtin',
        '-fno-stack-protector',
        '-fno-asynchronous-unwind-tables', '-fno-unwind-tables',
        '-Oz', '-fno-vectorize', '-fno-slp-vectorize',
        '-Wall', '-Wno-unused-function', '-Wextra', '-Werror',
        f'-DPROBE_VARIANT={variant_code}',
        '-S', '-emit-llvm'
    ]
    def run(args):
        r = subprocess.run([str(x) for x in args], cwd=H, capture_output=True, text=True)
        with (H / 'evidence' / f'build_p8_{variant_name}.log').open('a') as f:
            f.write(' '.join(str(x) for x in args) + '\n' + r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)

    print(f"Compiling probe.c with Clang for {variant_name}...")
    ll_out = H / 'build' / f'probe_p8_{variant_name}.ll'
    run([LLVM / 'clang.exe', *flags, 'src/probe.c', '-o', str(ll_out)])
    ll_out.write_text(ll_out.read_text().replace(', target_mem: none', ''))

    # Run IR provenance audit
    print(f"Running IR pointer provenance audit for {variant_name}...")
    import runpy
    ir_auditor = runpy.run_path(str(H / 'audit_ir.py'))
    ir_auditor['audit'](ll_out, variant=variant_name)

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
    (H / 'build' / f'probe_p8_{variant_name}.o').write_bytes(obj)
    (H / 'build' / f'probe_p8_{variant_name}_compiler.s').write_text(tm.emit_assembly(module))

    print(f"Linking payload for {variant_name}...")
    payload_elf = H / 'build' / f'probe_payload_p8_{variant_name}.elf'
    payload_bin = H / 'build' / f'probe_p8_{variant_name}.bin'
    run([LLVM / 'ld.lld.exe', '-m', 'elf64ppc', '-T', str(ld_path), '--no-undefined',
         f'--Map=build/probe_p8_{variant_name}.map', f'build/probe_p8_{variant_name}.o', '-o', str(payload_elf)])
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

    trampolines = make_entries(syms, original)
    p_bin = payload_bin.read_bytes()
    code = bytearray(0x300 + len(p_bin))
    code[:0x300] = trampolines
    code[0x300:] = p_bin
    assert 0x4800 + len(code) <= 0x7FF0, f"Code slot exceeded: {hex(0x4800 + len(code))} > 0x7FF0"
    print(f"Payload code size: {len(code)} bytes (0x4800..{hex(0x4800 + len(code))}), slot capacity 14320 bytes ({len(code)*100/14320:.1f}%)")

    # Patch original stock ELF in place (shift = 0, segment sizes unchanged)
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
    patch(code_file_off, bytes(code), f'PPC64 diagnostic payload in code slot ({variant_name})', bytes(len(code)))

    # 2. Hook menu-row selector at 0x270FFC
    hook_file_off = vaoff(e, 0x270FFC)
    patch(hook_file_off, branch(0x270FFC, syms['entry_menu']), f'Hook menu-row selector at 0x270FFC ({variant_name})', bytes.fromhex('e882cea8'))

    # Verify no shifts or segment corruption
    assert len(e) == len(original), f"ELF length changed: {len(e)} vs {len(original)}"
    assert headers(e)[2] == ph, "PHDR table changed"

    # Write patched ELF to local_only/p8/
    out_elf = ROOT / 'local_only' / 'p8' / f'ps2_netemu_p8_{variant_name}.elf'
    out_elf.write_bytes(e)
    elf_sha = hashlib.sha256(e).hexdigest()
    print(f"Patched ELF written: {out_elf} ({len(e)} bytes, sha256={elf_sha})")

    # Repack SELF
    out_self = ROOT / 'local_only' / 'p8' / f'ps2_netemu_p8_{variant_name}.self'
    print(f"Repacking SELF to {out_self}...")
    import runpy
    pack = runpy.run_path(str(H / 'resign_self_installed.py'))
    pack['main'](out_elf, out_self)
    self_sha = hashlib.sha256(out_self.read_bytes()).hexdigest()
    print(f"Repacked SELF: {out_self} ({out_self.stat().st_size} bytes, sha256={self_sha})")

    # Round trip verification: decrypt with selfdec.py
    print(f"Verifying SELF round-trip for {variant_name} with selfdec.py...")
    roundtrip_elf = ROOT / 'local_only' / 'p8' / f'roundtrip_{variant_name}.elf'
    dec = runpy.run_path(str(H / 'selfdec.py'))
    key_vault = Path(r'C:\Users\remus\ps3buzz-console\raw_capture_debug11\dependencies\dl\key_vault.cpp')
    dec['main'](str(key_vault), str(out_self), str(roundtrip_elf))

    rt_data = roundtrip_elf.read_bytes()
    assert len(rt_data) == len(e), f"Roundtrip ELF length mismatch: {len(rt_data)} vs {len(e)}"
    assert hashlib.sha256(rt_data).hexdigest() == elf_sha, f"Roundtrip ELF SHA256 mismatch for {variant_name}!"
    print(f"SELF round-trip verified for {variant_name}: decrypted ELF matches patched ELF byte for byte!")

    table = dict(
        variant=variant_name,
        code=variant_code,
        elf_sha256=elf_sha,
        self_sha256=self_sha,
        code_size=len(code),
        symbols=syms,
        patches=patches
    )
    return table

def main():
    variants = [
        ('T1', 1),
    ]
    summary = {}
    for vname, vcode in variants:
        t = build_variant(vname, vcode)
        summary[vname] = t

    (H / 'evidence' / 'p8_patch_table.json').write_text(json.dumps(summary, indent=2))
    print("\n==================================================")
    print("ALL P8 VARIANTS BUILT & VERIFIED SUCCESSFULLY!")
    print("==================================================")
    for vname, t in summary.items():
        print(f"  {vname}: ELF={t['elf_sha256'][:16]}... SELF={t['self_sha256'][:16]}... size={t['code_size']} bytes")

if __name__ == '__main__':
    main()
