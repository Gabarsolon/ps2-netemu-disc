#!/usr/bin/env python3
"""
tools/p14_analyze_dump.py - Offline analyzer for LV1 memory increment 0x700000..0x800000
"""

import sys
import struct
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUMP_PATH = ROOT / "local_only" / "lv1_mem_700000_800000.bin"
SS1_PATH = ROOT / "local_only" / "analysis" / "p0i" / "modules" / "ss_server1.elf"

if not DUMP_PATH.exists():
    print(f"[ERROR] Dump file {DUMP_PATH} does not exist yet.")
    sys.exit(1)

dump = DUMP_PATH.read_bytes()
ss1 = SS1_PATH.read_bytes()

dump_base = 0x700000
dump_size = len(dump)
print(f"Loaded Dump: {dump_size} bytes (0x{dump_base:06X}..0x{dump_base + dump_size:06X})")
print(f"Loaded 4.93 ss_server1.elf: {len(ss1)} bytes (SHA-256: {hashlib.sha256(ss1).hexdigest()})\n")

def phys_to_off(phys):
    if dump_base <= phys < dump_base + dump_size:
        return phys - dump_base
    return None

def off_to_phys(off):
    return dump_base + off

# 1. Search for profile check pattern
pat = bytes.fromhex("81 21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01")
idx = dump.find(pat)
if idx != -1:
    phys_pat = off_to_phys(idx)
    phys_branch = phys_pat + 0x10
    branch_word = dump[idx + 0x10 : idx + 0x14].hex(' ')
    print(f"[FOUND] Profile Check Pattern at Physical 0x{phys_pat:06X} (dump offset 0x{idx:X})")
    print(f"        Original Pattern: {dump[idx : idx + 16].hex(' ')}")
    print(f"        Branch Word at 0x{phys_branch:06X}: {branch_word}")
    expected_branch = "40 9d 00 1c"
    if branch_word == expected_branch:
        print(f"        --> Exact Match for original instruction: ble cr7, 0x8002072c ({branch_word})")
        print(f"        --> Descriptive Patch: replace with 48 00 00 1c (b 0x8002072c)")
    else:
        print(f"        --> Unexpected branch word (expected {expected_branch})")
else:
    print("[NOT FOUND] Profile check pattern not found in dump!")

# 2. Search for diagnostic strings
print("\n" + "="*60)
print("DIAGNOSTIC STRINGS SEARCH")
print("="*60)
for s in [b"HW: not ps2 disc", b"profile:%08X"]:
    pos = 0
    found = []
    while True:
        i = dump.find(s, pos)
        if i == -1: break
        found.append(off_to_phys(i))
        pos = i + 1
    print(f"String '{s.decode()}': {[hex(x) for x in found]}")

# 3. Triple-region byte-by-byte verification (64 bytes each)
print("\n" + "="*60)
print("TRIPLE-REGION VERIFICATION AGAINST DECRYPTED 4.93 ss_server1.elf")
print("="*60)

verif_regions = [
    ("Region 1 (Mid-text Entry)", 0x00700000, 0x1C000),
    ("Region 2 (Profile Check & Branch)", 0x00714700, 0x30700),
    ("Region 3 (Diagnostic Strings)", 0x00740880, 0x5C880),
]

all_passed = True
for name, phys, file_off in verif_regions:
    d_off = phys_to_off(phys)
    if d_off is None or d_off + 64 > len(dump):
        print(f"{name}: Physical 0x{phys:06X} out of dump range!")
        all_passed = False
        continue
    d_slice = dump[d_off : d_off + 64]
    m_slice = ss1[file_off : file_off + 64]
    match = (d_slice == m_slice)
    msg = "PASS (64/64 identical)" if match else "FAIL"
    print(f"{name} (Phys 0x{phys:06X} vs File 0x{file_off:05X}): {msg}")
    if not match:
        all_passed = False
        diffs = sum(1 for a, b in zip(d_slice, m_slice) if a != b)
        print(f"  Diff count: {diffs}/64")

# 4. Map contiguous 4KB pages of ss_server1 Seg 0
print("\n" + "="*60)
print("MAPPING 4KB PAGES OF ss_server1 IN DUMP")
print("="*60)

seg0_pages_matched = 0
for p_idx in range(len(ss1) // 0x1000):
    f_off = p_idx * 0x1000
    page_data = ss1[f_off : f_off + 0x1000]
    needle = page_data[:64]
    if needle.count(b'\x00') > 50:
        continue
    pos = 0
    while True:
        i = dump.find(needle, pos)
        if i == -1: break
        phys = off_to_phys(i)
        if phys % 0x1000 == 0:
            seg0_pages_matched += 1
            if seg0_pages_matched <= 10 or seg0_pages_matched % 15 == 0:
                print(f"  Page {seg0_pages_matched:2d}: File 0x{f_off:05X} (VA 0x{0x80000000 + f_off - 0x10000:08X}) -> Phys 0x{phys:06X}")
        pos = i + 1

print(f"\nTotal non-empty 4KB pages of ss_server1 verified in dump: {seg0_pages_matched}")
