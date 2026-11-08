#!/usr/bin/env python3
"""
tools/patch_cobra_netemu_disc.py - In-Memory Cobra Kernel Hook for PS2 Optical Disc Boot on Netemu.

Architecture:
  Platform: PS3 Slim (CECH-2504B, Evilnat 4.93 CEX Cobra 8.5)
  Target Module: Cobra stage2 (loaded at 0x00520000 in LV2 Kernel RAM)
  Function: shutdown_copy_params_patched (called during sys_sm_shutdown 0x8204)

Problem Solved:
  1. Cobra hard-freezes in an infinite loop (fatal()) when launching physical optical PS2 discs on Slim:
       if (disc_emulation == EMU_OFF && (effective_disctype == PS2_CD || PS2_DVD)) {
           fatal("Sorry, no optical disc support in ps2_netemu\\n");
       }
     At 0x005308C4: 48 00 00 00 (b 0x005308C4)
  2. Persistence of XMB-applied LV1 patches into the netemu partition is unproven.
  3. Guest HVSC 182/183 attempts returned -6 / LV1_NO_ENTRY in prior probes.

Solution:
  Install a Position-Independent (PIC) kernel trampoline into unused alignment space at 0x0053BD00 in Cobra RAM:
  1. Hooks 0x005308C4 to branch to 0x0053BD00 (48 00 B4 3C).
  2. Anchors the 64-bit LV2 kernel virtual address space using bl +4; mflr r12 (preventing kernel DSI exceptions).
  3. Executes HVSC 183 (lv1_poked) directly from LV2 kernel mode:
     - 0x00713210 -> 0x48000164e92296c0 (ss_server1 Drive FW check bypass)
     - 0x00714710 -> 0x4800001c7fc3f378 (ss_server1 Disc profile check bypass)
  4. Branches back to 0x005308D4 to complete Cobra's netemu parameter setup (--COBRA--, ps2bootparam.dat).
"""

import sys
import re
import argparse
import urllib.request
import urllib.error
from html import unescape

HOST = "192.168.0.169"

# Signatures and Addresses
SIGNATURE_ADDR = 0x005308B0
EXPECTED_SIGNATURE = "81 29 00 00 3d 29 ff ff 39 29 00 a0 2b 89 00 01"

HOOK_CALL_ADDR = 0x005308C0
STOCK_CALL_BYTES = "41 9d 06 c8 48 00 00 00"  # bgt +6c8; b 0x005308c4 (fatal infinite loop)
PATCH_CALL_BYTES = "41 9d 06 c8 48 00 b4 3c"  # bgt +6c8; b 0x0053bd00 (branch to our kernel hook)

HOOK_CODE_ADDR = 0x0053BD00
HOOK_DATA_ADDR = 0x0053BD80

# Machine code for the position-independent kernel trampoline (56 bytes = 7 64-bit words)
# 0x0053bd00: bl 0x53bd04           (48000005)
# 0x0053bd04: mflr r12              (7d8802a6)  r12 = 0x0053BD04 (in 64-bit kernel EA)
# 0x0053bd08: ld r3, 0x7c(r12)      (e86c007c)  r3 = 0x00713210 (ss_server1 FW check)
# 0x0053bd0c: ld r4, 0x84(r12)      (e88c0084)  r4 = 0x48000164e92296c0
# 0x0053bd10: li r11, 183           (396000b7)  HVSC 183: lv1_poked
# 0x0053bd14: sc 1                  (44000022)
# 0x0053bd18: bl 0x53bd1c           (48000005)
# 0x0053bd1c: mflr r12              (7d8802a6)  r12 = 0x0053BD1C (in 64-bit kernel EA)
# 0x0053bd20: ld r3, 0x74(r12)      (e86c0074)  r3 = 0x00714710 (ss_server1 Profile check)
# 0x0053bd24: ld r4, 0x7c(r12)      (e88c007c)  r4 = 0x4800001c7fc3f378
# 0x0053bd28: li r11, 183           (396000b7)  HVSC 183: lv1_poked
# 0x0053bd2c: sc 1                  (44000022)
# 0x0053bd30: b 0x005308d4          (4bff4ba4)  resume Cobra build_netemu_params
# 0x0053bd34: nop                   (60000000)
HOOK_CODE_WORDS = [
    (0x0053BD00, "480000057d8802a6"),  # bl +4; mflr r12
    (0x0053BD08, "e86c007ce88c0084"),  # ld r3, 0x7c(r12); ld r4, 0x84(r12)
    (0x0053BD10, "396000b744000022"),  # li r11, 183; sc 1
    (0x0053BD18, "480000057d8802a6"),  # bl +4; mflr r12
    (0x0053BD20, "e86c0074e88c007c"),  # ld r3, 0x74(r12); ld r4, 0x7c(r12)
    (0x0053BD28, "396000b744000022"),  # li r11, 183; sc 1
    (0x0053BD30, "4bff4ba460000000"),  # b 0x005308d4; nop
]

