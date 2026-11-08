#!/usr/bin/env python3
"""
tools/patch_lv1_ss1.py - Safe in-memory patch for ss_server1 optical profile check.

Target:
  Physical Address: 0x00714710 (LV1 Hypervisor RAM)
  Module: ss_server1 (Firmware 4.93)
  Virtual Address: 0x80020710

Signature at 0x00714700 (16 bytes):
  81 21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01

Stock 8-byte word at 0x00714710:
  40 9D 00 1C 7F C3 F3 78  (ble cr7, 0x8002072c; mr r3, r30)

Patched 8-byte word at 0x00714710:
  48 00 00 1C 7F C3 F3 78  (b 0x8002072c; mr r3, r30)
"""

import sys
import re
import argparse
import urllib.request
import urllib.error

HOST = "192.168.0.169"

EXPECTED_PATTERN = "81 21 00 70 3d 29 ff ff 39 29 00 a0 2b 89 00 01"
STOCK_BYTES = "40 9d 00 1c 7f c3 f3 78"
PATCH_BYTES = "48 00 00 1c 7f c3 f3 78"

STOCK_HEX_POKE = "409d001c7fc3f378"
PATCH_HEX_POKE = "4800001c7fc3f378"

def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "patch_lv1/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def peek_range(addr, timeout=10):
    url = f"http://{HOST}/peek.lv1?{addr:x}"
    return http_get(url, timeout=timeout)

def extract_bytes(html, addr, num_bytes=16):
    # Match lines like "00714700 : 81 21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01"
    # or "00714700  81 21 00 70 ..."
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

def check_target(verbose=True):
    if verbose:
        print(f"[*] Reading LV1 physical memory at 0x00714700 from {HOST}...")
    try:
        html = peek_range(0x714700)
    except Exception as e:
        print(f"[-] HTTP Error reading from console: {e}")
        return "ERROR", None

    pat = extract_bytes(html, 0x714700, 16)
    w8 = extract_bytes(html, 0x714710, 8)

    if verbose:
        print(f"    0x00714700 (16-byte pattern): {pat}")
        print(f"    0x00714710 (8-byte word)    : {w8}")

    if pat != EXPECTED_PATTERN:
        print("[-] SAFETY CHECK FAILED: Pattern at 0x00714700 does NOT match expected ss_server1 signature!")
        print(f"    Expected: {EXPECTED_PATTERN}")
        print(f"    Got     : {pat}")
        return "MISMATCH", w8

    if w8 == STOCK_BYTES:
        state = "STOCK"
    elif w8 == PATCH_BYTES:
        state = "PATCHED"
    else:
        state = "UNKNOWN"

    if verbose:
        print(f"[*] Target State: {state}")
    return state, w8

def apply_patch():
    state, w8 = check_target(verbose=True)
    if state == "PATCHED":
        print("[!] Console is ALREADY PATCHED. Nothing to do.")
        return True
    if state != "STOCK":
        print(f"[-] ABORTING: Cannot apply patch when target state is {state} (got {w8})")
        return False

    print("\n[*] Applying in-memory patch to 0x00714710...")
    print(f"    Writing: {PATCH_HEX_POKE} (b 0x8002072c; mr r3, r30)")
    poke_url = f"http://{HOST}/poke.lv1?714710={PATCH_HEX_POKE}"
    try:
        http_get(poke_url, timeout=10)
    except Exception as e:
        print(f"[-] Poke request failed: {e}")
        return False

    print("[*] Verifying write...")
    new_state, new_w8 = check_target(verbose=True)
    if new_state == "PATCHED":
        print("[+] SUCCESS: Patch successfully applied and verified in LV1 RAM!")
        print("    Profile check is now bypassed (unconditional branch to session key calculation).")
        return True
    else:
        print(f"[-] VERIFICATION FAILED: Expected state PATCHED, got {new_state} ({new_w8})")
        return False

def restore_stock():
    state, w8 = check_target(verbose=True)
    if state == "STOCK":
        print("[!] Console is ALREADY in STOCK state. Nothing to do.")
        return True
    if state != "PATCHED":
        print(f"[-] WARNING: Target state is {state} (got {w8}), not PATCHED.")

    print("\n[*] Restoring stock instruction to 0x00714710...")
    print(f"    Writing: {STOCK_HEX_POKE} (ble cr7, 0x8002072c; mr r3, r30)")
    poke_url = f"http://{HOST}/poke.lv1?714710={STOCK_HEX_POKE}"
    try:
        http_get(poke_url, timeout=10)
    except Exception as e:
        print(f"[-] Poke request failed: {e}")
        return False

    print("[*] Verifying write...")
    new_state, new_w8 = check_target(verbose=True)
    if new_state == "STOCK":
        print("[+] SUCCESS: Stock state successfully restored and verified in LV1 RAM!")
        return True
    else:
        print(f"[-] VERIFICATION FAILED: Expected state STOCK, got {new_state} ({new_w8})")
        return False

def main():
    p = argparse.ArgumentParser(description="Safe in-memory patch for ss_server1 optical profile check.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="Check current state of target memory (read-only)")
    g.add_argument("--apply", action="store_true", help="Apply patch (409D001C -> 4800001C)")
    g.add_argument("--restore", action="store_true", help="Restore stock instruction (4800001C -> 409D001C)")

    args = p.parse_args()
    if args.check:
        state, _ = check_target(verbose=True)
        sys.exit(0 if state in ("STOCK", "PATCHED") else 1)
    elif args.apply:
        ok = apply_patch()
        sys.exit(0 if ok else 1)
    elif args.restore:
        ok = restore_stock()
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
