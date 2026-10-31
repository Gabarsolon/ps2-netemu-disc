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
(ROOT / 'local_only' / 'p2b').mkdir(parents=True, exist_ok=True)

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

    # Dictionary of changed offsets -> new 32-bit hex words
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

    # Assert exactly 29 instructions match stock byte-for-byte
    ident = sum(1 for i in range(0, 180, 4) if wrapper[i:i+4] == stock_bytes[i:i+4])
    assert ident == 29, f"Expected 29 identical instructions, got {ident}"

    # Assert sc 0 is at offset 0x58
    sc_val, = struct.unpack_from('>I', wrapper, 0x58)
    assert sc_val == 0x44000002, f"Expected sc 0 at +0x58, got {hex(sc_val)}"

    return bytes(wrapper)

def make_entries(syms, stock_elf_bytes):
    import runpy
    a = runpy.run_path(str(H / 'ppcasm.py'))
    code = bytearray(0x200)  # 512 bytes for wrapper + trampolines (0x4800..0x4A00)

    # 1. lv1_hcall at 0x4800 (180 bytes, 0x4800..0x48b4, sc 0 at 0x4858)
    b_wrapper = make_hcall_wrapper(stock_elf_bytes)
    assert len(b_wrapper) == 180
    code[0x00 : 0x00 + len(b_wrapper)] = b_wrapper
    syms['lv1_hcall'] = 0x4800

    # 2. repo_read at 0x48C0, native_clock at 0x4900, alloc_buffer at 0x4910, entry_menu at 0x4950, native_alloc at 0x4990
    entries = [
        ('repo_read', 0x48c0, 0x111eb8, False),
        ('native_clock', 0x4900, 0x0b9cd0, 'jump'),
        ('alloc_buffer', 0x4910, 0x019a5c, False),
        ('entry_menu', 0x4950, syms['s4_menu'], True),
        ('native_alloc', 0x4990, 0x0b9848, False),
    ]
    for name, pc, target, payload in entries:
        if payload == 'jump':
            source = f'b {target:#x}\n'
        else:
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

    rc_names = [
        "NOT_RUN",                  # 0: not attempted
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

    step_names = [
        "OPEN", "ALLOC_SHIM", "DMA_ALLOC", "MAP",
        "TUR", "INQ", "CAP", "READ", "UNMAP", "FREE", "CLOSE"
    ]

    # Page A: P2-<variant> DONE ALL OK or FAIL <step> rc=<name>
    labels_a = [
        f"P2-{variant} DONE ALL OK (STEPS COMPLETE)".encode('ascii').ljust(STR_STRIDE, b'\0'),
        f"P2-{variant} TIMEOUT AT TUR (ABORTED: NO UNMAP/CLOSE)".encode('ascii').ljust(STR_STRIDE, b'\0'),
        f"P2-{variant} TIMEOUT AT INQUIRY (ABORTED: NO UNMAP/CLOSE)".encode('ascii').ljust(STR_STRIDE, b'\0'),
        f"P2-{variant} TIMEOUT AT READ CAPACITY (ABORTED)".encode('ascii').ljust(STR_STRIDE, b'\0'),
        f"P2-{variant} TIMEOUT AT READ SECTOR 16 (ABORTED)".encode('ascii').ljust(STR_STRIDE, b'\0'),
    ]
    for s_name in step_names:
        for r_name in rc_names:
            s = f"P2-{variant} FAIL {s_name} rc={r_name}"
            assert len(s) < STR_STRIDE, f"Page A string too long: {s}"
            labels_a.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))
    assert len(labels_a) == 5 + 11 * 12  # 137 strings
    blob_a = b''.join(labels_a)

    # Page B: raw rc hex (530 strings)
    labels_b = [
        f"P2-{variant} RC: ALL CALLS SUCCESS (RC=00000000)".encode('ascii').ljust(STR_STRIDE, b'\0')
    ]
    for i in range(256):
        labels_b.append(f"P2-{variant} RC: -0x{256-i:02x} ({256-i})".encode('ascii').ljust(STR_STRIDE, b'\0'))
    for i in range(256):
        labels_b.append(f"P2-{variant} RC: +0x{i:02x} ({i})".encode('ascii').ljust(STR_STRIDE, b'\0'))
    for i in range(16):
        labels_b.append(f"P2-{variant} RC: 0x{i:x}xxxxxxx".encode('ascii').ljust(STR_STRIDE, b'\0'))
    labels_b.append(b"RC: NOT ATTEMPTED".ljust(STR_STRIDE, b'\0'))
    assert len(labels_b) == 530
    blob_b = b''.join(labels_b)

    # Page C: variant-specific data
    labels_c = []
    if variant == 'H0':
        labels_c.append(b"P2-H0 DATA: DMA ALLOC FAILED".ljust(STR_STRIDE, b'\0'))
        for rgn in range(8):
            labels_c.append(f"P2-H0 DATA: DMA REGION ID = {rgn}".encode('ascii').ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H0 DATA: DMA REGION ID >= 8".ljust(STR_STRIDE, b'\0'))
        assert len(labels_c) == 10
    elif variant == 'H1':
        labels_c.append(b"P2-H1 DATA: ALLOC SHIM FAILED".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H1 DATA: MAP DMA REGION FAILED".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H1 DATA: UNMAP DMA REGION FAILED".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H1 DATA: MAP & UNMAP SUCCESSFUL (BUFFER OK)".ljust(STR_STRIDE, b'\0'))
        assert len(labels_c) == 4
    elif variant == 'H2':
        labels_c.append(b"P2-H2 DATA: TUR TIMEOUT".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H2 DATA: INQUIRY TIMEOUT".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H2 DATA: TUR NOT READY (NO DISC OR AUTH REQ)".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H2 DATA: TUR ERROR STATUS".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H2 DATA: INQUIRY ERROR STATUS".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H2 DATA: INQ \"SONY    PS-SYSTEM   308R\" OK!".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H2 DATA: INQ NON-SONY DEVICE STRING".ljust(STR_STRIDE, b'\0'))
        assert len(labels_c) == 7
    elif variant == 'H3':
        labels_c.append(b"P2-H3 DATA: READ SECTOR 16 TIMEOUT".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H3 DATA: READ SECTOR 16 SUBMIT ERROR".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H3 DATA: READ STATUS=NOT READY (NO DISC)".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H3 DATA: READ STATUS=AUTH REQ (EXPECTED PS2 DISC)".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H3 DATA: READ OTHER ERROR STATUS".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H3 DATA: PVD MATCH (01 43 44 30 30 31 01 00 ISO9660 OK!)".ljust(STR_STRIDE, b'\0'))
        labels_c.append(b"P2-H3 DATA: READ SUCCESSFUL (NON-PVD HEADER)".ljust(STR_STRIDE, b'\0'))
        assert len(labels_c) == 7
    blob_c = b''.join(labels_c)

    # Page D: scan summary (4505 strings, identical to P1g)
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

    labels_d = []
    for r in range(5):
        r_pre = rom_prefixes[r]
        for h in range(901):
            h_suf = hdd_suffixes[h]
            s = f"{r_pre} {h_suf}"
            assert len(s) < STR_STRIDE, f"Page D string too long: {s}"
            labels_d.append(s.encode('ascii').ljust(STR_STRIDE, b'\0'))
    assert len(labels_d) == 4505
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

def build_variant(variant_name, variant_code):
    print(f"\n==================================================")
    print(f"Building P2 Variant {variant_name} (code={variant_code})...")
    print(f"==================================================")

    original = BASE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SHA, "stock.elf SHA256 mismatch"
    orig_self = ORIGINAL_SELF.read_bytes()
    assert hashlib.sha256(orig_self).hexdigest() == SELF_SHA, "stock SELF SHA256 mismatch"

    # Mailbox at 0x930F20 must be all-zero in stock (192 bytes)
    assert not any(original[vaoff(original, 0x930f20) : vaoff(original, 0x930f20) + 192]), "mailbox not zero"

    # Build immutable labels
    symbols, label_data = build_labels(variant_name)
    end = 0x74e930 + len(label_data)
    assert end < 0x821000, f"extended RO segment exceeds 0x821000: {hex(end)}"
    print(f"Generated immutable labels for {variant_name}: {len(label_data)} bytes (ends at {hex(end)})")

    # Linker script: payload starts at 0x4A00
    linker = '''OUTPUT_FORMAT(elf64-powerpc)
ENTRY(s4_menu)
SECTIONS {
  . = 0x4A00;
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
    linker += 'repo_read = 0x48c0;\n'
    linker += 'native_clock = 0x4900;\n'
    linker += 'alloc_buffer = 0x4910;\n'
    linker += 'native_alloc = 0x4990;\n'
    linker += 'lv1_hcall = 0x4800;\n'
    ld_path = H / 'build' / f'link_p2b_{variant_name}.ld'
    ld_path.write_text(linker)

    # Compile C payload
    flags = [
        '--target=powerpc64-unknown-linux-gnu', '-mcpu=970', '-mabi=elfv2',
        '-mno-altivec', '-mno-vsx', '-msoft-float', '-ffreestanding',
        '-fno-builtin', '-fno-stack-protector', '-fno-pic',
        '-fno-asynchronous-unwind-tables', '-fno-unwind-tables',
        '-Oz', '-fno-vectorize', '-fno-slp-vectorize',
        '-Wall', '-Wno-unused-function', '-Wextra', '-Werror',
        f'-DPROBE_VARIANT={variant_code}',
        '-S', '-emit-llvm'
    ]
    def run(args):
        r = subprocess.run([str(x) for x in args], cwd=H, capture_output=True, text=True)
        with (H / 'evidence' / f'build_p2b_{variant_name}.log').open('a') as f:
            f.write(' '.join(str(x) for x in args) + '\n' + r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)

    print(f"Compiling probe.c with Clang for {variant_name}...")
    ll_out = H / 'build' / f'probe_p2b_{variant_name}.ll'
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
    (H / 'build' / f'probe_p2b_{variant_name}.o').write_bytes(obj)
    (H / 'build' / f'probe_p2b_{variant_name}_compiler.s').write_text(tm.emit_assembly(module))

    print(f"Linking payload for {variant_name}...")
    payload_elf = H / 'build' / f'probe_payload_p2b_{variant_name}.elf'
    payload_bin = H / 'build' / f'probe_p2b_{variant_name}.bin'
    run([LLVM / 'ld.lld.exe', '-m', 'elf64ppc', '-T', str(ld_path), '--no-undefined',
         f'--Map=build/probe_p2b_{variant_name}.map', f'build/probe_p2b_{variant_name}.o', '-o', str(payload_elf)])
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
    code = bytearray(0x200 + len(p_bin))
    code[:0x200] = trampolines
    code[0x200:] = p_bin
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
    patch(vaoff(e, 0x4800), bytes(code), f'PPC64 payload in code slot (P2 {variant_name})', bytes(len(code)))

    # Fail-open hook check: 0x270FFC MUST hold 0xe882cea8
    patch(vaoff(e, 0x270FFC), branch(0x270FFC, syms['entry_menu']), 'Hook menu-row selector at 0x270FFC', bytes.fromhex('e882cea8'))

    # Extend PHDR1 RO filesz/memsz
    newsize = end - p[3]
    patch(po + 56 + 32, struct.pack('>QQ', newsize, newsize), 'PHDR1 RO filesz/memsz', struct.pack('>QQ', p[5], p[6]))
    assert sh[33][3] + sh[33][5] == 0x74e930
    patch(newso + 33 * 64 + 32, struct.pack('>Q', end - sh[33][3]), 'Last RO section size', struct.pack('>Q', sh[33][5]))

    # Insert label data
    dataoff = p[2] + p[5]
    patch(dataoff, label_data, f'Immutable diagnostic label tables (P2 {variant_name})', bytes(len(label_data)))

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

    # Write patched ELF to local_only/p2b/
    out_elf = ROOT / 'local_only' / 'p2b' / f'ps2_netemu_p2b_{variant_name}.elf'
    out_elf.write_bytes(e)
    elf_sha = hashlib.sha256(e).hexdigest()
    print(f"Patched ELF written: {out_elf} ({len(e)} bytes, sha256={elf_sha})")

    # Repack SELF
    out_self = ROOT / 'local_only' / 'p2b' / f'ps2_netemu_p2b_{variant_name}.self'
    print(f"Repacking SELF to {out_self}...")
    pack = runpy.run_path(str(H / 'resign_self_installed.py'))
    pack['main'](out_elf, out_self)
    self_sha = hashlib.sha256(out_self.read_bytes()).hexdigest()
    print(f"Repacked SELF: {out_self} ({out_self.stat().st_size} bytes, sha256={self_sha})")

    # Round trip verification: decrypt with selfdec.py
    print(f"Verifying SELF round-trip with selfdec.py for {variant_name}...")
    roundtrip_elf = ROOT / 'local_only' / 'p2b' / f'roundtrip_{variant_name}.elf'
    dec = runpy.run_path(str(H / 'selfdec.py'))
    key_vault = Path(r'C:\Users\remus\ps3buzz-console\raw_capture_debug11\dependencies\dl\key_vault.cpp')
    dec['main'](str(key_vault), str(out_self), str(roundtrip_elf))

    rt_data = roundtrip_elf.read_bytes()
    assert len(rt_data) == len(e), f"Roundtrip ELF length mismatch: {len(rt_data)} vs {len(e)}"
    assert hashlib.sha256(rt_data).hexdigest() == elf_sha, "Roundtrip ELF SHA256 mismatch!"
    print(f"SELF round-trip verified: decrypted ELF matches patched ELF byte for byte!")

    # Patch summary table
    table = dict(
        variant=variant_name,
        elf_sha256=elf_sha,
        self_sha256=self_sha,
        code_size=len(code),
        labels_size=len(label_data),
        labels_end=hex(end),
        symbols=syms,
        patches=patches
    )
    (H / 'evidence' / f'p2b_{variant_name}_patch_table.json').write_text(json.dumps(table, indent=2))
    return table

def main():
    print("Building all four P2 variants (H0..H3)...")
    summary = {}
    for name, code in [('H0', 0), ('H1', 1), ('H2', 2), ('H3', 3)]:
        summary[name] = build_variant(name, code)

    print("\n==================================================")
    print("ALL FOUR P2 VARIANTS BUILT AND VERIFIED BYTE-FOR-BYTE!")
    print("==================================================")
    for name, info in summary.items():
        print(f"  {name}: ELF SHA256={info['elf_sha256'][:16]}... SELF SHA256={info['self_sha256'][:16]}... Code={info['code_size']}B Labels={info['labels_size']}B")

if __name__ == '__main__':
    main()
