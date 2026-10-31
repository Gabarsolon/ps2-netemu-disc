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
(ROOT / 'local_only' / 'p1c2').mkdir(parents=True, exist_ok=True)

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

    # 1. repo_read at 0x4800 (target stock 0x111eb8, TOC 0x751280)
    # 2. native_alloc at 0x4840 (target stock 0x0b9848, TOC 0x751280)
    # 3. entry_menu at 0x4880 (target s4_menu, TOC syms['.TOC.'])
    entries = [
        ('repo_read', 0x4800, 0x111eb8, False),
        ('native_alloc', 0x4840, 0x0b9848, False),
        ('entry_menu', 0x4880, syms['s4_menu'], True),
        ('native_clock', 0x48c0, 0x0b9cd0, False)
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
        assert len(b) <= 64, f'{name} trampoline exceeds 64 bytes ({len(b)})'
        code[pc - 0x4800 : pc - 0x4800 + len(b)] = b
        syms[name] = pc
    return bytes(code)

def build_labels():
    symbols = {}
    data = bytearray()
    STRING_WIDTH = 32

    # Standard errors list for field slots 0..6
    err_suffixes = [
        "rc=-6 NO_ENT",
        "rc=-4 DENIED",
        "rc=-3 NO_PRIV",
        "rc=-5 ACC_VIOL",
        "rc=-1 SHORT",
        "rc=-2 NOTSUP",
        "rc=ERR"
    ]

    def make_field_table(page_num, node_tag, field_name, custom_values=None):
        prefix = f"P{page_num:02d} {node_tag} {field_name}"
        labels = []
        # Slots 0..6: errors
        for err in err_suffixes:
            s = f"{prefix}: {err}"
            assert len(s) < STRING_WIDTH, f"Label too long: '{s}'"
            labels.append(s.encode('ascii').ljust(STRING_WIDTH, b'\0'))
        # Slots 7..262: values 0..255
        for val in range(256):
            if custom_values and val in custom_values:
                val_str = custom_values[val]
            else:
                val_str = f"0x{val:02X}"
            s = f"{prefix}: {val_str}"
            assert len(s) < STRING_WIDTH, f"Label too long: '{s}'"
            labels.append(s.encode('ascii').ljust(STRING_WIDTH, b'\0'))
        assert len(labels) == 263
        return b''.join(labels)

    # Page 00: Summary (160 strings)
    # P00 P1C r=%s h=%s id=%s p=%s
    r_strs = ["0", "1", "2", "3", "4+"]
    h_strs = ["0", "1"]
    modes = ["4/2", "b/d", "500", "hex"]
    ports = ["0", "1", "2", "?"]
    labels_00 = []
    for r in range(5):
        for h in range(2):
            for m in range(4):
                for p in range(4):
                    s = f"P00 P1C r={r_strs[r]} h={h_strs[h]} id={modes[m]} p={ports[p]}"
                    assert len(s) < STRING_WIDTH, f"P00 label too long: '{s}'"
                    labels_00.append(s.encode('ascii').ljust(STRING_WIDTH, b'\0'))
    assert len(labels_00) == 160
    symbols['labels_page_00'] = 0x74e930 + len(data)
    data.extend(b''.join(labels_00))

    # Page 01: Optical type
    opt_type_custom = {0: "0 (DISK)", 5: "5 (ROM)", 14: "14 (FLASH)"}
    symbols['labels_page_01'] = 0x74e930 + len(data)
    data.extend(make_field_table(1, "OPT", "type", opt_type_custom))

    # Page 02: HDD type
    hdd_type_custom = {0: "0 (DISK)", 5: "5 (ROM)", 14: "14 (FLASH)"}
    symbols['labels_page_02'] = 0x74e930 + len(data)
    data.extend(make_field_table(2, "HDD", "type", hdd_type_custom))

    # Page 03: Optical id
    opt_id_custom = {2: "2 (ROM DEV)"}
    symbols['labels_page_03'] = 0x74e930 + len(data)
    data.extend(make_field_table(3, "OPT", "id", opt_id_custom))

    # Page 04: HDD id
    hdd_id_custom = {0: "0", 3: "3"}
    symbols['labels_page_04'] = 0x74e930 + len(data)
    data.extend(make_field_table(4, "HDD", "id", hdd_id_custom))

    # Page 05: Optical port
    symbols['labels_page_05'] = 0x74e930 + len(data)
    data.extend(make_field_table(5, "OPT", "port", {0: "0 (PORT0)"}))

    # Page 06: HDD port
    symbols['labels_page_06'] = 0x74e930 + len(data)
    data.extend(make_field_table(6, "HDD", "port", {2: "2 (PORT2)"}))

    # Page 07: Optical blk_size (268 strings)
    # Slots 0..4: errors; 5..11: standard sizes; 12..267: hi-byte
    def make_blk_table(page_num, node_tag):
        labels = []
        prefix = f"P{page_num:02d} {node_tag} blk_sz"
        errs = ["rc=-6 NO_ENT", "rc=-4 DENIED", "rc=-3 NO_PRIV", "rc=-5 ACC_VIOL", "rc=ERR"]
        for e in errs:
            s = f"{prefix}: {e}"
            assert len(s) < STRING_WIDTH
            labels.append(s.encode('ascii').ljust(STRING_WIDTH, b'\0'))
        std_sizes = ["0", "512 (0x200)", "1024", "2048 (0x800)", "4096", "2352 (CD)", "2064 (XA)"]
        for sz in std_sizes:
            s = f"{prefix}: {sz}"
            assert len(s) < STRING_WIDTH
            labels.append(s.encode('ascii').ljust(STRING_WIDTH, b'\0'))
        for hi in range(256):
            s = f"{prefix}: 0x{hi:02X}__"
            assert len(s) < STRING_WIDTH
            labels.append(s.encode('ascii').ljust(STRING_WIDTH, b'\0'))
        assert len(labels) == 268
        return b''.join(labels)

    symbols['labels_page_07'] = 0x74e930 + len(data)
    data.extend(make_blk_table(7, "OPT"))

    # Page 08: HDD blk_size
    symbols['labels_page_08'] = 0x74e930 + len(data)
    data.extend(make_blk_table(8, "HDD"))

    # Page 09: Optical n_blocks
    symbols['labels_page_09'] = 0x74e930 + len(data)
    data.extend(make_field_table(9, "OPT", "n_blks", {0: "0 (NO DISC)"}))

    # Page 10: HDD n_blocks
    symbols['labels_page_10'] = 0x74e930 + len(data)
    data.extend(make_field_table(10, "HDD", "n_blks", {0: "0"}))

    # Page 11: Optical n_regs
    symbols['labels_page_11'] = 0x74e930 + len(data)
    data.extend(make_field_table(11, "OPT", "n_regs", {0: "0 (NO REGS)"}))

    # Page 12: HDD n_regs
    symbols['labels_page_12'] = 0x74e930 + len(data)
    data.extend(make_field_table(12, "HDD", "n_regs", {0: "0"}))

    # Page 13: Optical meddling
    symbols['labels_page_13'] = 0x74e930 + len(data)
    data.extend(make_field_table(13, "OPT", "meddl", {0: "0 (OFF)", 1: "1 (ON)"}))

    # Page 14: HDD meddling
    symbols['labels_page_14'] = 0x74e930 + len(data)
    data.extend(make_field_table(14, "HDD", "meddl", {0: "0 (OFF)", 1: "1 (ON)"}))

    # Page 15: Optical PCI
    symbols['labels_page_15'] = 0x74e930 + len(data)
    data.extend(make_field_table(15, "OPT", "pci_b"))

    # Page 16: HDD PCI
    symbols['labels_page_16'] = 0x74e930 + len(data)
    data.extend(make_field_table(16, "HDD", "pci_b"))

    # Page 17: Optical intr/0
    symbols['labels_page_17'] = 0x74e930 + len(data)
    data.extend(make_field_table(17, "OPT", "intr0"))

    # Page 18: HDD intr/0
    symbols['labels_page_18'] = 0x74e930 + len(data)
    data.extend(make_field_table(18, "HDD", "intr0", {18: "18 (0x12 HDD)"}))

    # Page 19: Optical reg/0 type
    symbols['labels_page_19'] = 0x74e930 + len(data)
    data.extend(make_field_table(19, "OPT", "reg0_t"))

    # Page 20: HDD reg/0 type
    symbols['labels_page_20'] = 0x74e930 + len(data)
    data.extend(make_field_table(20, "HDD", "reg0_t"))

    # Page 21: Optical intr/1
    symbols['labels_page_21'] = 0x74e930 + len(data)
    data.extend(make_field_table(21, "OPT", "intr1"))

    # Page 22: HDD intr/1
    symbols['labels_page_22'] = 0x74e930 + len(data)
    data.extend(make_field_table(22, "HDD", "intr1"))

    # Page 23: Bus 4 keys (type, id, num_dev)
    symbols['labels_page_23'] = 0x74e930 + len(data)
    data.extend(make_field_table(23, "BUS4", "ndev", {1: "1 dev", 2: "2 devs", 3: "3 devs", 4: "4 devs"}))

    # Pad data to 16 bytes
    data.extend(bytes((-len(data)) % 16))
    return symbols, bytes(data)

def build():
    print("Checking input hashes...")
    original = BASE.read_bytes()
    assert hashlib.sha256(original).hexdigest() == SHA, "stock.elf SHA256 mismatch"
    orig_self = ORIGINAL_SELF.read_bytes()
    assert hashlib.sha256(orig_self).hexdigest() == SELF_SHA, "stock SELF SHA256 mismatch"

    # Mailbox at 0x930F20 must be all-zero in stock
    assert not any(original[vaoff(original, 0x930f20) : vaoff(original, 0x930f20) + 96]), "mailbox not zero"

    # Build immutable labels
    symbols, label_data = build_labels()
    end = 0x74e930 + len(label_data)
    assert end < 0x800000, f"extended RO segment exceeds 0x800000: {hex(end)}"
    print(f"Generated immutable labels: {len(label_data)} bytes (ends at {hex(end)})")

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
    linker += 'repo_read = 0x4800;\n'
    linker += 'native_alloc = 0x4840;\n'
    linker += 'native_clock = 0x48c0;\n'
    (H / 'build' / 'link.ld').write_text(linker)

    # Compile C payload
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
        with (H / 'evidence' / 'build.log').open('a') as f:
            f.write(' '.join(str(x) for x in args) + '\n' + r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)

    print("Compiling probe.c with Clang...")
    run([LLVM / 'clang.exe', *flags, 'src/probe.c', '-o', 'build/probe.ll'])
    llpath = H / 'build' / 'probe.ll'
    llpath.write_text(llpath.read_text().replace(', target_mem: none', ''))

    # Run IR provenance audit
    print("Running IR pointer provenance audit...")
    import runpy
    ir_auditor = runpy.run_path(str(H / 'audit_ir.py'))
    ir_auditor['audit'](llpath)

    import llvmlite.binding as llvm
    llvm.initialize_all_targets()
    llvm.initialize_all_asmprinters()
    module = llvm.parse_assembly(llpath.read_text())
    module.verify()
    tm = llvm.Target.from_triple(module.triple).create_target_machine(
        cpu='970', features='-altivec,-vsx', reloc='static', codemodel='small', abiname='elfv2'
    )
    obj = bytearray(tm.emit_object(module))
    assert struct.unpack_from('>I', obj, 48)[0] == 2, "ELFv2 ABI expected"
    (H / 'build' / 'probe.o').write_bytes(obj)
    (H / 'build' / 'probe_compiler.s').write_text(tm.emit_assembly(module))

    print("Linking payload...")
    run([LLVM / 'ld.lld.exe', '-m', 'elf64ppc', '-T', 'build/link.ld', '--no-undefined', '--Map=build/probe.map', 'build/probe.o', '-o', 'build/probe_payload.elf'])
    run([LLVM / 'llvm-objcopy.exe', '-O', 'binary', 'build/probe_payload.elf', 'build/probe.bin'])

    syms = symtab(H / 'build' / 'probe_payload.elf')
    from elftools.elf.elffile import ELFFile
    with open(H / 'build' / 'probe_payload.elf', 'rb') as f:
        pe = ELFFile(f)
        opd = pe.get_section_by_name('.opd')
        ob = opd.data() if opd else b''
        oa = opd['sh_addr'] if opd else 0
        for name, address in list(syms.items()):
            if oa <= address < oa + len(ob):
                syms[name + '_descriptor'] = address
                syms[name] = struct.unpack_from('>Q', ob, address - oa)[0]

    trampolines = make_entries(syms)
    payload_bin = (H / 'build' / 'probe.bin').read_bytes()
    # Code slot reservation: 0x4800..0x7FF0 = 14,320 bytes
    code = bytearray(0x100 + len(payload_bin))
    code[:0x100] = trampolines
    code[0x100:] = payload_bin
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
    patch(vaoff(e, 0x4800), bytes(code), 'PPC64 payload in code slot', bytes(len(code)))

    # Fail-open hook check: 0x270FFC MUST hold 0xe882cea8
    patch(vaoff(e, 0x270FFC), branch(0x270FFC, syms['entry_menu']), 'Hook menu-row selector at 0x270FFC', bytes.fromhex('e882cea8'))

    # Extend PHDR1 RO filesz/memsz
    newsize = end - p[3]
    patch(po + 56 + 32, struct.pack('>QQ', newsize, newsize), 'PHDR1 RO filesz/memsz', struct.pack('>QQ', p[5], p[6]))
    assert sh[33][3] + sh[33][5] == 0x74e930
    patch(newso + 33 * 64 + 32, struct.pack('>Q', end - sh[33][3]), 'Last RO section size', struct.pack('>Q', sh[33][5]))

    # Insert label data
    dataoff = p[2] + p[5]
    patch(dataoff, label_data, 'Immutable diagnostic label tables', bytes(len(label_data)))

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

    # Write patched ELF to local_only/p1c2/
    out_elf = ROOT / 'local_only' / 'p1c2' / 'ps2_netemu_p1c2.elf'
    out_elf.write_bytes(e)
    elf_sha = hashlib.sha256(e).hexdigest()
    print(f"Patched ELF written: {out_elf} ({len(e)} bytes, sha256={elf_sha})")

    # Repack SELF
    out_self = ROOT / 'local_only' / 'p1c2' / 'ps2_netemu_p1c2.self'
    print(f"Repacking SELF to {out_self}...")
    pack = runpy.run_path(str(H / 'resign_self_installed.py'))
    pack['main'](out_elf, out_self)
    self_sha = hashlib.sha256(out_self.read_bytes()).hexdigest()
    print(f"Repacked SELF: {out_self} ({out_self.stat().st_size} bytes, sha256={self_sha})")

    # Round trip verification: decrypt with selfdec.py
    print("Verifying SELF round-trip with selfdec.py...")
    roundtrip_elf = ROOT / 'local_only' / 'p1c2' / 'roundtrip.elf'
    dec = runpy.run_path(str(H / 'selfdec.py'))
    key_vault = Path(r'C:\Users\remus\ps3buzz-console\raw_capture_debug11\dependencies\dl\key_vault.cpp')
    dec['main'](str(key_vault), str(out_self), str(roundtrip_elf))

    rt_data = roundtrip_elf.read_bytes()
    assert len(rt_data) == len(e), f"Roundtrip ELF length mismatch: {len(rt_data)} vs {len(e)}"
    assert hashlib.sha256(rt_data).hexdigest() == elf_sha, "Roundtrip ELF SHA256 mismatch!"
    print("SELF round-trip verified: decrypted ELF matches patched ELF byte for byte!")

    # Patch summary
    table = dict(
        variant='P1C2',
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
    (H / 'evidence' / 'p1c2_patch_table.json').write_text(json.dumps(table, indent=2))
    print(f"Build complete! Table saved to evidence/p1c2_patch_table.json")

if __name__ == '__main__':
    build()
