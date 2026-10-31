from pathlib import Path
import struct, json, hashlib, subprocess, sys, os

H = Path(__file__).resolve().parent
ROOT = H.parent
LLVM = Path(r'C:\Program Files\LLVM\bin')
BASE = ROOT / 'local_only' / 'stock.elf'
SHA = '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'
ORIGINAL_SELF = ROOT / 'local_only' / 'stock_ps2_netemu.self'
SELF_SHA = 'bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a'

for d in ['build', 'evidence', 'tmp']:
    (H / d).mkdir(exist_ok=True)
(ROOT / 'local_only' / 'p1d').mkdir(parents=True, exist_ok=True)

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
    import runpy
    a = runpy.run_path(str(H / 'ppcasm.py'))
    code = bytearray(0x100)  # 256 bytes for trampolines (0x4800..0x4900)

    # 1. lv1_open_device at 0x4820 (sc 0 with r11=0x800000aa)
    asm_open = a['Assembler'](0x4820)
    asm_open.asm('li r11, 0xaa\noris r11, r11, 0x8000\nsc 0\nblr\n')
    b_open, _ = asm_open.finish()
    assert len(b_open) <= 16
    code[0x4820 - 0x4800 : 0x4820 - 0x4800 + len(b_open)] = b_open
    syms['lv1_open_device'] = 0x4820

    # 2. lv1_close_device at 0x4830 (sc 0 with r11=0x800000ab)
    asm_close = a['Assembler'](0x4830)
    asm_close.asm('li r11, 0xab\noris r11, r11, 0x8000\nsc 0\nblr\n')
    b_close, _ = asm_close.finish()
    assert len(b_close) <= 16
    code[0x4830 - 0x4800 : 0x4830 - 0x4800 + len(b_close)] = b_close
    syms['lv1_close_device'] = 0x4830

    # 3. repo_read at 0x4840 and entry_menu at 0x4880
    entries = [
        ('repo_read', 0x4840, 0x111eb8, False),
        ('entry_menu', 0x4880, syms['s4_menu'], True)
    ]
    for name, pc, target, payload in entries:
        toc = syms['.TOC.'] if payload else 0x751280
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
            f'blr'
        )
        if name == 'entry_menu':
            source = source.replace(f'bl {target}', f'lwz r3,44(r24)\nbl {target}').replace('nop\nld r2', 'mr r4,r3\nld r2')
        asm = a['Assembler'](pc)
        asm.asm(source)
        b, rows = asm.finish()
        assert len(b) <= 64, f'{name} trampoline exceeds 64 bytes'
        code[pc - 0x4800 : pc - 0x4800 + len(b)] = b
        syms[name] = pc
    return bytes(code)

