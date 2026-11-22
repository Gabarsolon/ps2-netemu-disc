"""Automated netemu test loop: [install] -> launch ISO via webMAN -> wait -> quit game -> pull + decode log.

Usage (python -I tools/run_test.py [--install <self>] [--wait 20] [--pad] [--dry]):
  --install <self>  run tools\\install_netemu.ps1 -File <self> -Force first (audited builds only)
  --iso <name>      ISO file name under /dev_hdd0/PS2ISO (default: the Buzz! test ISO)
  --wait N          seconds to wait after the game starts (default 20)
  --keep            do not exit the game (default: exit with CROSS, LEFT, CROSS on the Pico bridge, COM9)
  --dry             print the steps and URLs, send nothing
Only webMAN GETs (mount.ps3, quit.ps3, root), an FTP read of the log, and optional controller taps.
"""
import argparse
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HOST = "192.168.0.169"
ISO = "Buzz! The Schools Quiz (Europe).iso"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def get(url, timeout=15):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install")
    ap.add_argument("--iso", default=ISO)
    ap.add_argument("--wait", type=int, default=20)
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--attach", action="store_true", help="game already running: skip install and launch")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "local_only", "run_test_log.bin"))
    a = ap.parse_args()

    mount = "http://%s/mount.ps3/dev_hdd0/PS2ISO/%s" % (HOST, urllib.parse.quote(a.iso))
    play = "http://%s/play.ps3/dev_hdd0/PS2ISO/%s" % (HOST, urllib.parse.quote(a.iso, safe="!()"))
    ftp = "ftp://%s/dev_hdd0/tmp/netemu_log.bin" % HOST
    steps = []
    if a.attach:
        steps = ["attach to the running game"]
    elif a.install:
        steps.append("install %s" % a.install)
    if not a.attach:
      steps += ["GET " + play + "  (mounts and starts the game)", "wait %ds" % a.wait]
    if not a.keep:
        steps.append("pad: PS, CROSS, LEFT, CROSS (exit game: NO -> YES)")
    steps += ["wait for webMAN/FTP (max 3 min)", "FTP read " + ftp, "decode"]
    print("\n".join("  - " + s for s in steps))
    if a.dry:
        return 0

    if a.install and not a.attach:
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
               os.path.join(HERE, "install_netemu.ps1"), "-File", a.install, "-Force"]
        print("installing ...")
        if subprocess.call(cmd, cwd=ROOT) != 0:
            print("install failed, stopping")
            return 2
    if not a.attach and get("http://%s/" % HOST, 8) != 200:
        print("webMAN not answering, stopping")
        return 3
    old = open(a.out, "rb").read() if os.path.exists(a.out) else b""
    if not a.attach:
        print("play:", get(play))
        time.sleep(a.wait)
    if not a.keep:
        sys.path.insert(0, os.path.expanduser("~"))
        from ps3_controller import PS3Controller
        ctl = PS3Controller("COM9")
        try:
            print("status:", ctl.get_status())
            for b in ("PS", "CROSS", "LEFT", "CROSS"):
                print(b, ctl.press(b, 150))
                time.sleep(2.0 if b == "PS" else 1.2)
        finally:
            ctl.close()
    ok = False
    for _ in range(18):
        time.sleep(10)
        try:
            if get("http://%s/" % HOST, 6) == 200:
                ok = True
                break
        except Exception:
            pass
    if not ok:
        print("webMAN did not come back in 3 minutes, stopping (log not pulled)")
        return 4
    subprocess.check_call(["curl.exe", "-s", "-m", "60", "-o", a.out, ftp])
    print("log saved:", a.out, os.path.getsize(a.out))
    if open(a.out, "rb").read() == old:
        print("NO NEW RUN: the log is identical to the previous one; do not trust it")
        return 5
    subprocess.call([sys.executable, "-I", os.path.join(HERE, "decode_netemu_log.py"), a.out], cwd=ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
