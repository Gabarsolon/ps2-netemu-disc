#!/usr/bin/env python3
"""
tools/canary_ss1.py - Set or verify canary values in ss_server1 0x16 return paths.

Locations:
1. 0x00713248: li r29, 0x16 -> 0xAA (Drive FW strncmp fail in _opd_FUN_8001f0e4)
2. 0x00713e48: li r29, 0x16 -> 0xCC (Profile check fail in func_0x8001fa14)
3. 0x00714410: li r31, 0x16 -> 0xDD (Profile check fail in func_0x80020280)
4. 0x00714720: li r31, 0x16 -> 0xBB (Profile check fail in _opd_FUN_80020638)
"""

import sys
import re
import argparse
import urllib.request

HOST = "192.168.0.169"

CANARIES = [
    {
        "name": "FW strncmp in 8001f0e4",
        "addr": 0x00713248,
        "stock": "3ba00016",
        "canary": "3ba000aa",
        "canary_val": 0xAA,
    },
    {
        "name": "Profile in 8001fa14",
        "addr": 0x00713e48,
        "stock": "3ba00016",
        "canary": "3ba000cc",
        "canary_val": 0xCC,
    },
    {
        "name": "Profile in 80020280",
        "addr": 0x00714410,
        "stock": "3be00016",
        "canary": "3be000dd",
        "canary_val": 0xDD,
    },
    {
        "name": "Profile in 80020638",
        "addr": 0x00714720,
        "stock": "3be00016",
        "canary": "3be000bb",
        "canary_val": 0xBB,
    },
]

def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "canary_ss1/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def peek_word(addr):
    # Align to 8 bytes for clean 64-bit peek
    aligned = addr & ~7
    url = f"http://{HOST}/peek.lv1?{aligned:x}"
    resp = http_get(url)
    m = re.search(r'<pre>(.*?)</pre>', resp, re.DOTALL)
    if not m:
        raise RuntimeError(f"Could not parse peek response for {aligned:x}")
    for line in m.group(1).split("<br>"):
        line_clean = line.strip()
        if not line_clean:
            continue
        parts = line_clean.split()
        if len(parts) >= 17:
            try:
                base_addr = int(parts[0], 16)
                if base_addr <= addr < base_addr + 16:
                    offset = addr - base_addr
                    # 4 bytes
                    word_bytes = parts[1 + offset : 1 + offset + 4]
                    return "".join(word_bytes).lower()
            except ValueError:
                continue
    raise RuntimeError(f"Address {addr:x} not found in dump")

def poke_word(addr, hex_str):
    url = f"http://{HOST}/poke.lv1?{addr:x}={hex_str}"
    return http_get(url)

def check():
    print("[*] Checking Canary States in ss_server1:")
    for c in CANARIES:
        curr = peek_word(c["addr"])
        status = "UNKNOWN"
        if curr == c["stock"]:
            status = "STOCK (0x16)"
        elif curr == c["canary"]:
            status = f"CANARY ACTIVE (0x{c['canary_val']:02X})"
        print(f"  [{c['name']}] 0x{c['addr']:08X}: {status} (curr={curr})")

def apply_canaries():
    print("[*] Applying Canaries in ss_server1:")
    for c in CANARIES:
        curr = peek_word(c["addr"])
        if curr != c["canary"]:
            print(f"  Poking {c['name']} at 0x{c['addr']:08X}: {curr} -> {c['canary']}...")
            poke_word(c["addr"], c["canary"])
        else:
            print(f"  Already canaried at 0x{c['addr']:08X}: {curr}")
    print("\n[*] Verifying Canary Writes:")
    all_ok = True
    for c in CANARIES:
        curr = peek_word(c["addr"])
        if curr == c["canary"]:
            print(f"  [+] 0x{c['addr']:08X}: OK -> 0x{c['canary_val']:02X}")
        else:
            print(f"  [-] 0x{c['addr']:08X}: FAILED! curr={curr}, expected={c['canary']}")
            all_ok = False
    return all_ok

def restore_stock():
    print("[*] Restoring Stock in ss_server1:")
    for c in CANARIES:
        curr = peek_word(c["addr"])
        if curr != c["stock"]:
            print(f"  Restoring {c['name']} at 0x{c['addr']:08X}: {curr} -> {c['stock']}...")
            poke_word(c["addr"], c["stock"])
        else:
            print(f"  Already stock at 0x{c['addr']:08X}: {curr}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args()

    if args.apply:
        apply_canaries()
    elif args.restore:
        restore_stock()
    else:
        check()
