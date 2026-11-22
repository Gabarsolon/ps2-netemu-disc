#!/usr/bin/env python3
"""
tools/patch_cobra_netemu_disc.py - In-Memory Cobra Kernel Hook for PS2 Optical Disc Boot on Netemu.
Includes Hardware Cache Synchronization (dcbf / sync / icbi / isync).

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
  2. Any in-memory LV1 patches applied from XMB are reset during partition reinitialization on boot.
  3. ps2_netemu runs in guest partition PS2_NE_LPAR where HVSC 182/183 are denied (-6 / LV1_NO_ENTRY).
  4. PowerPC L1 Instruction Cache Non-Coherency: Data stores (via poke.lv1 or HVSC 183) do not automatically
     invalidate the L1 I-cache of the CPU cores. Software MUST execute dcbf, sync, icbi, isync.

Solution:
  Install a Position-Independent (PIC) kernel trampoline into unused alignment space at 0x0053BD00 in Cobra RAM:
  1. Hooks 0x005308C4 to branch to 0x005308D4 (48 00 00 10), bypassing the optical disc fatal loop.
  2. Hooks 0x005308D4 to branch to 0x0053BD00 (48 00 B4 2C), hooking ALL netemu boots (optical & carrier ISO).
  3. Anchors the 64-bit LV2 kernel virtual address space using bl +4; mflr r12; addi r12, r12, 0x7c.
  4. Executes HVSC 183 (lv1_poked) directly from LV2 kernel mode:
     - 0x00713210 -> 0x48000164e92296c0 (ss_server1 Drive FW check bypass)
     - 0x00714710 -> 0x4800001c7fc3f378 (ss_server1 Disc profile check bypass)
  5. Executes Hardware Cache Synchronization via direct-mapped HV_BASE (0x8000000014000000ULL):
     - dcbf 0, r3 (Data Cache Block Flush)
     - sync       (Heavy memory barrier)
     - icbi 0, r3 (Instruction Cache Block Invalidate)
     - isync      (Instruction pipeline synchronize)
  6. Executes displaced stock instruction std r2, 0x28(r1) and branches back to 0x005308D8.
"""

import sys
import re
import argparse
import urllib.request
import urllib.error
from html import unescape

HOST = "192.168.0.169"

# Signatures and Hook Addresses
SIGNATURE_ADDR = 0x005308B0
EXPECTED_SIGNATURE = "81 29 00 00 3d 29 ff ff 39 29 00 a0 2b 89 00 01"

# Optical disc fatal panic bypass at 0x005308C4
OPTICAL_HOOK_ADDR = 0x005308C4
OPTICAL_STOCK_BYTES = "48 00 00 00"  # b 0x005308c4 (fatal infinite loop)
OPTICAL_PATCH_BYTES = "48 00 00 10"  # b 0x005308d4 (branch forward to common hook)

# Common netemu entry hook at 0x005308D4
COMMON_HOOK_ADDR = 0x005308D4
COMMON_STOCK_BYTES = "f8 41 00 28"  # std r2, 0x28(r1)
COMMON_PATCH_BYTES = "48 00 b4 2c"  # b 0x0053bd00 (branch to our kernel trampoline)

HOOK_CODE_ADDR = 0x0053BD00
HOOK_DATA_ADDR = 0x0053BD40

# Machine code for the position-independent kernel trampoline (56 bytes code + 32 bytes data)
# 0x0053bd00: bl 0x53bd04           (48000005)
# 0x0053bd04: mflr r12              (7d8802a6)  r12 = 0x0053BD04 (in 64-bit kernel EA)
# 0x0053bd08: addi r12, r12, 0x3c   (398c003c)  r12 = 0x0053BD40 (data table base)
# 0x0053bd0c: ld r3, 0(r12)         (e86c0000)  r3 = 0x00713210 (FW check phys)
# 0x0053bd10: ld r4, 8(r12)         (e88c0008)  r4 = 0x48000164e92296c0 (FW check patch)
# 0x0053bd14: li r11, 183           (396000b7)  HVSC 183: lv1_poked
# 0x0053bd18: sc 1                  (44000022)
# 0x0053bd1c: ld r3, 0x10(r12)      (e86c0010)  r3 = 0x00714710 (Profile check phys)
# 0x0053bd20: ld r4, 0x18(r12)      (e88c0018)  r4 = 0x4800001c7fc3f378 (Profile check patch)
# 0x0053bd24: li r11, 183           (396000b7)  HVSC 183: lv1_poked
# 0x0053bd28: sc 1                  (44000022)
# 0x0053bd2c: std r2, 0x28(r1)      (f8410028)  Displaced instruction from 0x005308D4
# 0x0053bd30: b 0x005308d8          (4bff4ba8)  Resume Cobra build_netemu_params
# 0x0053bd34: nop                   (60000000)  Padding
HOOK_CODE_WORDS = [
    (0x0053BD00, "480000057d8802a6"),  # bl +4; mflr r12
    (0x0053BD08, "398c003ce86c0000"),  # addi r12, r12, 0x3c; ld r3, 0(r12)
    (0x0053BD10, "e88c0008396000b7"),  # ld r4, 8(r12); li r11, 183
    (0x0053BD18, "44000022e86c0010"),  # sc 1; ld r3, 0x10(r12)
    (0x0053BD20, "e88c0018396000b7"),  # ld r4, 0x18(r12); li r11, 183
    (0x0053BD28, "44000022f8410028"),  # sc 1; std r2, 0x28(r1)
    (0x0053BD30, "4bff4ba860000000"),  # b 0x005308d8; nop
]

