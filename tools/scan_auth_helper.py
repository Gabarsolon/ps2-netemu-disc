#!/usr/bin/env python3
"""Multi-target LV1 RAM scanner for ss_server1 auth helper (0x80020638) code words.

Searches the full LV1 physical space for distinctive byte sequences from the
op-0x5005 auth helper, to enumerate every live copy of this code path.

Usage: python scan_auth_helper.py [--start 0x100000] [--end 0x800000] [--chunk 0x10000]

Read-only: uses webMAN /peek.lv1 only. Reports all matches with phys address.
"""
import sys
import re
import argparse
import urllib.request
from html import unescape

HOST = "192.168.0.169"
CHUNK_DEFAULT = 0x10000  # 64 KB per request

# Distinctive byte sequences from ss_server1 fn_80020638 (op-0x5005 auth helper)
# Each entry: (name, bytes, description)
PATTERNS = [
    # Profile check: subis r9,r9,0x1; addi r9,r9,0xa0; cmplwi cr7,r9,0x1; ble cr7,...
    # This computes (r9 - 0xFF60) <= 1 - the PS2 disc profile gate
    ("profile_check",
     bytes.fromhex("3d29ffff392900a02b890001409d001c"),
     "PS2 profile check (profile - 0xFF60) <= 1"),
    # Secure dispatch: li r3,0xc; bl 0x8003220c
    ("secure_dispatch",
     bytes.fromhex("3860000c48011ad5"),
     "Secure dispatch call (r3=0xc)"),
    # Error 0x16 load: li r31,0x16
    ("error_16",
     bytes.fromhex("3be00016"),
     "Load status 0x16 (profile rejection path)"),
    # /dev/rbd0 query helper call: bl 0x80024e30
    ("rbd0_query",
     bytes.fromhex("48004765"),
     "Call to /dev/rbd0 query helper (0x80024e30)"),
    # Move sub-op to r5 for secure dispatch: or r5,r29,r29
    ("move_subop",
     bytes.fromhex("7fa5eb78"),
     "Move sub-op to r5 before secure dispatch"),
    # Epilogue start: ld r0,0xc0(r1); rldicl r3,r31,0,0x20
    ("epilogue",
     bytes.fromhex("e80100c07be30020"),
     "Epilogue: restore LR, zero-extend return status"),
]

# Also include the helper entry prologue (but it's shared with other functions)
PROLOGUE = bytes.fromhex("f821ff517c0802a6fba10098fbc100a0")  # stdu/mfspr/std/std


def peek_lv1(addr, size=CHUNK_DEFAULT):
    # webMAN LV1 peek takes 32-bit physical address directly
    url = f"http://{HOST}/peek.lv1?{addr:x}"
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.read().decode('utf-8', errors='replace')


def parse_html_to_bytes(html, base_addr):
    """Parse webMAN <pre> memory dump into raw bytes dict {offset_from_base: bytes}."""
    memory = re.search(r"<pre\b[^>]*>(.*?)</pre>", html, flags=re.IGNORECASE | re.DOTALL)
    if memory is None:
        return {}
    html = memory.group(1)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    html = unescape(re.sub(r"<[^>]*>", "", html))
    rows = {}
    pattern = r"(?<![0-9a-fA-F])([0-9a-fA-F]{8})[ :]+((?:[0-9a-fA-F]{2}[ \t]+){15}[0-9a-fA-F]{2})(?![0-9a-fA-F])"
    for match in re.finditer(pattern, html):
        row_addr = int(match.group(1), 16)
        if row_addr % 16:
            continue
        rows[row_addr] = bytes.fromhex(match.group(2))
    # Assemble contiguous bytes from base_addr
    data = bytearray()
    for a in range(base_addr, base_addr + CHUNK_DEFAULT, 16):
        if a in rows:
            data.extend(rows[a])
        else:
            data.extend(b'\x00' * 16)
    return data


def scan_chunk(addr, patterns, verbose=False):
    html = peek_lv1(addr)
    data = parse_html_to_bytes(html, addr)
    if not data:
        return []
    matches = []
    for name, pat, desc in patterns:
        start = 0
        while True:
            idx = data.find(pat, start)
            if idx < 0:
                break
            phys = addr + idx
            matches.append((phys, name, desc))
            start = idx + 1
    return matches


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start', type=lambda x: int(x, 0), default=0x100000,
                        help='LV1 phys start (default 0x100000)')
    parser.add_argument('--end', type=lambda x: int(x, 0), default=0x800000,
                        help='LV1 phys end (default 0x800000)')
    parser.add_argument('--chunk', type=lambda x: int(x, 0), default=CHUNK_DEFAULT,
                        help=f'Bytes per request (default {CHUNK_DEFAULT:#x})')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    start = args.start & ~15
    end = args.end & ~15
    chunk = args.chunk

    print(f"Scanning LV1 phys {start:#x}..{end:#x} in {chunk:#x}-byte chunks")
    print(f"Patterns: {', '.join(n for n,_,_ in PATTERNS)}")
    if args.verbose:
        for n, p, d in PATTERNS:
            print(f"  {n:16s} {p.hex()}  ({d})")

    total_matches = 0
    for addr in range(start, end, chunk):
        if args.verbose:
            sys.stdout.write(f"\r  {addr:#x}..")
            sys.stdout.flush()
        matches = scan_chunk(addr, PATTERNS, args.verbose)
        for phys, name, desc in matches:
            print(f"\n  MATCH: {phys:#x}  {name:16s}  {desc}")
            total_matches += 1
    print(f"\nDone. Total matches: {total_matches}")


if __name__ == '__main__':
    main()