#!/usr/bin/env python3
"""Dump a contiguous LV1 physical window via webMAN /peek.lv1.

Usage: python dump_lv1_window.py <hex_start> <hex_end> <output.bin>

The PS3 must be reachable at 192.168.0.169 with webMAN MOD running.
Read-only: uses /peek.lv1 only. Output is raw binary.
"""
import sys
import re
import time
import urllib.request
from html import unescape
from pathlib import Path

HOST = "192.168.0.169"
VIEW_SIZE = 512  # bytes per peek view (32 lines × 16 bytes)
MAX_RETRIES = 5
RETRY_DELAY = 3.0
INTER_REQUEST_DELAY = 0.1  # seconds between requests


def peek_lv1(addr32):
    """Fetch LV1 memory view at 32-bit physical address with retries."""
    url = f"http://{HOST}/peek.lv1?{addr32:x}"
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                return response.read().decode('utf-8', errors='replace')
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(RETRY_DELAY * (attempt + 1))
    return None


def parse_view(html, expected_addr):
    """Parse a single 512-byte view. Returns bytes or None."""
    m = re.search(r"<pre\b[^>]*>(.*?)</pre>", html, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    content = m.group(1)
    content = re.sub(r"<br\s*/?>", "\n", content, flags=re.IGNORECASE)
    content = unescape(re.sub(r"<[^>]*>", "", content))

    data = bytearray()
    pattern = r"(?<![0-9a-fA-F])([0-9a-fA-F]{8})[ :]+((?:[0-9a-fA-F]{2}[ \t]+){15}[0-9a-fA-F]{2})(?![0-9a-fA-F])"
    for match in re.finditer(pattern, content):
        line_addr = int(match.group(1), 16)
        line_bytes = bytes.fromhex(match.group(2))
        if data and line_addr != ((expected_addr + len(data)) & 0xFFFFFFFF):
            return None
        data.extend(line_bytes)
    return bytes(data)


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    start = int(sys.argv[1], 16)
    end = int(sys.argv[2], 16)
    out = Path(sys.argv[3])

    if start >= end or (end - start) % 16:
        raise SystemExit("start < end and both 16-byte aligned required")

    total = end - start
    num_views = (total + VIEW_SIZE - 1) // VIEW_SIZE
    print(f"Dumping LV1 phys {start:#x}..{end:#x} ({total / 1024 / 1024:.1f} MB, {num_views} views) to {out}")
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open('wb') as f:
        for i in range(num_views):
            phys = start + i * VIEW_SIZE
            remaining = min(VIEW_SIZE, total - i * VIEW_SIZE)

            html = peek_lv1(phys)
            if html is None:
                raise SystemExit(f"Failed to fetch view {i} at {phys:#x}")
            chunk = parse_view(html, phys)
            if chunk is None:
                raise SystemExit(f"Address mismatch in view {i} at {phys:#x}")
            if len(chunk) < remaining:
                raise SystemExit(f"Short read in view {i}: {len(chunk)} < {remaining}")

            f.write(chunk[:remaining])

            done = (i + 1) * VIEW_SIZE
            if done > total:
                done = total
            sys.stdout.write(f"\r  {done / 1024 / 1024:.2f} / {total / 1024 / 1024:.2f} MB  (view {i+1}/{num_views})")
            sys.stdout.flush()

            # Small delay to avoid overwhelming the PS3 web server
            if i < num_views - 1:
                time.sleep(INTER_REQUEST_DELAY)

    print(f"\nDone. Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == '__main__':
    main()