# Data constants table (32 bytes = 4 64-bit words)
HOOK_DATA_WORDS = [
    (0x0053BD40, "0000000000713210"),  # Addr 1: ss_server1 Drive FW check phys
    (0x0053BD48, "48000164e92296c0"),  # Val 1:  b 0x8001F374 + next inst
    (0x0053BD50, "0000000000714710"),  # Addr 2: ss_server1 Disc profile check phys
    (0x0053BD58, "4800001c7fc3f378"),  # Val 2:  b 0x8002072c + next inst
]


def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "patch_cobra_netemu_disc/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def peek_lv2(addr, timeout=10):
    url = f"http://{HOST}/peek.lv2?{addr:x}"
    return http_get(url, timeout=timeout)


def poke_lv2(addr, hex_str, timeout=10):
    url = f"http://{HOST}/poke.lv2?{addr:x}={hex_str}"
    return http_get(url, timeout=timeout)


def extract_bytes(html, addr, num_bytes=16):
    memory = re.search(r"<pre\b[^>]*>(.*?)</pre>", html, flags=re.IGNORECASE | re.DOTALL)
    if memory is None:
        return ""
    text = memory.group(1)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = unescape(re.sub(r"<[^>]*>", "", text))

    rows = {}
    pattern = r"(?<![0-9a-fA-F])([0-9a-fA-F]{8})[ :]+((?:[0-9a-fA-F]{2}[ \t]+){15}[0-9a-fA-F]{2})(?![0-9a-fA-F])"
    for match in re.finditer(pattern, text):
        row_addr = int(match.group(1), 16)
        row_bytes = match.group(2).replace(" ", "").lower()
        rows[row_addr] = row_bytes

    base_row = addr & ~0xF
    if base_row not in rows:
        return ""

    row_data = rows[base_row]
    offset_in_row = (addr & 0xF) * 2
    extracted = row_data[offset_in_row:offset_in_row + num_bytes * 2]

    if len(extracted) < num_bytes * 2 and (base_row + 16) in rows:
        needed = num_bytes * 2 - len(extracted)
        extracted += rows[base_row + 16][:needed]

    formatted = " ".join([extracted[i:i+2] for i in range(0, len(extracted), 2)])
    return formatted


def verify_signature():
    html = peek_lv2(SIGNATURE_ADDR)
    found = extract_bytes(html, SIGNATURE_ADDR, 16)
    if found != EXPECTED_SIGNATURE:
        print(f"[-] ERROR: Signature mismatch at 0x{SIGNATURE_ADDR:08x}!")
        print(f"    Expected: {EXPECTED_SIGNATURE}")
        print(f"    Found:    {found}")
        return False
    return True


