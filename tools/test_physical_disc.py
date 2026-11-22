#!/usr/bin/env python3
"""
tools/test_physical_disc.py - Automated test runner for physical PS2 disc execution in netemu.

Flow:
1. Verify and ensure LV1 ss_server3 Gate & Auth patches are ACTIVE (Gate 1, Gate 2, Site 1, Site 2).
2. Verify and ensure LV2 Cobra stage2 panic bypass is ACTIVE (0x005308C4 -> 48 00 00 10).
3. Reset /dev_hdd0/tmp/netemu_log.bin with 64 KiB zeroes via FTP.
4. Verify Pico DS3 controller bridge on COM9.
5. Launch physical disc via webMAN GET /play.ps3.
6. Wait 22s for netemu boot.
7. Send PS Button tap to trigger optical disc probe & HDD write-ahead log flush.
8. Wait 8s for diagnostic summary & END record to commit.
9. Send exit sequence (CROSS -> LEFT -> CROSS) to cleanly return to XMB.
10. Wait for PS3 to return to XMB (FTP online).
11. Pull /dev_hdd0/tmp/netemu_log.bin and decode.
"""

import sys
import os
import time
import socket
import io
import ftplib
import subprocess
import urllib.request
import urllib.error

# Ensure immediate line flushing
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

# Set global default socket timeout so urllib connect never hangs indefinitely
socket.setdefaulttimeout(5.0)

HOST = "192.168.0.169"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Add DS3 bridge path & tools path
sys.path.insert(0, os.path.join(ROOT, "pico-ds3-bridge", "python"))
sys.path.insert(0, HERE)

from ps3_controller import PS3Controller
from patch_lv2_cobra import apply_patch as apply_cobra_patch, check_target as check_cobra_patch
from patch_ss_server3 import check_patches as check_ss3_patches, apply_patches as apply_ss3_patches

def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "test_physical_disc/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def main():
    print("==================================================")
    print("  PHYSICAL PS2 DISC NETEMU AUTOMATED HARDWARE TEST")
    print("==================================================")

    # 1. Check & ensure LV1 Hypervisor ss_server3 patches
    print("\n[Step 1] Ensuring LV1 ss_server3 Gate Bypasses & Auth Patches are ACTIVE...")
    ss3_state = check_ss3_patches()
    if ss3_state != "ACTIVE":
        print("[*] Applying ss_server3 patches...", flush=True)
        apply_ss3_patches()
    print("[+] LV1 ss_server3 hardware auth patches are ACTIVE.", flush=True)

    # 2. Check & ensure LV2 Cobra stage2 optical bypass
    print("\n[Step 2] Ensuring LV2 Cobra stage2 optical disc panic bypass is ACTIVE...")
    cobra_state, _ = check_cobra_patch(verbose=False)
    if cobra_state != "PATCHED":
        print(f"[*] Cobra state is {cobra_state}, applying bypass...", flush=True)
        if not apply_cobra_patch():
            print("[-] Failed to apply Cobra LV2 patch. Aborting.", flush=True)
            return 1
    print("[+] LV2 Cobra stage2 optical disc panic bypass is ACTIVE.", flush=True)

    # 3. Check optical drive & reset log on PS3
    print("\n[Step 3] Checking optical drive & resetting log on PS3...", flush=True)
    with ftplib.FTP(HOST, timeout=10, encoding="latin-1") as ftp:
        ftp.login()
        disc = ftp.nlst("/dev_bdvd")
        print("    Optical drive contains:", disc[:5], flush=True)
        if "SLES_544.66" not in disc and "SYSTEM.CNF" not in disc:
            print("[-] WARNING: Expected PS2 optical disc (TDU) not detected in /dev_bdvd!", flush=True)

        # Reset log file to 64KB zeroes
        zero_buf = io.BytesIO(b"\x00" * 65536)
        ftp.storbinary("STOR /dev_hdd0/tmp/netemu_log.bin", zero_buf)
        print("[+] Log placeholder /dev_hdd0/tmp/netemu_log.bin reset to 64 KiB zeroes.", flush=True)

    # 4. Check COM9 Controller Bridge
    print("\n[Step 4] Checking DS3 Pico bridge on COM9...", flush=True)
    ctl = PS3Controller("COM9")
    try:
        st = ctl.get_status()
        print(f"    Bridge status: {st}", flush=True)
        if "mounted=1" not in st:
            print("[-] Controller bridge is not mounted to PS3. Aborting.", flush=True)
            return 1
    finally:
        ctl.close()
    print("[+] DS3 bridge verified on COM9.", flush=True)

    # 5. Launch physical disc
    print("\n[Step 5] Launching physical disc via webMAN GET /play.ps3...", flush=True)
    play_url = f"http://{HOST}/play.ps3"
    try:
        resp = http_get(play_url, timeout=15)
        print(f"    Launch response notice: {resp[:80]}...", flush=True)
    except Exception as e:
        print(f"    Launch notice (transitioning): {e}", flush=True)

    # 6. Wait for netemu boot
    wait_time = 22
    print(f"\n[Step 6] Waiting {wait_time}s for netemu to boot from physical disc...", flush=True)
    for sec in range(wait_time, 0, -5):
        print(f"    {sec}s remaining...", flush=True)
        time.sleep(5)

    # 7. Open in-game menu to trigger diagnostic probe
    print("\n[Step 7] Sending PS button to open in-game menu (triggers optical probe)...", flush=True)
    ctl = PS3Controller("COM9")
    try:
        print("    Tapping PS button (300ms)...", flush=True)
        ctl.press("PS", 300)

        # 8. Wait for probe execution & durable HDD log flush
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
    finally:
        ctl.close()
    print("[+] Exit sequence sent. Waiting for console to boot back into XMB...", flush=True)

    # 10. Wait for XMB return
    print("\n[Step 9] Waiting for PS3 to return to XMB (polling FTP)...", flush=True)
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
        print("[-] WARNING: PS3 did not return to XMB within expected time.", flush=True)
        return 1

    # 11. Pull netemu_log.bin via FTP
    print("\n[Step 10] Downloading /dev_hdd0/tmp/netemu_log.bin via FTP...", flush=True)
    out_log = os.path.join(ROOT, "local_only", "netemu_log_physical_disc.bin")
    with ftplib.FTP(HOST, timeout=10, encoding="latin-1") as ftp:
        ftp.login()
        with open(out_log, "wb") as f:
            ftp.retrbinary("RETR /dev_hdd0/tmp/netemu_log.bin", f.write)
    print(f"[+] Downloaded {os.path.getsize(out_log)} bytes to {out_log}", flush=True)

    # 12. Decode log
    print("\n[Step 11] Decoding log records...", flush=True)
    subprocess.run([sys.executable, os.path.join(HERE, "decode_netemu_log.py"), out_log])

    print("\n=======================================================", flush=True)
    print("  PHYSICAL DISC HARDWARE TEST COMPLETED!", flush=True)
    print("=======================================================", flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
