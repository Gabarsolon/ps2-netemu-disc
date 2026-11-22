#!/usr/bin/env python3
"""
tools/patch_ss_server3.py - Hypervisor ss_server3 PS2 Optical Disc Hardware Auth Patcher

Patches ss_server3 in permanent hypervisor memory (0x100000..0x300000) using Cobra's
authentic Backward-Compatible hardware disc authentication logic:

Site 1 (Drive Auth Command):
  Address: 0x00165B54
  Stock:   38 60 00 02 (li r3, 2)
  Patch:   38 60 00 29 (li r3, 0x29)

Site 2 (Drive Teardown / Unauth):
  Address: 0x00165CD0
  Stock:   38 60 00 1E (li r3, 30)
  Patch:   38 60 00 29 (li r3, 0x29)
"""

import sys
import re
import argparse
import urllib.request
import urllib.error

HOST = "192.168.0.169"

PATCHES = [
    {
        "name": "ss_server3 PS2 LPAR Gate Bypass",
        "addr": 0x00165B44,
        "stock_hex": "409e0070",
        "patch_hex": "60000000",
    },
    {
        "name": "ss_server3 PS2 Hardware Model Gate Bypass",
        "addr": 0x00165B4C,
        "stock_hex": "409e0068",
        "patch_hex": "60000000",
    },
    {
        "name": "ss_server3 PS2 Drive Auth (Site 1)",
        "addr": 0x00165B54,
        "stock_hex": "38600002",
        "patch_hex": "38600029",
    },
    {
        "name": "ss_server3 PS2 Drive Unauth (Site 2)",
        "addr": 0x00165CD0,
        "stock_hex": "3860001e",
        "patch_hex": "38600029",
    }
]

def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "patch_ss_server3/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def peek_word(addr, timeout=10):
    # Peek 16 bytes containing addr
    base = addr & ~0xF
    offset = addr & 0xF
    url = f"http://{HOST}/peek.lv1?{base:x}"
    resp = http_get(url, timeout=timeout)
    base_str = f"{base:08X}"
    m = re.search(rf"{base_str}[ :]+([0-9a-fA-F ]+)", resp)
    if not m:
        raise RuntimeError(f"Could not parse peek output for 0x{base:08x}")
    bytes_hex = m.group(1).split()
    word_bytes = bytes_hex[offset:offset+4]
    return "".join(word_bytes).lower()

def poke_word(addr, hex_str, timeout=10):
    url = f"http://{HOST}/poke.lv1?{addr:x}={hex_str}"
    return http_get(url, timeout=timeout)

def check_patches():
    print(f"[*] Reading ss_server3 patch sites from {HOST}...")
    all_patched = True
    all_stock = True
    for p in PATCHES:
        val = peek_word(p["addr"])
        status = "UNKNOWN"
        if val == p["stock_hex"].lower():
            status = "STOCK"
            all_patched = False
        elif val == p["patch_hex"].lower():
            status = "PATCHED"
            all_stock = False
        else:
            all_patched = False
            all_stock = False
        print(f"    {p['name']} at 0x{p['addr']:08X}: {val} [{status}]")

    if all_patched:
        return "ACTIVE"
    elif all_stock:
        return "STOCK"
    else:
        return "MIXED"

def apply_patches():
    print(f"[*] Applying ss_server3 PS2 auth patches to {HOST}...")
    for p in PATCHES:
        val = peek_word(p["addr"])
        if val == p["patch_hex"].lower():
            print(f"    {p['name']} at 0x{p['addr']:08X} is already PATCHED.")
            continue
        print(f"    Poking 0x{p['addr']:08X} with {p['patch_hex']}...")
        poke_word(p["addr"], p["patch_hex"])
        new_val = peek_word(p["addr"])
        if new_val != p["patch_hex"].lower():
            raise RuntimeError(f"Failed to patch {p['name']}! Expected {p['patch_hex']}, got {new_val}")
        print(f"    [+] {p['name']} verified: {new_val}")
    print("[+] All ss_server3 patches applied successfully.")

def restore_stock():
    print(f"[*] Restoring ss_server3 patch sites to STOCK on {HOST}...")
    for p in PATCHES:
        val = peek_word(p["addr"])
        if val == p["stock_hex"].lower():
            print(f"    {p['name']} at 0x{p['addr']:08X} is already STOCK.")
            continue
        print(f"    Poking 0x{p['addr']:08X} with {p['stock_hex']}...")
        poke_word(p["addr"], p["stock_hex"])
        new_val = peek_word(p["addr"])
        if new_val != p["stock_hex"].lower():
            raise RuntimeError(f"Failed to restore {p['name']}! Expected {p['stock_hex']}, got {new_val}")
        print(f"    [+] {p['name']} verified: {new_val}")
    print("[+] All ss_server3 patches restored to STOCK.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hypervisor ss_server3 PS2 Drive Auth Patcher")
    parser.add_argument("--check", action="store_true", help="Check current patch status")
    parser.add_argument("--apply", action="store_true", help="Apply patches")
    parser.add_argument("--restore", action="store_true", help="Restore stock instructions")
    args = parser.parse_args()

    if args.apply:
        apply_patches()
    elif args.restore:
        restore_stock()
    else:
        state = check_patches()
        print(f"[*] Overall ss_server3 state: {state}")
