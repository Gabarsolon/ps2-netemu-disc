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
(ROOT / 'local_only' / 'p1b_noopen').mkdir(parents=True, exist_ok=True)

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

    # 1. lv1_open_device at 0x4820 (remains linked into code slot, never called when PROBE_DO_OPEN=0)
    asm_open = a['Assembler'](0x4820)
    asm_open.asm('li r11, 0xaa\noris r11, r11, 0x8000\nsc 0\nblr\n')
    b_open, _ = asm_open.finish()
    assert len(b_open) <= 16
    code[0x4820 - 0x4800 : 0x4820 - 0x4800 + len(b_open)] = b_open
    syms['lv1_open_device'] = 0x4820

    # 2. lv1_close_device at 0x4830 (remains linked into code slot, never called when PROBE_DO_OPEN=0)
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

def build_labels():
    # Page A: P1B DONE rom=%s open=%s close=%s (75 strings, padded to 48 bytes)
    # Includes "open=OFF" for ablation build
    r_strs = ["0", "1", "2", "3", "4+"]
    o_strs = ["SKIP", "OK", "DENIED", "ERR", "OFF"]
    c_strs = ["-", "OK", "ERR"]
    labels_a = []
    for r in range(5):
        for o in range(5):
            for c in range(3):
                s = f"P1B DONE rom={r_strs[r]} open={o_strs[o]} close={c_strs[c]}"
                assert len(s) < 48
                labels_a.append(s.encode('ascii').ljust(48, b'\0'))
    blob_a = b''.join(labels_a)

    # Page B: ROM B=%02d D=%02d P=%s ID=%s (7169 strings, padded to 48 bytes)
    labels_b = [b"P1B NO ROM DEV (R=0)\0".ljust(48, b'\0')]
    for mode in range(7):
        for b in range(16):
            for d in range(16):
                for p in range(4):
                    p_str = str(p) if p < 3 else "?"
                    if mode == 0:
                        id_str = f"ID={b:x}/{d:x}"
                    elif mode == 1:
                        id_str = "ID=500/501"
                    elif mode == 2:
                        id_str = "ID=100/200"
                    elif mode == 3:
                        id_str = "ID=4/0"
                    elif mode == 4:
                        id_str = "ID=5/2"
                    elif mode == 5:
                        id_str = "ID=0/0"
                    else:
                        id_str = "ID=HEX"
                    s = f"ROM B={b:02d} D={d:02d} P={p_str} {id_str}"
                    assert len(s) < 48
                    labels_b.append(s.encode('ascii').ljust(48, b'\0'))
    blob_b = b''.join(labels_b)

    # Page C: HDD B=%s D=%s P=%s %s (901 strings, padded to 48 bytes)
    labels_c = [b"HDD: NOT FOUND (PROBE INVALID)\0".ljust(48, b'\0')]
    ph_strs = ["PH=-/-", "PH=EMU", "PH=GX", "PH=BOTH"]
    for b in range(9):
        for d in range(5):
            for p in range(5):
                for ph in range(4):
                    b_str = str(b) if b < 8 else "?"
                    d_str = str(d) if d < 4 else "?"
                    p_str = str(p) if p < 4 else "?"
                    s = f"HDD B={b_str} D={d_str} P={p_str} {ph_strs[ph]}"
                    assert len(s) < 48
                    labels_c.append(s.encode('ascii').ljust(48, b'\0'))
    blob_c = b''.join(labels_c)

    # Page D: OP:%s CL:%s RP:%s (1152 strings, padded to 48 bytes)
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
                assert len(s) < 48
                labels_d.append(s.encode('ascii').ljust(48, b'\0'))
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
    assert end < 0x821000, f"extended RO segment exceeds 0x821000: {hex(end)}"
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
    linker += 'repo_read = 0x4840;\n'
    linker += 'lv1_open_device = 0x4820;\n'
    linker += 'lv1_close_device = 0x4830;\n'
    (H / 'build' / 'link.ld').write_text(linker)

    # Compile C payload
    do_open = int(os.environ.get('PROBE_DO_OPEN', '0'))
    flags = [
        '--target=powerpc64-unknown-linux-gnu', '-mcpu=970', '-mabi=elfv2',
        '-mno-altivec', '-mno-vsx', '-msoft-float', '-ffreestanding',
        '-fno-builtin', '-fno-stack-protector', '-fno-pic',
        '-fno-asynchronous-unwind-tables', '-fno-unwind-tables',
        '-Oz', '-fno-vectorize', '-fno-slp-vectorize',
        '-Wall', '-Wno-unused-function', '-Wextra', '-Werror',
        f'-DPROBE_DO_OPEN={do_open}',
        '-S', '-emit-llvm'
    ]
    def run(args):
        r = subprocess.run([str(x) for x in args], cwd=H, capture_output=True, text=True)
        with (H / 'evidence' / 'build.log').open('a') as f:
            f.write(' '.join(str(x) for x in args) + '\n' + r.stdout + r.stderr)
        if r.returncode:
            raise RuntimeError(r.stdout + r.stderr)

    print(f"Compiling probe.c with Clang (PROBE_DO_OPEN={do_open})...")
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
    # Trampolines sit at 0x4800..0x4900 (256 bytes)
    # Payload binary sits at 0x4900
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

    # Write patched ELF to local_only/p1b_noopen/
    out_elf = ROOT / 'local_only' / 'p1b_noopen' / 'ps2_netemu_p1b_noopen.elf'
    out_elf.write_bytes(e)
    elf_sha = hashlib.sha256(e).hexdigest()
    print(f"Patched ELF written: {out_elf} ({len(e)} bytes, sha256={elf_sha})")

    # Repack SELF
    out_self = ROOT / 'local_only' / 'p1b_noopen' / 'ps2_netemu_p1b_noopen.self'
    print(f"Repacking SELF to {out_self}...")
    pack = runpy.run_path(str(H / 'resign_self_installed.py'))
    pack['main'](out_elf, out_self)
    self_sha = hashlib.sha256(out_self.read_bytes()).hexdigest()
    print(f"Repacked SELF: {out_self} ({out_self.stat().st_size} bytes, sha256={self_sha})")

    # Round trip verification: decrypt with selfdec.py
    print("Verifying SELF round-trip with selfdec.py...")
    roundtrip_elf = ROOT / 'local_only' / 'p1b_noopen' / 'roundtrip.elf'
    dec = runpy.run_path(str(H / 'selfdec.py'))
    key_vault = Path(r'C:\Users\remus\ps3buzz-console\raw_capture_debug11\dependencies\dl\key_vault.cpp')
    dec['main'](str(key_vault), str(out_self), str(roundtrip_elf))

    rt_data = roundtrip_elf.read_bytes()
    assert len(rt_data) == len(e), f"Roundtrip ELF length mismatch: {len(rt_data)} vs {len(e)}"
    assert hashlib.sha256(rt_data).hexdigest() == elf_sha, "Roundtrip ELF SHA256 mismatch!"
    print("SELF round-trip verified: decrypted ELF matches patched ELF byte for byte!")

    # Patch summary
    table = dict(
        variant='P1B_NOOPEN',
        probe_do_open=do_open,
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
    (H / 'evidence' / 'p1b_noopen_patch_table.json').write_text(json.dumps(table, indent=2))
    print(f"Build complete! Table saved to evidence/p1b_noopen_patch_table.json")

if __name__ == '__main__':
    build()
