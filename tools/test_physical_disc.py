#!/usr/bin/env python3
"""
tools/test_physical_disc.py - Automated test runner for physical PS2 disc execution in netemu.

Flow:
1. Verify and ensure LV2 Cobra patch is active.
2. Launch physical disc via webMAN GET /play.ps3.
3. Wait 25 seconds for netemu boot & probe execution.
4. Send PS Button exit sequence via COM9 DS3 bridge to cleanly flush HDD log and return to XMB.
5. Wait for webMAN HTTP 200 on XMB.
6. Pull /dev_hdd0/tmp/netemu_log.bin and decode.
"""

import sys
import os
import time
import socket
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

# Add DS3 bridge path
sys.path.insert(0, os.path.join(ROOT, "pico-ds3-bridge", "python"))
from ps3_controller import PS3Controller
from patch_lv2_cobra import apply_patch, check_target
from patch_all_live import apply_all as apply_lv1_patches, check_all as check_lv1_patches

def http_get(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": "test_physical_disc/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def main():
    print("==================================================")
    print("PHYSICAL PS2 DISC NETEMU AUTOMATED TEST RUNNER")
    print("==================================================")

    # 1. Check & ensure LV1 Hypervisor and LV2 Cobra patches
    print("\n[Step 1] Ensuring LV1 Hypervisor and LV2 Cobra patches are active...")
    print("[*] Checking LV1 Hypervisor patches...")
    if not check_lv1_patches():
        print("[*] Applying LV1 Hypervisor patches...")
        apply_lv1_patches()
    print("[+] LV1 Hypervisor patches verified.")

    print("[*] Checking LV2 Cobra patch...")
    state, _ = check_target(verbose=False)
    if state != "PATCHED":
        print(f"[*] State is {state}, applying Cobra patch...")
        if not apply_patch():
            print("[-] Failed to apply Cobra LV2 patch. Aborting.")
            return 1
    print("[+] LV2 Cobra patch is ACTIVE.")

    # 2. Check webMAN & disc presence
    print("\n[Step 2] Checking console & physical disc status...")
    try:
        html = http_get(f"http://{HOST}/", timeout=5)
    except Exception as e:
        print(f"[-] Console not responding: {e}")
        return 1

    if "dev_bdvd" not in html:
        print("[-] ERROR: No optical disc detected in /dev_bdvd by webMAN!")
        return 1
    print("[+] Optical disc detected in optical drive tray.")

    # 3. Check COM9 Controller
    print("\n[Step 3] Checking DS3 Pico bridge on COM9...")
    ctl = PS3Controller("COM9")
    try:
        st = ctl.get_status()
        print(f"[+] DS3 Bridge Status: {st}")
    finally:
        ctl.close()

    # 4. Prepare local log destination
    out_log = os.path.join(ROOT, "local_only", "run_test_log.bin")
    old_log_data = open(out_log, "rb").read() if os.path.exists(out_log) else b""

    # 5. Launch physical disc
    print("\n[Step 4] Launching physical disc via webMAN GET /play.ps3...")
    play_url = f"http://{HOST}/play.ps3"
    try:
        resp = http_get(play_url, timeout=15)
        print("[+] /play.ps3 request sent successfully.")
    except Exception as e:
        print(f"[-] Error sending /play.ps3: {e}")
        return 1

    # 6. Wait for netemu boot & probe execution
    wait_time = 25
    print(f"\n[Step 5] Waiting {wait_time}s for netemu to boot, run probe & stabilize...")
    for sec in range(wait_time, 0, -5):
        print(f"    {sec}s remaining...")
        time.sleep(5)

    # 7. Send Controller Exit Sequence
    print("\n[Step 6] Sending DS3 exit sequence via COM9 (PS -> CROSS -> LEFT -> CROSS)...")
    ctl = PS3Controller("COM9")
    try:
        sequence = [
            ("PS", 200, 3.0),
            ("CROSS", 200, 1.5),
            ("LEFT", 200, 1.5),
            ("CROSS", 200, 1.5)
        ]
        for btn, hold_ms, delay_s in sequence:
            print(f"    Pressing {btn} ({hold_ms}ms)...")
            ctl.press(btn, hold_ms)
            time.sleep(delay_s)
    finally:
        ctl.close()
    print("[+] Exit sequence completed.")

    # 8. Wait for XMB return
    print("\n[Step 7] Waiting for PS3 to return to XMB (polling webMAN HTTP)...")
    xmb_ready = False
    for attempt in range(1, 30):
        print(f"    Waiting for XMB (attempt {attempt}/30)...", flush=True)
        try:
            http_get(f"http://{HOST}/", timeout=2)
            xmb_ready = True
            print(f"[+] Console is back on XMB (attempt {attempt}).", flush=True)
            break
        except Exception:
            time.sleep(2)

    if not xmb_ready:
        print("[-] WARNING: PS3 did not return to XMB within 90 seconds.")
        print("    Checking if console crashed or requires manual reset...")
        return 1

    # 9. Pull netemu_log.bin via FTP
    print("\n[Step 8] Pulling /dev_hdd0/tmp/netemu_log.bin via FTP...")
    ftp_url = f"ftp://{HOST}/dev_hdd0/tmp/netemu_log.bin"
    curl_cmd = ["curl.exe", "-s", "-m", "30", "-o", out_log, ftp_url]
    res = subprocess.run(curl_cmd)
    if res.returncode != 0 or not os.path.exists(out_log):
        print(f"[-] Failed to pull log file via curl (rc={res.returncode})")
        return 1

    new_log_data = open(out_log, "rb").read()
    print(f"[+] Log file pulled successfully: {len(new_log_data)} bytes.")

    if new_log_data == old_log_data:
        print("[!] NOTICE: Log file is identical to previous run.")
    else:
        print("[+] NEW LOG DATA RECORDED!")

    # 10. Decode log
    print("\n[Step 9] Decoding netemu_log.bin...")
    decode_cmd = [sys.executable, os.path.join(HERE, "decode_netemu_log.py"), out_log]
    subprocess.run(decode_cmd)

    return 0

if __name__ == "__main__":
    sys.exit(main())
