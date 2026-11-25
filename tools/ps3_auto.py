"""One entry point for unattended PS3 test loops: state, screen grab, hard-cut recovery.

    python tools/ps3_auto.py state              # webMAN HTTP + XMB flag + plug on/off + watts
    python tools/ps3_auto.py grab [out.png]     # one capture-card frame; unmutes the card and retries if black
    python tools/ps3_auto.py recover            # 30 s AC cut, then wait for the sc 377 auto-boot
    python tools/ps3_auto.py recover --force    # same, even if webMAN HTTP still answers

Recovery relies on /dev_hdd0/autoexec.bat re-arming syscall 377 (PS3_SM_WAKE_P_O_R)
at every boot, so AC restore boots the console by itself (PROVEN 3/3, see
docs/PS3_BLUETOOTH_WAKE.md). recover refuses while webMAN answers unless --force:
a healthy PS2 session has no network, so HTTP down alone is not a freeze. Decide
"frozen" first (docs/AUTOMATION.md), then call recover. Exit codes: 0 ok, 1 refused,
2 AC on not verified, 3 no boot within the wait.
"""
from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HOST = 'http://192.168.0.169'
ROOT = Path(__file__).resolve().parents[1]
CAPTURE_TOOLS = Path(r'C:\Users\remus\ps3-240p\tools')   # capture_unmute.py lives here
sys.path.insert(0, r'C:\Users\remus')                     # ps3_power_manager.py (private Tapo config)


def http(path='/cpursx.ps3', timeout=3):
    try:
        with urllib.request.urlopen(HOST + path, timeout=timeout) as r:
            return r.read().decode('utf-8', 'replace')
    except OSError:
        return None


async def plug_device():
    import ps3_power_manager as m
    from tapo import ApiClient
    cfg = m.load_tapo_config()
    device = await asyncio.wait_for(ApiClient(cfg['email'], cfg['password']).p115(cfg['ip']), 15)
    if (await asyncio.wait_for(device.get_device_info(), 10)).model != 'P115':
        raise RuntimeError('expected the verified P115 plug')
    return device


async def plug_state():
    device = await plug_device()
    info = await asyncio.wait_for(device.get_device_info(), 10)
    power = await asyncio.wait_for(device.get_current_power(), 10)
    return info.device_on, power.current_power


def state():
    body = http()
    try:
        on, watts = asyncio.run(plug_state())
        plug = f"plug={'on' if on else 'off'} watts={watts}"
    except Exception as e:  # plug can be unreachable for a while after a console power-off
        plug = f'plug=unreachable ({type(e).__name__})'
    print(f"http={'up' if body else 'down'} xmb={bool(body and '(XMB)' in body)} {plug}")
    return 0


def frame(path):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'dshow', '-rtbufsize', '100M',
                    '-video_size', '1920x1080', '-vcodec', 'mjpeg', '-i', 'video=USB3 Video',
                    '-frames:v', '1', '-update', '1', '-y', str(path)], check=True, timeout=30)
    from PIL import Image, ImageStat
    return ImageStat.Stat(Image.open(path).convert('L')).mean[0]


def unmute():
    sys.path.insert(0, str(CAPTURE_TOOLS))
    import hid
    from capture_unmute import open_card, clear
    device = open_card(hid)
    try:
        return clear(device) & 1
    finally:
        device.close()


def grab(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mean = frame(path)
    note = ''
    if mean < 3:
        try:
            was_muted = unmute()
        except SystemExit as e:  # open_card exits on an unexpected card
            was_muted, note = 0, f' (unmute skipped: {e})'
        if was_muted:
            time.sleep(1)
            mean = frame(path)
            note = ' (card was muted; unmuted and regrabbed - SD image is 1:1 in the top-left)'
    print(f'{path.resolve()} mean={mean:.1f}{note}')
    return 0


async def cut(off_s):
    device = await plug_device()
    try:
        await asyncio.wait_for(device.off(), 10)
        print('AC off', flush=True)
        await asyncio.sleep(off_s)
    finally:
        for attempt in range(6):
            try:
                await asyncio.wait_for(device.on(), 10)
                if (await asyncio.wait_for(device.get_device_info(), 10)).device_on:
                    print('AC on verified', flush=True)
                    return True
            except Exception as e:
                print('AC on retry', type(e).__name__, flush=True)
                await asyncio.sleep(3)
                try:
                    device = await plug_device()
                except Exception:
                    pass
    return False


def recover(force, off_s, wait_s):
    if http() and not force:
        print('webMAN answers: console is not off/frozen at GameOS. Refusing (use --force).')
        return 1
    if not asyncio.run(cut(off_s)):
        print('AC ON NOT VERIFIED - power the plug on by hand.')
        return 2
    t0 = time.time()
    while time.time() - t0 < wait_s:
        if http(timeout=2):
            print(f'auto-boot: webMAN online {time.time() - t0:.0f} s after AC on')
            return 0
        time.sleep(2)
    print(f'no boot within {wait_s} s (autoexec.bat missing, or cut before it ran?) - press the power button.')
    return 3


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('state')
    g = sub.add_parser('grab')
    g.add_argument('out', nargs='?', default=str(ROOT / 'local_only' / 'auto' / time.strftime('grab_%Y%m%dT%H%M%S.png')))
    r = sub.add_parser('recover')
    r.add_argument('--force', action='store_true')
    r.add_argument('--off', type=int, default=30, help='seconds AC off (>=30 proven)')
    r.add_argument('--wait', type=int, default=180, help='seconds to wait for webMAN after AC on')
    a = ap.parse_args()
    if a.cmd == 'state':
        return state()
    if a.cmd == 'grab':
        return grab(a.out)
    return recover(a.force, max(a.off, 30), a.wait)


if __name__ == '__main__':
    sys.exit(main())
