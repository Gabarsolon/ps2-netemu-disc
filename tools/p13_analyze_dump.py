#!/usr/bin/env python3
"""
tools/p13_analyze_dump.py - Offline analyzer for LV1 memory dump 0x100000..0x300000
"""

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DUMP_PATH = ROOT / "local_only" / "lv1_mem_100000_300000.bin"
MODULES_DIR = ROOT / "local_only" / "analysis" / "p0i" / "modules"

dump = DUMP_PATH.read_bytes()
dump_base = 0x100000
dump_size = len(dump)
print(f"Loaded dump: {dump_size} bytes (0x{dump_base:08X}..0x{dump_base + dump_size:08X})")

def phys_to_off(phys_addr):
    if dump_base <= phys_addr < dump_base + dump_size:
        return phys_addr - dump_base
    return None

def off_to_phys(off):
    return dump_base + off

# 1. Search for modules by ELF segment slices
print("\n" + "="*60)
print("1. SEARCHING FOR EMBEDDED MODULES IN DUMP")
print("="*60)

modules = ['ss_server3.elf', 'ss_server2.elf', 'ss_server1.elf', 'sysmgr_ss.elf', 'ss_init.elf', 'pme_init.elf', 'updater_frontend.elf']

for mod_name in modules:
    mod_path = MODULES_DIR / mod_name
    if not mod_path.exists():
        continue
    data = mod_path.read_bytes()
    
    # Try text segment slices
    # Let's take multiple 32-byte chunks from various offsets in the module
    print(f"\n--- Searching for {mod_name} (size {len(data)}) ---")
    
    found_bases = []
    # Test slices from 0x10000, 0x11000, 0x12000, 0x20000, 0x30000
    for test_off in range(0x10000, min(len(data), 0x50000), 0x4000):
        slice_32 = data[test_off : test_off + 32]
        # Skip if all zeros
        if slice_32 == b'\x00' * 32:
            continue
        p = 0
        while True:
            idx = dump.find(slice_32, p)
            if idx == -1:
                break
            phys = off_to_phys(idx)
            assumed_base = phys - (test_off - 0x10000) # Seg 0 starts at p_offset 0x10000
            found_bases.append((assumed_base, test_off, phys))
            p = idx + 1
            
    if found_bases:
        # Group by assumed_base
        counts = {}
        for b, toff, ph in found_bases:
            counts[b] = counts.get(b, 0) + 1
        print(f"  Matches found! Candidate bases:")
        for b, cnt in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"    Base PhysAddr 0x{b:08X} (supported by {cnt} slice matches)")
            # Verify module at this base
            seg0_off = 0x10000
            match_bytes = 0
            total_test = 0
            for check_off in range(0x10000, min(len(data), 0x40000), 16):
                dump_idx = phys_to_off(b + (check_off - 0x10000))
                if dump_idx is not None and dump_idx + 16 <= len(dump):
                    total_test += 16
                    if dump[dump_idx : dump_idx + 16] == data[check_off : check_off + 16]:
                        match_bytes += 16
            pct = (match_bytes / total_test * 100) if total_test > 0 else 0
            print(f"      Verification: {match_bytes}/{total_test} bytes identical ({pct:.1f}%)")
    else:
        print(f"  NO slices matched for {mod_name} in 0x100000..0x300000")

# 2. Check Process structs at slot 3 (0x12c010) and slot 10 (0x12c8d0)
print("\n" + "="*60)
print("2. INSPECTING PROCESS STRUCTS IN DUMP")
print("="*60)

for slot_idx, slot_phys in [(3, 0x12c010), (10, 0x12c8d0)]:
    off = phys_to_off(slot_phys)
    print(f"\n--- Process Slot {slot_idx} at 0x{slot_phys:08X} (dump off 0x{off:X}) ---")
    # Read Process header
    pid, = struct.unpack_from('>I', dump, off)
    addr_space, = struct.unpack_from('>Q', dump, off + 8)
    print(f"  PID (off 0x00): {pid}")
    print(f"  AddressSpace* (off 0x08): 0x{addr_space:016X}")
    
    # Check if AddressSpace* is in dump
    as_phys = addr_space
    as_off = phys_to_off(as_phys)
    if as_off is not None:
        print(f"  -> AddressSpace in dump at off 0x{as_off:X}!")
        apd_ptr, = struct.unpack_from('>Q', dump, as_off + 0x18)
        print(f"     APD* (AddressSpace + 0x18): 0x{apd_ptr:016X}")
        apd_off = phys_to_off(apd_ptr)
        if apd_off is not None:
            print(f"     -> APD in dump at off 0x{apd_off:X}!")
            head_page, = struct.unpack_from('>I', dump, apd_off + 0x3C)
            anchor = apd_ptr + 0x28
            print(f"        Page list head (APD + 0x3C): 0x{head_page:08X} (anchor: 0x{anchor:08X})")
            
            # Walk page list
            curr_page = head_page
            visited = set()
            page_idx = 0
            while curr_page != anchor and curr_page != 0 and curr_page not in visited:
                visited.add(curr_page)
                page_off = phys_to_off(curr_page)
                if page_off is None:
                    print(f"        Page {page_idx} at 0x{curr_page:08X} is outside dump range!")
                    break
                raddr, = struct.unpack_from('>Q', dump, page_off)
                vaddr, = struct.unpack_from('>I', dump, page_off + 8)
                next_p, = struct.unpack_from('>I', dump, page_off + 0x14)
                shift = dump[page_off + 0x18]
                sz = 1 << shift if shift else 4096
                print(f"        Page {page_idx:2d}: VAddr=0x{vaddr:08X} -> RAddr=0x{raddr:08X} (size=0x{sz:X}, next=0x{next_p:08X})")
                curr_page = next_p
                page_idx += 1
                if page_idx >= 50:
                    print("        (truncated at 50 pages)")
                    break
        else:
            print(f"     APD at 0x{apd_ptr:016X} is outside dump range!")
    else:
        print(f"  AddressSpace at 0x{addr_space:016X} is outside dump range!")
