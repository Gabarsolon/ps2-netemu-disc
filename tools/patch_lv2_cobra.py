#!/usr/bin/env python3
"""
tools/patch_lv2_cobra.py - Safe in-memory patch for Cobra optical disc bypass in LV2 RAM.

Target:
  Firmware: 4.93 Evilnat CFW (Cobra 8.x)
  Module: stage2.cex (loaded in LV2 kernel RAM at base 0x00520000)
  Offset: 0x108C4 (RAM Address: 0x005308C4)
  8-byte word Address: 0x005308C0

Context:
  In Cobra's storage_ext_cobra7.c (shutdown_copy_params_patched):
    if (ps2emu_type == PS2EMU_SW && argp[12] == 0) {
      if (disc_emulation == EMU_OFF) {
        if (effective_disctype == DEVICE_TYPE_PS2_CD || effective_disctype == DEVICE_TYPE_PS2_DVD) {
          fatal("Sorry, no optical disc support in ps2_netemu\\n");
        }
      }
    }
  The fatal() call was compiled as `b 0x108c4` (48 00 00 00, infinite loop to self),
  hard-freezing the PS3 before netemu even loads when a physical PS2 disc is played!

Stock 8-byte word at 0x005308C0:
  41 9D 06 C8 48 00 00 00  (bc bo=12, bi=29, 0x10f88; b 0x108c4 [infinite loop])

Patched 8-byte word at 0x005308C0:
  41 9D 06 C8 48 00 00 10  (bc bo=12, bi=29, 0x10f88; b 0x108d4 [bypass to netemu param builder])
"""

import sys
import re
import argparse
import urllib.request
import urllib.error

HOST = "192.168.0.169"

EXPECTED_PATTERN = "81 29 00 00 3d 29 ff ff 39 29 00 a0 2b 89 00 01"
STOCK_BYTES = "41 9d 06 c8 48 00 00 00"
PATCH_BYTES = "41 9d 06 c8 48 00 00 10"

STOCK_HEX_POKE = "419d06c848000000"
PATCH_HEX_POKE = "419d06c848000010"

def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "patch_lv2_cobra/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def peek_range(addr, timeout=10):
    url = f"http://{HOST}/peek.lv2?{addr:x}"
    return http_get(url, timeout=timeout)

def extract_bytes(html, addr, num_bytes=16):
    addr_str = f"{addr:08x}"
    pattern = rf"{addr_str}[ :]+([0-9a-fA-F ]+)"
    m = re.search(pattern, html, re.IGNORECASE)
    if not m:
        return None
    raw_hex = m.group(1).strip()
    parts = raw_hex.split()
    if len(parts) >= num_bytes:
        return " ".join(parts[:num_bytes]).lower()
    return " ".join(parts).lower()

def check_target(verbose=True):
    if verbose:
        print(f"[*] Reading LV2 memory at 0x005308B0 from {HOST}...")
    try:
        html = peek_range(0x5308b0)
    except Exception as e:
        print(f"[-] HTTP Error reading from console: {e}")
        return "ERROR", None

    pat = extract_bytes(html, 0x5308b0, 16)
    w8 = extract_bytes(html, 0x5308c0, 8)

    if verbose:
        print(f"    0x005308B0 (16-byte pattern): {pat}")
        print(f"    0x005308C0 (8-byte word)    : {w8}")

    if pat != EXPECTED_PATTERN:
        print("[-] SAFETY CHECK FAILED: Pattern at 0x005308B0 does NOT match expected Cobra signature!")
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

    print("\n[*] Applying in-memory patch to 0x005308C0...")
    print(f"    Writing: {PATCH_HEX_POKE} (b 0x005308d4 bypass)")
    poke_url = f"http://{HOST}/poke.lv2?5308c0={PATCH_HEX_POKE}"
    try:
        http_get(poke_url, timeout=10)
    except Exception as e:
        print(f"[-] Poke request failed: {e}")
        return False

    print("[*] Verifying write...")
    new_state, new_w8 = check_target(verbose=True)
    if new_state == "PATCHED":
        print("[+] SUCCESS: Patch successfully applied and verified in LV2 RAM!")
        print("    Cobra physical disc panic is now bypassed (routes directly to netemu parameter builder).")
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

    print("\n[*] Restoring stock instruction to 0x005308C0...")
    print(f"    Writing: {STOCK_HEX_POKE} (b 0x108c4 infinite loop)")
    poke_url = f"http://{HOST}/poke.lv2?5308c0={STOCK_HEX_POKE}"
    try:
        http_get(poke_url, timeout=10)
    except Exception as e:
        print(f"[-] Poke request failed: {e}")
        return False

    print("[*] Verifying write...")
    new_state, new_w8 = check_target(verbose=True)
    if new_state == "STOCK":
        print("[+] SUCCESS: Stock state successfully restored and verified in LV2 RAM!")
        return True
    else:
        print(f"[-] VERIFICATION FAILED: Expected state STOCK, got {new_state} ({new_w8})")
        return False

def main():
    p = argparse.ArgumentParser(description="Safe in-memory patch for Cobra optical disc launch in LV2 RAM.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="Check current state of target memory (read-only)")
    g.add_argument("--apply", action="store_true", help="Apply patch (48000000 -> 48000010)")
    g.add_argument("--restore", action="store_true", help="Restore stock instruction (48000010 -> 48000000)")

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