def build_labels(variant):
    STR_STRIDE = 64

    # Page A: P1D-A DONE open(9,0,0) rc=<name> or P1D-B DONE close(4,2) rc=<name>
    names = [
        "NONE",                     # 0: not attempted
        "SUCCESS",                  # 1: 0
        "RESOURCE_SHORTAGE",        # 2: -2
        "NO_PRIVILEGE",             # 3: -3
        "DENIED_BY_POLICY",         # 4: -4
        "ACCESS_VIOLATION",         # 5: -5
        "NO_ENTRY",                 # 6: -6
        "BUSY",                     # 7: -9
        "EMPTY",                    # 8: -10
        "NOT_OWNER/WRONG_STATE",    # 9: -11
        "INVALID_PARAMETER",        # 10: -17
        "HEX",                      # 11: other
    ]
    labels_a = []
    for name in names:
        if variant == 'A':
            s = f"P1D-A DONE open(9,0,0) rc={name}"
        else:
            s = f"P1D-B DONE close(4,2) rc={name}"
        assert len(s) < STR_STRIDE, f"Page A string too long: {s}"
        labels_a.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))
    blob_a = b''.join(labels_a)

    # Page B: raw rc as hex (low 32 bits) plus common LV1 code name
    # 0..255: 0xFFFFFF00..0xFFFFFFFF (-256..-1)
    # 256..511: 0x00000000..0x000000FF (0..255)
    # 512..527: 16 fallback patterns for other high nibbles
    # 528: "RC: NOT ATTEMPTED"
    code_names = {
        0: "SUCCESS",
        -2: "RESOURCE_SHORTAGE",
        -3: "NO_PRIVILEGE",
        -4: "DENIED_BY_POLICY",
        -5: "ACCESS_VIOLATION",
        -6: "NO_ENTRY",
        -9: "BUSY",
        -10: "EMPTY",
        -11: "NOT_OWNER/WRONG_STATE",
        -17: "INVALID_PARAMETER",
    }
    labels_b = []
    # 0..255: FFFFFF00..FFFFFFFF
    for k in range(256):
        val = 0xFFFFFF00 | k
        dec = val - 0x100000000
        name = code_names.get(dec, "HEX")
        s = f"RC={val:08X} ({dec}) {name}"
        assert len(s) < STR_STRIDE, f"Page B string too long: {s}"
        labels_b.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))

    # 256..511: 00000000..000000FF
    for k in range(256):
        val = k
        name = "SUCCESS" if val == 0 else "HEX"
        s = f"RC={val:08X} ({val}) {name}"
        assert len(s) < STR_STRIDE, f"Page B string too long: {s}"
        labels_b.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))

    # 512..527: other high nibbles
    for h in range(16):
        s = f"RC={h:X}XXXXXXX (UNCOMMON CODE HEX)"
        assert len(s) < STR_STRIDE, f"Page B fallback too long: {s}"
        labels_b.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))

    # 528: not attempted
    s = "RC: NOT ATTEMPTED"
    labels_b.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))
    assert len(labels_b) == 529
    blob_b = b''.join(labels_b)

    # Page C: optical node summary + HDD control (type/ids)
    # r (0..4) * 901 + h_idx (0..900) = 4505 strings
    rom_prefixes = [
        "NO ROM DEV (R=0)",                     # 0
        "ROM B=04 D=02 P=0 ID=4/2",             # 1
        "ROM B=05 D=00 P=0 ID=5/0",             # 2
        "ROM B=04 D=02",                         # 3
        "ROM DEV FOUND",                         # 4
    ]
    ph_strs = ["PH=-/-", "PH=EMU", "PH=GX", "PH=BOTH"]
    hdd_suffixes = ["HDD: NOT FOUND"]           # h_idx = 0
    for b in range(9):
        for d in range(5):
            for p in range(5):
                for ph in range(4):
                    b_str = str(b) if b < 8 else "?"
                    d_str = str(d) if d < 4 else "?"
                    p_str = str(p) if p < 4 else "?"
                    hdd_suffixes.append(f"HDD B={b_str} D={d_str} P={p_str} {ph_strs[ph]}")
    assert len(hdd_suffixes) == 901

    labels_c = []
    for r in range(5):
        r_pre = rom_prefixes[r]
        for h in range(901):
            h_suf = hdd_suffixes[h]
            s = f"{r_pre} {h_suf}"
            assert len(s) < STR_STRIDE, f"Page C string too long: {s}"
            labels_c.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))
    assert len(labels_c) == 4505
    blob_c = b''.join(labels_c)

    # Page D: OP:%s CL:%s RP:%s (1152 strings, padded to STR_STRIDE bytes)
    op_strs = ["OP:SKIP", "OP:0(OK)", "OP:-2(SHORT)", "OP:-3(NO_PRIV)", "OP:-4(DENIED)",
               "OP:-5(ACC_VIOL)", "OP:-6(NO_ENT)", "OP:-9(BUSY)", "OP:-10(EMPTY)",
               "OP:-11(STATE)", "OP:-17(PARAM)", "OP:ERR(HEX)"]
    cl_strs = ["CL:--", "CL:0(OK)", "CL:-2(SHORT)", "CL:-3(NO_PRIV)", "CL:-4(DENIED)",
               "CL:-5(ACC_VIOL)", "CL:-6(NO_ENT)", "CL:-9(BUSY)", "CL:-10(EMPTY)",
               "CL:-11(STATE)", "CL:-17(PARAM)", "CL:ERR(HEX)"]
    rp_strs = ["RP:0(OK)", "RP:-1(ENOENT)", "RP:-6(FA)", "RP:-2(FE)", "RP:-3(FD)",
               "RP:-4(FC)", "RP:-5(FB)", "RP:ERR"]
    labels_d = []
    for op in range(12):
        for cl in range(12):
            for rp in range(8):
                s = f"{op_strs[op]} {cl_strs[cl]} {rp_strs[rp]}"
                assert len(s) < STR_STRIDE, f"Page D string too long: {s}"
                labels_d.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))
    assert len(labels_d) == 1152
    blob_d = b''.join(labels_d)

    symbols = {}
    data = bytearray()
    symbols['labels_page_a'] = 0x74e930 + len(data)
    data.extend(blob_a)
    symbols['labels_page_b'] = 0x74e930 + len(data)
    data.extend(blob_b)
    symbols['labels_page_c'] = 0x74e930 + len(data)
    data.extend(blob_c)
    symbols['labels_page_d'] = 0x74e930 + len(data)
    data.extend(blob_d)

    # Pad data to 16 bytes
    data.extend(bytes((-len(data)) % 16))
    return symbols, bytes(data)