# Data constants table (32 bytes = 4 64-bit words)
HOOK_DATA_WORDS = [
    (0x0053BD80, "0000000000713210"),  # Addr 1: ss_server1 Drive FW check
    (0x0053BD88, "48000164e92296c0"),  # Val 1:  b 0x8001f374 + next inst
    (0x0053BD90, "0000000000714710"),  # Addr 2: ss_server1 Disc profile check
    (0x0053BD98, "4800001c7fc3f378"),  # Val 2:  b 0x8002072c + next inst
]


def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "patch_cobra_netemu_disc/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def peek_lv2(addr, timeout=10):
    url = f"http://{HOST}/peek.lv2?{addr:x}"
    return http_get(url, timeout=timeout)


def poke_lv2(addr, hex_str, timeout=10):
    url = f"http://{HOST}/poke.lv2?{addr:x}={hex_str}"
    return http_get(url, timeout=timeout)


def extract_bytes(html, addr, num_bytes=16):
    # webMAN rounds the displayed address down to 16 bytes and may wrap
    # individual bytes in highlight tags. Read by displayed address, not URL.
    memory = re.search(r"<pre\b[^>]*>(.*?)</pre>", html, flags=re.IGNORECASE | re.DOTALL)
    if memory is None:
        return None
    html = memory.group(1)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = unescape(re.sub(r"<[^>]*>", "", html))
    rows = {}
    pattern = r"(?<![0-9a-fA-F])([0-9a-fA-F]{8})[ :]+((?:[0-9a-fA-F]{2}[ \t]+){15}[0-9a-fA-F]{2})(?![0-9a-fA-F])"
    for match in re.finditer(pattern, html):
        base = int(match.group(1), 16)
        if base in rows or base % 16:
            return None
        rows[base] = bytes.fromhex(match.group(2))
    try:
        data = bytes(rows[a & ~15][a & 15] for a in range(addr, addr + num_bytes))
    except KeyError:
        return None
    return data.hex(" ")


def read_snapshot(verbose=False):
    """Read every byte that apply/revert may overwrite, including gaps."""
    sig = extract_bytes(peek_lv2(SIGNATURE_ADDR), SIGNATURE_ADDR, 16)
    call = extract_bytes(peek_lv2(HOOK_CALL_ADDR), HOOK_CALL_ADDR, 8)
    size = HOOK_DATA_ADDR + 32 - HOOK_CODE_ADDR
    slot = extract_bytes(peek_lv2(HOOK_CODE_ADDR), HOOK_CODE_ADDR, size)
    if sig != EXPECTED_SIGNATURE or call is None or slot is None:
        print("[-] Safety check failed: signature mismatch or incomplete memory response.")
        return "ERROR"

    expected = bytearray(size)
    for address, value in HOOK_CODE_WORDS + HOOK_DATA_WORDS:
        expected[address - HOOK_CODE_ADDR:address - HOOK_CODE_ADDR + 8] = bytes.fromhex(value)
    actual = bytes.fromhex(slot)
    if call == PATCH_CALL_BYTES and actual == expected:
        state = "ACTIVE"
    elif call == STOCK_CALL_BYTES and actual == bytes(size):
        state = "STOCK"
    else:
        state = "UNKNOWN"
    if verbose:
        print(f"    Callsite at 0x{HOOK_CALL_ADDR:08x}: {call}")
        print(f"    Full trampoline/data region checked: {size} bytes")
    return state


