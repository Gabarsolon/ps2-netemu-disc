#!/usr/bin/env python3
"""
tools/patch_ss1_duo.py - Hypervisor ss_server1 Drive FW Check & Disc Profile Bypass

Applies the two required in-memory patches to ss_server1 in LV1 RAM:
1. Drive FW Check Bypass at 0x00713210:
   Stock:  41 9E 01 64 (beq cr7, 0x8001f374)
   Patch:  48 00 01 64 (b 0x8001f374)
   Bypasses the "PS-SYSTEM" / "PS-SPECIAL" strncmp check that fails on PS3 Slim.

2. Disc Profile Check Bypass at 0x00714710:
   Stock:  40 9D 00 1C (ble cr7, 0x8002072c)
   Patch:  48 00 00 1C (b 0x8002072c)
   Bypasses the 0xFF60/0xFF61 profile check for optical PS2 DVD/CD.
"""

import sys
import re
import argparse
import urllib.request
import urllib.error

HOST = "192.168.0.169"

PATCHES = [
    {
        "name": "Drive FW Check Bypass",
        "addr": 0x00713210,
        "pattern_addr": 0x00713200,
        "expected_pattern": "7c 65 1b 78 7f a3 eb 78 48 02 15 f9 2f 83 00 00",
        "stock": "41 9e 01 64",
        "stock_hex": "419e0164",
        "patch": "48 00 01 64",
        "patch_hex": "48000164",
    },
    {
        "name": "Disc Profile Check Bypass",
        "addr": 0x00714710,
        "pattern_addr": 0x00714700,
        "expected_pattern": "81 21 00 70 3d 29 ff ff 39 29 00 a0 2b 89 00 01",
        "stock": "40 9d 00 1c",
        "stock_hex": "409d001c",
        "patch": "48 00 00 1c",
        "patch_hex": "4800001c",
    }
]

def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "patch_ss1_duo/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def peek_range(addr, timeout=10):
    url = f"http://{HOST}/peek.lv1?{addr:x}"
    return http_get(url, timeout=timeout)

def poke_word(addr, hex_str, timeout=10):
    url = f"http://{HOST}/poke.lv1?{addr:x}={hex_str}"
    return http_get(url, timeout=timeout)

def extract_bytes(html, addr, num_bytes=16):
    addr_str = f"{addr:08x}"
    pattern = rf"{addr_str}[ :]+([0-9a-fA-F ]+)"
    m = re.search(pattern, html)
    if not m:
        return None
    raw_hex = m.group(1).strip()
    parts = raw_hex.split()
    if len(parts) >= num_bytes:
        return " ".join(parts[:num_bytes]).lower()
    return " ".join(parts).lower()

def check_patches(verbose=True):
    all_patched = True
    all_stock = True
    for p in PATCHES:
        html = peek_range(p["pattern_addr"])
        pat = extract_bytes(html, p["pattern_addr"], 16)
        word = extract_bytes(html, p["addr"], 4)
        
        status = "UNKNOWN"
        if word == p["patch"]:
            status = "PATCHED"
            all_stock = False
        elif word == p["stock"]:
            status = "STOCK"
            all_patched = False
        else:
            status = f"UNEXPECTED ({word})"
            all_patched = False
            all_stock = False

        if verbose:
            print(f"[*] {p['name']} at 0x{p['addr']:08X}: {status} (curr={word}, stock={p['stock']}, patch={p['patch']})")

    return all_patched, all_stock

def apply_patches():
    print("[*] Checking patch state before applying...")
    for p in PATCHES:
        html = peek_range(p["pattern_addr"])
        pat = extract_bytes(html, p["pattern_addr"], 16)
        if pat != p["expected_pattern"]:
            print(f"[-] ERROR: Pattern mismatch at 0x{p['pattern_addr']:08X} for {p['name']}!")
            print(f"    Expected: {p['expected_pattern']}")
            print(f"    Got:      {pat}")
            return False

        word = extract_bytes(html, p["addr"], 4)
        if word == p["patch"]:
            print(f"[+] {p['name']} is already PATCHED.")
            continue
        elif word != p["stock"]:
            print(f"[-] ERROR: Target word at 0x{p['addr']:08X} does not match stock: {word}")
            return False

        print(f"[*] Poking {p['name']} at 0x{p['addr']:08X}: {word} -> {p['patch']} ({p['patch_hex']})...")
        poke_word(p["addr"], p["patch_hex"])

    print("\n[*] Verifying write...")
    all_patched, _ = check_patches(verbose=True)
    if all_patched:
        print("[+] SUCCESS: Both ss_server1 patches are ACTIVE and verified in LV1 RAM!")
        return True
    else:
        print("[-] ERROR: Verification failed!")
        return False

def main():
    ap = argparse.ArgumentParser(description="Hypervisor ss_server1 Duo Patch")
    ap.add_argument("--check", action="store_true", help="Check current patch state")
    ap.add_argument("--apply", action="store_true", help="Apply patches to LV1 RAM")
    args = ap.parse_args()

    if args.apply:
        success = apply_patches()
        sys.exit(0 if success else 1)
    else:
        all_patched, all_stock = check_patches(verbose=True)
        if all_patched:
            print("\n[+] State: ALL PATCHED")
        elif all_stock:
            print("\n[*] State: ALL STOCK")
        else:
            print("\n[?] State: MIXED / UNEXPECTED")

if __name__ == "__main__":
    main()