def build_variant(variant):
    print(f"\n==================================================")
    print(f"Building P1d Variant {variant}...")
    print(f"==================================================")

    original = BASE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SHA, "stock.elf SHA256 mismatch"
    orig_self = ORIGINAL_SELF.read_bytes()
    assert hashlib.sha256(orig_self).hexdigest() == SELF_SHA, "stock SELF SHA256 mismatch"

    # Mailbox at 0x930F20 must be all-zero in stock
    assert not any(original[vaoff(original, 0x930f20) : vaoff(original, 0x930f20) + 96]), "mailbox not zero"

    # Build immutable labels
    symbols, label_data = build_labels(variant)
    end = 0x74e930 + len(label_data)
    assert end < 0x821000, f"extended RO segment exceeds 0x821000: {hex(end)}"
    print(f"Generated immutable labels for Variant {variant}: {len(label_data)} bytes (ends at {hex(end)})")

    # Linker script
    linker = '''OUTPUT_FORMAT(elf64-powerpc)
ENTRY(s4_menu)
SECTIONS {
  . = 0x4900;
  .text : { *(.text) *(.text.*) }
  .rodata : { *(.rodata*) }
  . = ALIGN(8);
  .toc : { *(.toc*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
'''
    linker += '\n'.join(f'{k} = {v:#x};' for k, v in symbols.items()) + '\n'
    linker += 'repo_read = 0x4840;\n'
    linker += 'lv1_open_device = 0x4820;\n'
    linker += 'lv1_close_device = 0x4830;\n'
    (H / 'build' / f'link_{variant}.ld').write_text(linker)

    # Compile C payload
    flags = [
        '--target=powerpc64-unknown-linux-gnu', '-mcpu=970', '-mabi=elfv2',
        '-mno-altivec', '-mno-vsx', '-msoft-float', '-ffreestanding',
        '-fno-builtin', '-fno-stack-protector', '-fno-pic',
        '-fno-asynchronous-unwind-tables', '-fno-unwind-tables',
        '-Oz', '-fno-vectorize', '-fno-slp-vectorize',
        '-Wall', '-Wno-unused-function', '-Wextra', '-Werror',
        f"-DPROBE_VARIANT='{variant}'",
        '-S', '-emit-llvm'
    ]
    def run(args):
        r = subprocess.run([str(x) for x in args], cwd=H, capture_output=True, text=True)
        with (H / 'evidence' / f'build_{variant}.log').open('a') as f:
            f.write(' '.join(str(x) for x in args) + '\n' + r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)

    print(f"Compiling probe.c with Clang (PROBE_VARIANT='{variant}')...")
    ll_out = H / 'build' / f'probe_{variant}.ll'
    run([LLVM / 'clang.exe', *flags, 'src/probe.c', '-o', str(ll_out)])
    ll_out.write_text(ll_out.read_text().replace(', target_mem: none', ''))

    # Run IR provenance audit
    print(f"Running IR pointer provenance audit for Variant {variant}...")
    import runpy
    ir_auditor = runpy.run_path(str(H / 'audit_ir.py'))
    ir_auditor['audit'](ll_out, variant=variant)

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
    (H / 'build' / f'probe_{variant}.o').write_bytes(obj)
    (H / 'build' / f'probe_{variant}_compiler.s').write_text(tm.emit_assembly(module))

    print(f"Linking payload for Variant {variant}...")
    payload_elf = H / 'build' / f'probe_payload_{variant}.elf'
    payload_bin = H / 'build' / f'probe_{variant}.bin'
    run([LLVM / 'ld.lld.exe', '-m', 'elf64ppc', '-T', f'build/link_{variant}.ld', '--no-undefined', f'--Map=build/probe_{variant}.map', f'build/probe_{variant}.o', '-o', str(payload_elf)])
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

    trampolines = make_entries(syms)
    p_bin = payload_bin.read_bytes()
    code = bytearray(0x100 + len(p_bin))
    code[:0x100] = trampolines
    code[0x100:] = p_bin
    assert 0x4800 + len(code) <= 0x7FF0, f"Code slot exceeded: {hex(0x4800 + len(code))} > 0x7FF0"
    print(f"Payload code size: {len(code)} bytes (0x4800..{hex(0x4800 + len(code))}), slot capacity 14320 bytes")

    po, so, ph, sh = headers(original)
    p = ph[1]  # PHDR1 (RO segment)
    assert p[3] + p[5] == 0x74e930

    insertion = ph[2][2]  # file offset of PHDR2
    shift = ((max(0, p[2] + end - p[3] - insertion) + 65535) // 65536) * 65536
    e = bytearray(original[:insertion]) + bytearray(shift) + bytearray(original[insertion:])
    newso = so + shift

    patches = []
    def patch(o, b, why, expected=None):
        old = bytes(e[o : o + len(b)])
        assert expected is None or old == expected, f"{why}: expected {expected.hex() if expected else None}, got {old.hex()}"
        e[o : o + len(b)] = b
        patches.append(dict(file_offset=hex(o), length=len(b), original=old.hex(), new=b.hex(), purpose=why))

    # ELF section table relocation
    patch(40, struct.pack('>Q', newso), 'ELF section table relocation', struct.pack('>Q', so))
    # PHDR2 file offset
    patch(po + 112 + 8, struct.pack('>Q', ph[2][2] + shift), 'PHDR2 file offset only', struct.pack('>Q', ph[2][2]))
    # Section offsets
    for j, section in enumerate(sh):
        if section[4] >= insertion:
            patch(newso + j * 64 + 24, struct.pack('>Q', section[4] + shift), f'Section file offset relocation {j}', struct.pack('>Q', section[4]))

    # Patch code slot
    patch(vaoff(e, 0x4800), bytes(code), f'PPC64 payload in code slot (Variant {variant})', bytes(len(code)))

    # Fail-open hook check: 0x270FFC MUST hold 0xe882cea8
    patch(vaoff(e, 0x270FFC), branch(0x270FFC, syms['entry_menu']), 'Hook menu-row selector at 0x270FFC', bytes.fromhex('e882cea8'))

    # Extend PHDR1 RO filesz/memsz
    newsize = end - p[3]
    patch(po + 56 + 32, struct.pack('>QQ', newsize, newsize), 'PHDR1 RO filesz/memsz', struct.pack('>QQ', p[5], p[6]))
    assert sh[33][3] + sh[33][5] == 0x74e930
    patch(newso + 33 * 64 + 32, struct.pack('>Q', end - sh[33][3]), 'Last RO section size', struct.pack('>Q', sh[33][5]))

    # Insert label data
    dataoff = p[2] + p[5]
    patch(dataoff, label_data, f'Immutable diagnostic label tables (Variant {variant})', bytes(len(label_data)))

    assert len(e) == len(original) + shift
    assert e[insertion + shift : insertion + shift + ph[2][5]] == original[insertion : insertion + ph[2][5]]

    # Byte diff verification
    mapped = bytearray(original[:insertion]) + bytearray(shift) + bytearray(original[insertion:])
    covered = bytearray(len(e))
    for t in patches:
        o = int(t['file_offset'], 16)
        covered[o : o + t['length']] = b'\1' * t['length']
    changed = sum(a != b for a, b in zip(mapped, e))
    assert all(a == b or covered[j] for j, (a, b) in enumerate(zip(mapped, e)))
    assert headers(e)[2][0] == ph[0] and headers(e)[2][2][3:] == ph[2][3:]

    # Write patched ELF to local_only/p1d/
    out_elf = ROOT / 'local_only' / 'p1d' / f'ps2_netemu_p1d_{variant}.elf'
    out_elf.write_bytes(e)
    elf_sha = hashlib.sha256(e).hexdigest()
    print(f"Patched ELF written: {out_elf} ({len(e)} bytes, sha256={elf_sha})")

    # Repack SELF
    out_self = ROOT / 'local_only' / 'p1d' / f'ps2_netemu_p1d_{variant}.self'
    print(f"Repacking SELF to {out_self}...")
    pack = runpy.run_path(str(H / 'resign_self_installed.py'))
    pack['main'](out_elf, out_self)
    self_sha = hashlib.sha256(out_self.read_bytes()).hexdigest()
    print(f"Repacked SELF: {out_self} ({out_self.stat().st_size} bytes, sha256={self_sha})")

    # Round trip verification: decrypt with selfdec.py
    print(f"Verifying SELF round-trip with selfdec.py for Variant {variant}...")
    roundtrip_elf = ROOT / 'local_only' / 'p1d' / f'roundtrip_{variant}.elf'
    dec = runpy.run_path(str(H / 'selfdec.py'))
    key_vault = Path(r'C:\Users\remus\ps3buzz-console\raw_capture_debug11\dependencies\dl\key_vault.cpp')
    dec['main'](str(key_vault), str(out_self), str(roundtrip_elf))

    rt_data = roundtrip_elf.read_bytes()
    assert len(rt_data) == len(e), f"Roundtrip ELF length mismatch: {len(rt_data)} vs {len(e)}"
    assert hashlib.sha256(rt_data).hexdigest() == elf_sha, "Roundtrip ELF SHA256 mismatch!"
    print(f"SELF round-trip verified: decrypted ELF matches patched ELF byte for byte!")

    # Patch summary table
    table = dict(
        variant=f'P1D_{variant}',
        probe_variant=variant,
        baseline=str(BASE),
        baseline_sha256=SHA,
        elf_sha256=elf_sha,
        self_sha256=self_sha,
        elf_size=len(e),
        self_size=out_self.stat().st_size,
        code_start='0x4800',
        code_end=hex(0x4800 + len(code)),
        code_size=len(code),
        data_start='0x74e930',
        data_end=hex(end),
        data_size=len(label_data),
        changed_bytes=changed,
        symbols=syms,
        patches=patches
    )
    (H / 'evidence' / f'p1d_{variant}_patch_table.json').write_text(json.dumps(table, indent=2))
    print(f"Build complete for Variant {variant}! Table saved to evidence/p1d_{variant}_patch_table.json")
    return elf_sha, self_sha

def main():
    print("Checking input baseline...")
    original = BASE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SHA, "stock.elf SHA256 mismatch"
    orig_self = ORIGINAL_SELF.read_bytes()
    assert hashlib.sha256(orig_self).hexdigest() == SELF_SHA, "stock SELF SHA256 mismatch"

    elf_sha_a, self_sha_a = build_variant('A')
    elf_sha_b, self_sha_b = build_variant('B')

    print("\n==================================================")
    print("P1d BUILD SUMMARY")
    print("==================================================")
    print(f"Variant A ELF:  local_only/p1d/ps2_netemu_p1d_A.elf  ({elf_sha_a})")
    print(f"Variant A SELF: local_only/p1d/ps2_netemu_p1d_A.self ({self_sha_a})")
    print(f"Variant B ELF:  local_only/p1d/ps2_netemu_p1d_B.elf  ({elf_sha_b})")
    print(f"Variant B SELF: local_only/p1d/ps2_netemu_p1d_B.self ({self_sha_b})")
    print("Both round-trips verified byte-for-byte exact.")

if __name__ == '__main__':
    main()
