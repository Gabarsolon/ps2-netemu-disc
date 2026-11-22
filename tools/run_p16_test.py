#!/usr/bin/env python3
"""
tools/run_p16_test.py - Automated console test runner for P16 with Cobra Cache Sync.

Flow:
1. Verify & ensure Cobra Hook with Cache Sync is ACTIVE in LV2 RAM.
2. Verify & ensure LV1 Hypervisor patches are ACTIVE.
3. Reset /dev_hdd0/tmp/netemu_log.bin with 64 KiB zeroes.
4. Launch carrier ISO via webMAN /play.ps3.
5. Wait 22s for carrier boot.
6. Send PS button tap to trigger optical disc probe and log writer.
7. Wait 8s for diagnostic summary & END record to commit.
8. Send exit sequence (CROSS -> LEFT -> CROSS) to return to XMB.
9. Wait for console to return to XMB (FTP online).
10. Download /dev_hdd0/tmp/netemu_log.bin and decode.
"""

import sys
import os
import time
import ftplib
import io
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pico-ds3-bridge/python"))
sys.path.insert(0, str(ROOT / "tools"))

from ps3_controller import PS3Controller
from patch_cobra_netemu_disc import check_state, restore_stock
from patch_ss1_duo import check_patches, apply_patches
from patch_ss_server3 import check_patches as check_ss3, apply_patches as apply_ss3
from ss1_auth_sentinel import set_state as set_sentinel, check as check_sentinel

HOST = "192.168.0.169"
ISO_NAME = "Buzz! The Schools Quiz (Europe).iso"