def check_status(verbose=True):
    if verbose:
        print(f"[*] Reading Cobra stage2 state from {HOST}...")

    state = read_snapshot(verbose)

    if verbose:
        print(f"[*] Overall Cobra Hook State: {state}")
    return state


def apply_patch():
    print("[*] Applying in-memory Position-Independent Cobra Kernel Hook for PS2 Netemu Optical Discs...")
    state = check_status(verbose=False)
    if state == "ACTIVE":
        print("[+] Exact hook is already installed and verified.")
        return True
    if state != "STOCK":
        print("[-] Aborting apply due to safety check failure.")
        return False

    # 1. Write hook data table
    print(f"[*] Writing 32-byte constant data table to 0x{HOOK_DATA_ADDR:08x}...")
    for addr, val in HOOK_DATA_WORDS:
        poke_lv2(addr, val)

    # 2. Write hook code instructions (Position-Independent PIC)
    print(f"[*] Writing 56-byte PIC kernel trampoline to 0x{HOOK_CODE_ADDR:08x}...")
    for addr, val in HOOK_CODE_WORDS:
        poke_lv2(addr, val)

    # A dropped write must never leave a branch into incomplete kernel code.
    for addr, value in HOOK_CODE_WORDS + HOOK_DATA_WORDS:
        actual = extract_bytes(peek_lv2(addr), addr, 8)
        if actual != bytes.fromhex(value).hex(" "):
            print(f"[-] Read-back failed at 0x{addr:08x}; hook branch not activated.")
            return False
    call = extract_bytes(peek_lv2(HOOK_CALL_ADDR), HOOK_CALL_ADDR, 8)
    if call != STOCK_CALL_BYTES:
        print("[-] Callsite changed during preparation; hook branch not activated.")
        return False

    # 3. Hook the callsite at 0x005308C0
    print(f"[*] Activating kernel hook branch at 0x{HOOK_CALL_ADDR:08x} (-> 0x{HOOK_CODE_ADDR:08x})...")
    poke_lv2(HOOK_CALL_ADDR, "419d06c84800b43c")

    # 4. Verify everything
    print("[*] Verifying applied hook in LV2 RAM...")
    new_state = check_status(verbose=True)
    if new_state == "ACTIVE":
        print("[+] SUCCESS: Cobra Kernel Hook is ACTIVE in LV2 RAM!")
        print("    This verifies RAM bytes only. Hypercall execution, authentication,")
        print("    sector reads, and successful netemu boot still require console evidence.")
        return True
    else:
        print(f"[-] Verification failed! Current state: {new_state}")
        return False


def revert_patch():
    print("[*] Reverting Cobra Kernel Hook to STOCK...")
    state = check_status(verbose=False)
    if state == "STOCK":
        return True
    if state != "ACTIVE":
        print("[-] Refusing revert: memory does not match this tool's exact hook.")
        return False
    poke_lv2(HOOK_CALL_ADDR, "419d06c848000000")
    if extract_bytes(peek_lv2(HOOK_CALL_ADDR), HOOK_CALL_ADDR, 8) != STOCK_CALL_BYTES:
        print("[-] Callsite restore failed; trampoline retained.")
        return False
    for addr, _ in HOOK_CODE_WORDS:
        poke_lv2(addr, "0000000000000000")
    for addr, _ in HOOK_DATA_WORDS:
        poke_lv2(addr, "0000000000000000")
    state = check_status(verbose=True)
    print(f"[*] Revert complete. Current state: {state}")
    return state == "STOCK"


def main():
    parser = argparse.ArgumentParser(description="Cobra Netemu Optical Disc Kernel Patcher")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--apply", action="store_true", help="Apply kernel hook in LV2 RAM")
    actions.add_argument("--revert", action="store_true", help="Revert kernel hook to stock")
    actions.add_argument("--check", action="store_true", help="Check current hook status")
    args = parser.parse_args()

    if args.apply:
        return 0 if apply_patch() else 1
    elif args.revert:
        return 0 if revert_patch() else 1
    elif args.check:
        return 0 if check_status(verbose=True) in ("ACTIVE", "STOCK") else 1
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(f"[-] Operation failed: {error}")
        sys.exit(1)