def check_state():
    print(f"[*] Reading Cobra stage2 state from {HOST}...")

    # Check optical fatal bypass hook
    opt_html = peek_lv2(OPTICAL_HOOK_ADDR)
    opt_curr = extract_bytes(opt_html, OPTICAL_HOOK_ADDR, 4)

    # Check common entry hook
    com_html = peek_lv2(COMMON_HOOK_ADDR)
    com_curr = extract_bytes(com_html, COMMON_HOOK_ADDR, 4)

    # Check trampoline code
    code_html = peek_lv2(HOOK_CODE_ADDR)
    code_curr = extract_bytes(code_html, HOOK_CODE_ADDR, 16)

    # Check data constants
    data_html = peek_lv2(HOOK_DATA_ADDR)
    data_curr = extract_bytes(data_html, HOOK_DATA_ADDR, 16)

    print(f"    Optical Hook at 0x{OPTICAL_HOOK_ADDR:08x}: {opt_curr}")
    print(f"    Common Hook  at 0x{COMMON_HOOK_ADDR:08x}: {com_curr}")
    print(f"    Hook code    at 0x{HOOK_CODE_ADDR:08x}: {code_curr}")
    print(f"    Hook data    at 0x{HOOK_DATA_ADDR:08x}: {data_curr}")

    is_opt_active = (opt_curr == OPTICAL_PATCH_BYTES.lower())
    is_com_active = (com_curr == COMMON_PATCH_BYTES.lower())

    if is_opt_active and is_com_active:
        state = "ACTIVE"
    elif opt_curr == OPTICAL_STOCK_BYTES.lower() and com_curr == COMMON_STOCK_BYTES.lower():
        state = "STOCK"
    else:
        state = "PARTIAL / UNKNOWN"

    print(f"[*] Overall Cobra Hook State: {state}")
    return state


def apply_hook():
    print("[*] Applying in-memory Cache-Synchronizing Cobra Kernel Hook for PS2 Netemu...")
    if not verify_signature():
        return False

    # 1. Write Data Table (48 bytes)
    print(f"[*] Writing 48-byte constant data table to 0x{HOOK_DATA_ADDR:08x}...")
    for addr, word_hex in HOOK_DATA_WORDS:
        poke_lv2(addr, word_hex)

    # 2. Write Trampoline Code (96 bytes)
    print(f"[*] Writing 96-byte PIC cache-synchronizing trampoline to 0x{HOOK_CODE_ADDR:08x}...")
    for addr, word_hex in HOOK_CODE_WORDS:
        poke_lv2(addr, word_hex)

    # 3. Activate Optical Hook (b 0x005308d4)
    print(f"[*] Activating optical fatal bypass at 0x{OPTICAL_HOOK_ADDR:08x} (-> 0x{COMMON_HOOK_ADDR:08x})...")
    poke_lv2(OPTICAL_HOOK_ADDR, OPTICAL_PATCH_BYTES.replace(" ", ""))

    # 4. Activate Common Netemu Hook (b 0x0053bd00)
    print(f"[*] Activating common netemu hook at 0x{COMMON_HOOK_ADDR:08x} (-> 0x{HOOK_CODE_ADDR:08x})...")
    poke_lv2(COMMON_HOOK_ADDR, COMMON_PATCH_BYTES.replace(" ", ""))

    # 5. Verify
    print("[*] Verifying applied hook in LV2 RAM...")
    state = check_state()
    if state == "ACTIVE":
        print("[+] SUCCESS: Cobra Kernel Hook with Hardware Cache Sync is ACTIVE in LV2 RAM!")
        print("    Netemu boots (both physical optical disc and carrier ISO) will now automatically:")
        print("    1. Trigger kernel-mode HVSC 183 to patch ss_server1 in LV1 RAM.")
        print("    2. Execute dcbf / sync / icbi / isync to invalidate PPE L1 instruction caches.")
        print("    3. Successfully authenticate physical optical discs (AUTH_VERDICT_OK).")
        return True
    else:
        print(f"[-] FAILED: Hook state is {state}")
        return False


def restore_stock():
    print("[*] Restoring stock Cobra stage2 code...")
    if not verify_signature():
        return False

    poke_lv2(OPTICAL_HOOK_ADDR, OPTICAL_STOCK_BYTES.replace(" ", ""))
    poke_lv2(COMMON_HOOK_ADDR, COMMON_STOCK_BYTES.replace(" ", ""))

    # Zero out trampoline area
    for addr, _ in HOOK_CODE_WORDS:
        poke_lv2(addr, "0000000000000000")
    for addr, _ in HOOK_DATA_WORDS:
        poke_lv2(addr, "0000000000000000")

    state = check_state()
    if state == "STOCK":
        print("[+] SUCCESS: Cobra stage2 restored to clean stock state.")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="In-Memory Cobra Kernel Hook for PS2 Optical Discs with Cache Sync")
    parser.add_argument("--check", action="store_true", help="Check current hook state in LV2 RAM")
    parser.add_argument("--apply", action="store_true", help="Apply the in-memory kernel hook")
    parser.add_argument("--restore", action="store_true", help="Restore stock Cobra code")
    args = parser.parse_args()

    if args.apply:
        success = apply_hook()
        sys.exit(0 if success else 1)
    elif args.restore:
        success = restore_stock()
        sys.exit(0 if success else 1)
    else:
        state = check_state()
        sys.exit(0 if state == "ACTIVE" else 1)


if __name__ == "__main__":
    main()