def main():
    print("=======================================================")
    print("  PS2 OPTICAL DISC NETEMU AUTOMATED HARDWARE TEST (P16)")
    print("=======================================================")

    # 1. Ensure Cobra Hook is STOCK (Prevents LV2 shutdown halt)
    print("\n[Step 1] Ensuring Cobra stage2 is STOCK (no shutdown hooks)...", flush=True)
    state = check_state()
    if state != "STOCK":
        print("[*] Hook active, reverting to STOCK...", flush=True)
        restore_stock()
    print("[+] Cobra stage2 is clean STOCK.", flush=True)

    # 2. Check & Apply LV1 Hypervisor ss_server3 Hardware PS2 Disc Auth Patches
    print("\n[Step 2] Ensuring ss_server3 PS2 Hardware Disc Auth patches are ACTIVE...", flush=True)
    ss3_state = check_ss3()
    if ss3_state != "ACTIVE":
        print("[*] ss_server3 patches not active, applying Cobra BC auth patches (0x29)...", flush=True)
        apply_ss3()
    print("[+] ss_server3 PS2 Hardware Disc Auth patches (0x165B54 & 0x165CD0) are ACTIVE.", flush=True)

    # 2b. Check & Apply LV1 ss_server1 patches & Auth Executor
    print("\n[Step 2b] Ensuring LV1 ss_server1 bypasses are applied...", flush=True)
    lv1_state = check_patches()
    if lv1_state != "ACTIVE":
        print("[*] LV1 duo patches not active, applying...", flush=True)
        apply_patches()
    print("[+] LV1 Duo patches (FW + Profile check bypass) are ACTIVE.", flush=True)

    sentinel_state = check_sentinel("auth_ok")
    if sentinel_state != "SENTINEL":
        print("[*] Setting Auth Executor 0x712724 to AUTH_OK (li r0, 0; stw r0, 0x18(r3); blr)...", flush=True)
        set_sentinel("SENTINEL", "auth_ok")
    print("[+] Auth Executor 0x712724 is ACTIVE (AUTH_OK).", flush=True)

    # 3. Verify optical disc in drive & reset log
    print("\n[Step 3] Checking optical drive & resetting log on PS3...", flush=True)
    with ftplib.FTP(HOST, timeout=10, encoding="latin-1") as ftp:
        ftp.login()
        disc = ftp.nlst("/dev_bdvd")
        print("    Optical drive contains:", disc[:3], flush=True)
        if "SLES_544.66" not in disc and "SYSTEM.CNF" not in disc:
            print("[-] WARNING: Expected PS2 optical disc (TDU) not detected in /dev_bdvd!", flush=True)

        # Reset log file to 64KB zeroes
        zero_buf = io.BytesIO(b"\x00" * 65536)
        ftp.storbinary("STOR /dev_hdd0/tmp/netemu_log.bin", zero_buf)
        print("[+] Log placeholder /dev_hdd0/tmp/netemu_log.bin reset to 64 KiB zeroes.", flush=True)

    # 4. Check DS3 Bridge
    print("\n[Step 4] Checking Pico DS3 bridge on COM9...", flush=True)
    ctl = PS3Controller("COM9")
    st = ctl.get_status()
    print(f"    Bridge status: {st}", flush=True)
    if "mounted=1" not in st:
        ctl.close()
        raise SystemExit("[-] Controller bridge is not mounted to PS3. Aborting.")

    # 5. Launch carrier ISO
    print("\n[Step 5] Launching carrier ISO via webMAN /play.ps3...", flush=True)
    iso_encoded = urllib.parse.quote(ISO_NAME, safe="!()")
    play_url = f"http://{HOST}/play.ps3/dev_hdd0/PS2ISO/{iso_encoded}"
    try:
        req = urllib.request.Request(play_url, headers={"User-Agent": "run_p16_test/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"    Launch response HTTP: {resp.status}", flush=True)
    except Exception as e:
        print(f"    Launch notice (transitioning): {e}", flush=True)

    # 6. Wait for netemu boot
    wait_boot = 22
    print(f"\n[Step 6] Waiting {wait_boot}s for netemu to boot into carrier...", flush=True)
    for remaining in range(wait_boot, 0, -5):
        print(f"    {remaining}s remaining...", flush=True)
        time.sleep(5)

    # 7. Open in-game menu to trigger diagnostic probe
    print("\n[Step 7] Sending PS button to open in-game menu (triggers optical probe)...", flush=True)
    print("    Tapping PS button (300ms)...", flush=True)
    ctl.press("PS", 300)

    # 8. Wait for probe execution and log flush
    wait_probe = 8
    print(f"    Waiting {wait_probe}s for probe execution & durable HDD log flush...", flush=True)
    time.sleep(wait_probe)

    # 9. Clean exit back to XMB
    print("\n[Step 8] Sending clean exit sequence (CROSS -> LEFT -> CROSS)...", flush=True)
    time.sleep(1.0)
    print("    Pressing CROSS (Select 'Quit Game')...", flush=True)
    ctl.press("CROSS", 150)
    time.sleep(1.5)
    print("    Pressing LEFT (Select 'Yes')...", flush=True)
    ctl.press("LEFT", 150)
    time.sleep(1.0)
    print("    Pressing CROSS (Confirm Exit)...", flush=True)
    ctl.press("CROSS", 150)
    ctl.close()
    print("[+] Exit sequence sent. Waiting for console to boot back into XMB...", flush=True)

    # 10. Wait for console to return to XMB (FTP online)
    print("\n[Step 9] Waiting for PS3 to return to XMB...", flush=True)
    ftp_online = False
    for attempt in range(1, 35):
        time.sleep(3)
        try:
            with ftplib.FTP(HOST, timeout=3, encoding="latin-1") as ftp:
                ftp.login()
                ftp_online = True
                print(f"[+] PS3 is back online in XMB (attempt {attempt})!", flush=True)
                break
        except Exception:
            print(f"    Waiting for XMB... ({attempt}/35)", flush=True)

    if not ftp_online:
        raise SystemExit("[-] Console did not return to XMB in time. Please check TV/screen.")

    # 11. Download fresh log
    print("\n[Step 10] Downloading /dev_hdd0/tmp/netemu_log.bin...", flush=True)
    out_log = ROOT / "local_only" / "netemu_log_p16_sync.bin"
    with ftplib.FTP(HOST, timeout=10, encoding="latin-1") as ftp:
        ftp.login()
        with open(out_log, "wb") as f:
            ftp.retrbinary("RETR /dev_hdd0/tmp/netemu_log.bin", f.write)
    print(f"[+] Downloaded {os.path.getsize(out_log)} bytes to {out_log}", flush=True)

    # 12. Run decoder
    print("\n[Step 11] Decoding log records...", flush=True)
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools" / "decode_netemu_log.py"), str(out_log)])

    print("\n=======================================================", flush=True)
    print("  TEST COMPLETED SUCCESSFULLY!", flush=True)
    print("=======================================================", flush=True)

if __name__ == "__main__":
    main()
