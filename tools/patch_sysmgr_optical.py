#!/usr/bin/env python3
"""Firmware-route LV1 RAM patches A/B for sysmgr_ss (live, reboot-recoverable).

Locates two sites by UNIQUE signature in the permanent HV pool, peek-verifies the
stock bytes, and (only with --apply) pokes them. --restore puts stock back.
RAM only via webMAN peek.lv1/poke.lv1 -- NEVER writes /dev_flash. Reboot clears pokes.

A (ability bit): preserve PS2_NE_LPAR optical ability 0x02000000.
    sig f97d0000 7c004838 ; patch the 7c004838 word (sig+4) -> 60000000 (nop)
B (BD bridge power): make PS2_NE_LPAR +0xc0 power the bus.
    sig f8030060 4e800020 38600001 4e800020 ; patch the 38600001 word (sig+8)
    -> 480003f4 (b 0x8001decc, PC-relative)

Usage: python -I tools/patch_sysmgr_optical.py [--locate|--check|--apply|--restore]
       [--host 192.168.0.169] [--start 0x120000] [--end 0x180000]
"""
import argparse, re, sys, time, urllib.request

HOST = "192.168.0.169"
POOL_START, POOL_END = 0x100000, 0x300000

SITES = [
    {"name": "A ability-bit", "sig": bytes.fromhex("f97d00007c004838"),
     "patch_off": 4, "stock": "7c004838", "patch": "60000000"},
    {"name": "B bridge-power", "sig": bytes.fromhex("f80300604e800020386000014e800020"),
     "patch_off": 8, "stock": "38600001", "patch": "480003f4"},
]

LINE = re.compile(r"([0-9A-Fa-f]{8})\s+((?:[0-9A-Fa-f]{2} ){16})")

def http_get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def peek_block(addr):
    """Return (base, bytes) for the 512-byte block webMAN dumps at addr."""
    txt = http_get(f"http://{HOST}/peek.lv1?{addr:x}")
    base = None; buf = bytearray()
    for m in LINE.finditer(txt):
        a = int(m.group(1), 16)
        row = bytes(int(x, 16) for x in m.group(2).split())
        if base is None:
            base = a
        if a == (base + len(buf)):
            buf += row
    return base, bytes(buf)

def peek_word(addr):
    base, buf = peek_block(addr & ~0x1FF)
    if base is None:
        raise RuntimeError(f"peek parse fail @ {addr:#x}")
    o = addr - base
    return buf[o:o+4].hex()

def poke_word(addr, hexval):
    return http_get(f"http://{HOST}/poke.lv1?{addr:x}={hexval}")

def scan_runs(start, end):
    """Peek the band in 512-byte steps, gap-tolerant. Return list of (base, bytes) runs."""
    blocks = {}
    a = start
    while a < end:
        try:
            b, buf = peek_block(a)
        except Exception:
            b, buf = None, b""
        if b is not None and buf:
            blocks[b] = buf
            a = b + len(buf)
        else:
            a += 0x200
        time.sleep(0.01)
    # stitch contiguous blocks into runs
    runs = []
    for base in sorted(blocks):
        buf = blocks[base]
        if runs and runs[-1][0] + len(runs[-1][1]) == base:
            runs[-1] = (runs[-1][0], runs[-1][1] + buf)
        else:
            runs.append((base, bytearray(buf)))
    return [(b, bytes(d)) for b, d in runs]

def locate(start, end):
    print(f"[*] scanning {start:#x}..{end:#x} for signatures ...", flush=True)
    runs = scan_runs(start, end)
    total = sum(len(d) for _, d in runs)
    print(f"    mapped {total} bytes in {len(runs)} run(s)", flush=True)
    found = {}
    for s in SITES:
        hits = []
        for base, data in runs:
            i = 0
            while True:
                i = data.find(s["sig"], i)
                if i < 0:
                    break
                hits.append(base + i); i += 1
        if not hits:
            print(f"    {s['name']}: NOT FOUND"); continue
        if len(hits) != 1:
            print(f"    {s['name']}: {len(hits)} matches {[hex(h) for h in hits]} (ambiguous) -- refusing"); continue
        site_addr = hits[0]
        patch_addr = site_addr + s["patch_off"]
        found[s["name"]] = (site_addr, patch_addr)
        print(f"    {s['name']}: sig@{site_addr:#x} patch_word@{patch_addr:#x}")
    return found

def check(found=None):
    if found is None:
        found = locate(args.start, args.end)
    ok = True
    for s in SITES:
        if s["name"] not in found:
            ok = False; continue
        _, pa = found[s["name"]]
        live = peek_word(pa)
        state = "STOCK" if live == s["stock"] else ("PATCHED" if live == s["patch"] else "UNKNOWN")
        print(f"    {s['name']} @ {pa:#x}: live={live} [{state}]")
        if state == "UNKNOWN":
            ok = False
    return ok, found

def apply():
    found = locate(args.start, args.end)
    if len(found) != len(SITES):
        print("[-] not all sites located; refusing to patch"); return 1
    for s in SITES:
        _, pa = found[s["name"]]
        live = peek_word(pa)
        if live == s["patch"]:
            print(f"    {s['name']} @ {pa:#x} already PATCHED"); continue
        if live != s["stock"]:
            print(f"[-] {s['name']} @ {pa:#x} live={live} != stock {s['stock']}; refusing"); return 1
        print(f"    poking {pa:#x} {s['stock']} -> {s['patch']}", flush=True)
        poke_word(pa, s["patch"])
        nv = peek_word(pa)
        if nv != s["patch"]:
            print(f"[-] verify FAIL @ {pa:#x}: got {nv}"); return 1
        print(f"    [+] verified {s['name']} = {nv}")
    print("[+] A+B applied."); return 0

def restore():
    found = locate(args.start, args.end)
    for s in SITES:
        if s["name"] not in found:
            continue
        _, pa = found[s["name"]]
        live = peek_word(pa)
        if live == s["stock"]:
            print(f"    {s['name']} @ {pa:#x} already STOCK"); continue
        poke_word(pa, s["stock"])
        nv = peek_word(pa)
        print(f"    {s['name']} @ {pa:#x} -> {nv} ({'OK' if nv==s['stock'] else 'FAIL'})")
    print("[+] restore done."); return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=HOST)
    ap.add_argument("--start", type=lambda x: int(x, 0), default=0x120000)
    ap.add_argument("--end", type=lambda x: int(x, 0), default=0x180000)
    ap.add_argument("--locate", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--restore", action="store_true")
    args = ap.parse_args()
    HOST = args.host
    if args.apply:
        sys.exit(apply())
    if args.restore:
        sys.exit(restore())
    if args.check:
        ok, _ = check(); sys.exit(0 if ok else 2)
    locate(args.start, args.end)
