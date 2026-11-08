#!/usr/bin/env python3
"""
tools/p14_walk.py - Safe read-only LV1 pointer chain walker & upper memory explorer

Performs ONLY HTTP GET requests of the form:
  http://192.168.0.169/peek.lv1?<hexaddr>

Allowed address space: [0x80000, 0x01000000) (Upper bound: 16 MiB LV1 RAM)

Usage:
  python -I tools/p14_walk.py --dry
  python -I tools/p14_walk.py --test
  python -I tools/p14_walk.py --peek <hexaddr>
  python -I tools/p14_walk.py --walk
  python -I tools/p14_walk.py --dump-inc <start_hex> <end_hex>
"""

import sys
import os
import time
import re
import json
import hashlib
import struct
import urllib.request
import urllib.error
from pathlib import Path

CONSOLE_IP = "192.168.0.169"
MIN_ALLOWED_ADDR = 0x80000
MAX_ALLOWED_ADDR = 0x01000000  # 16 MiB (Proven LV1 managed RAM upper bound)

WINDOW_SIZE = 0x200    # 512 bytes
STEP        = 0x200    # 512 bytes
REQUEST_PAUSE = 0.15   # >= 0.15s
REQUEST_TIMEOUT = 10   # 10s

TAG_RE = re.compile(r'<[^>]+>')
HEX_LINE_RE = re.compile(r'([0-9A-Fa-f]{8})\s+((?:[0-9A-Fa-f]{2} ){16})')

PEEK_CACHE = {}
REQUEST_COUNT = 0

def check_addr_allowed(addr, size=WINDOW_SIZE):
    if addr < MIN_ALLOWED_ADDR or (addr + size) > MAX_ALLOWED_ADDR:
        raise ValueError(f"Address range [0x{addr:X}, 0x{addr+size:X}) outside allowed bounds [0x{MIN_ALLOWED_ADDR:X}, 0x{MAX_ALLOWED_ADDR:X})")

def parse_peek_html(html_text, expected_addr):
    clean_text = TAG_RE.sub('', html_text)
    matches = HEX_LINE_RE.findall(clean_text)
    
    if len(matches) != 32:
        return None, f"Expected 32 hex lines, found {len(matches)}"
    
    expected_aligned = expected_addr & ~0xF
    try:
        first_addr = int(matches[0][0], 16)
    except ValueError:
        return None, f"Invalid address format in first line: {matches[0][0]}"
    
    if first_addr != expected_aligned:
        return None, f"First line address 0x{first_addr:08X} != expected 0x{expected_aligned:08X}"
    
    window_buf = bytearray()
    for idx, (addr_str, hex_str) in enumerate(matches):
        line_addr = int(addr_str, 16)
        if line_addr != expected_aligned + (idx * 16):
            return None, f"Address gap at line {idx}: 0x{line_addr:08X} != expected 0x{expected_aligned + idx*16:08X}"
        raw_bytes = bytes.fromhex(hex_str.strip())
        if len(raw_bytes) != 16:
            return None, f"Line {idx} length {len(raw_bytes)} != 16"
        window_buf.extend(raw_bytes)
    
    if len(window_buf) != WINDOW_SIZE:
        return None, f"Total parsed window size {len(window_buf)} != {WINDOW_SIZE}"
    
    return bytes(window_buf), None

def fetch_peek_window(addr, retry_count=1):
    global REQUEST_COUNT
    aligned_addr = addr & ~0x1FF
    
    if aligned_addr in PEEK_CACHE:
        return PEEK_CACHE[aligned_addr], None
        
    check_addr_allowed(aligned_addr, WINDOW_SIZE)
    url = f"http://{CONSOLE_IP}/peek.lv1?{aligned_addr:x}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    last_err = None
    for attempt in range(retry_count + 1):
        try:
            REQUEST_COUNT += 1
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                if resp.status != 200:
                    last_err = f"HTTP {resp.status} on {url}"
                    time.sleep(REQUEST_PAUSE)
                    continue
                content = resp.read().decode('utf-8', errors='replace')
                w_bytes, p_err = parse_peek_html(content, aligned_addr)
                if p_err:
                    last_err = f"Parse error on {url}: {p_err}"
                    time.sleep(REQUEST_PAUSE)
                    continue
                PEEK_CACHE[aligned_addr] = w_bytes
                time.sleep(REQUEST_PAUSE)
                return w_bytes, None
        except urllib.error.URLError as e:
            last_err = f"Network error on {url}: {e.reason}"
            time.sleep(REQUEST_PAUSE)
        except Exception as e:
            last_err = f"Unexpected error on {url}: {e}"
            time.sleep(REQUEST_PAUSE)
            
    return None, last_err

def perform_dump(start_addr, end_addr, out_bin_name, desc_name):
    root_dir = Path(__file__).resolve().parent.parent
    bin_path = root_dir / "local_only" / out_bin_name
    manifest_path = root_dir / "local_only" / f"{Path(out_bin_name).stem}.manifest.json"
    bin_path.parent.mkdir(parents=True, exist_ok=True)
    
    total_size = end_addr - start_addr
    num_windows = total_size // STEP
    
    print(f"=== Starting LV1 Memory Dump: {desc_name} ===")
    print(f"Target: http://{CONSOLE_IP}/peek.lv1?<hexaddr>")
    print(f"Range: 0x{start_addr:08X}..0x{end_addr:08X} ({total_size / 1024:.0f} KiB)")
    print(f"Windows: {num_windows} (step 0x{STEP:X})")
    print(f"Output: {bin_path.name}")
    print(f"First URL: http://{CONSOLE_IP}/peek.lv1?{start_addr:x}")
    print(f"Last URL:  http://{CONSOLE_IP}/peek.lv1?{end_addr - STEP:x}\n")
    
    mem_buf = bytearray(total_size)
    start_time = time.time()
    req_success = 0
    parse_errors = 0
    aborted = False
    abort_reason = ""
    
    try:
        for idx in range(num_windows):
            addr = start_addr + idx * STEP
            w_bytes, err = fetch_peek_window(addr, retry_count=1)
            if err:
                aborted = True
                abort_reason = f"Network/parse abort at window {idx+1}/{num_windows} (0x{addr:08X}): {err}"
                print(f"\n[ABORT] {abort_reason}")
                break
            off = addr - start_addr
            mem_buf[off : off + WINDOW_SIZE] = w_bytes
            req_success += 1
            
            if (idx + 1) % 100 == 0 or (idx + 1) == num_windows:
                elapsed = time.time() - start_time
                rate = (idx + 1) / elapsed if elapsed > 0 else 0
                eta = (num_windows - (idx + 1)) / rate if rate > 0 else 0
                print(f"\rProgress: {idx+1:4d}/{num_windows} ({(idx+1)/num_windows*100:5.1f}%) | "
                      f"Addr: 0x{addr:08X} | Rate: {rate:4.1f} req/s | ETA: {eta:4.0f}s", end="", flush=True)
                
    except KeyboardInterrupt:
        aborted = True
        abort_reason = "Interrupted by user"
        print(f"\n[ABORT] {abort_reason}")
        
    elapsed_total = time.time() - start_time
    print(f"\nDump finished in {elapsed_total:.2f}s ({req_success}/{num_windows} successful).")
    
    bin_path.write_bytes(mem_buf)
    sha256 = hashlib.sha256(mem_buf).hexdigest()
    print(f"Saved {len(mem_buf)} bytes to {bin_path} (sha256: {sha256})")
    
    manifest = {
        "description": desc_name,
        "start_addr": hex(start_addr),
        "end_addr": hex(end_addr),
        "total_bytes": total_size,
        "windows_total": num_windows,
        "windows_success": req_success,
        "aborted": aborted,
        "abort_reason": abort_reason,
        "duration_seconds": elapsed_total,
        "sha256": sha256,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved manifest to {manifest_path}\n")
    return not aborted

def run_self_tests():
    print("=== Running P14 Walk Self-Tests ===")
    try:
        check_addr_allowed(0x7FFFF)
        assert False, "Should have failed < 0x80000"
    except ValueError:
        pass
    try:
        check_addr_allowed(0x01000000)
        assert False, "Should have failed >= 0x01000000"
    except ValueError:
        pass
    check_addr_allowed(0x80000)
    check_addr_allowed(0x36CDB0)
    check_addr_allowed(0x700000)
    check_addr_allowed(0x01000000 - 0x200)
    print("  [PASS] Bounds check [0x80000, 0x01000000) verified")
    
    sample_lines = ["<html><body><pre>"]
    t_addr = 0x700000
    for i in range(32):
        hex_b = " ".join(f"{(t_addr + i*16 + j) & 0xFF:02X}" for j in range(16))
        sample_lines.append(f"{t_addr + i*16:08X}  {hex_b}  ................<br>")
    sample_lines.append("</pre></body></html>")
    sample_html = "\n".join(sample_lines)
    parsed_b, err = parse_peek_html(sample_html, t_addr)
    assert err is None, f"Synthetic parse failed: {err}"
    assert len(parsed_b) == 512, "Synthetic parse length != 512"
    print("  [PASS] HTML parser verified")
    print("[TEST] All self-tests PASSED successfully!\n")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "--test":
        run_self_tests()
        sys.exit(0)
    elif cmd == "--dry":
        print("=== DRY RUN (No console contact) ===")
        print(f"Allowed bounds: [0x{MIN_ALLOWED_ADDR:X}, 0x{MAX_ALLOWED_ADDR:X}) (16 MiB LV1 RAM)")
        print(f"Target URL: http://{CONSOLE_IP}/peek.lv1?<hexaddr>")
        print("Dry run complete.")
        sys.exit(0)
    elif cmd == "--peek":
        if len(sys.argv) < 3:
            print("Usage: --peek <hexaddr>")
            sys.exit(1)
        addr = int(sys.argv[2], 16)
        aligned = addr & ~0x1FF
        w_bytes, err = fetch_peek_window(aligned)
        if err:
            print(f"[ERROR] {err}")
            sys.exit(1)
        print(f"Successfully read 512 bytes at 0x{aligned:08X} (offset 0x{addr - aligned:X}):")
        for i in range(0, min(128, len(w_bytes)), 16):
            print(f"  0x{aligned + i:08X}: {w_bytes[i:i+16].hex(' ')}")
        sys.exit(0)
    elif cmd == "--dump-inc":
        if len(sys.argv) < 4:
            print("Usage: --dump-inc <start_hex> <end_hex>")
            sys.exit(1)
        s_addr = int(sys.argv[2], 16)
        e_addr = int(sys.argv[3], 16)
        name = f"lv1_mem_{s_addr:x}_{e_addr:x}.bin"
        success = perform_dump(s_addr, e_addr, name, f"LV1 Increment 0x{s_addr:06X}..0x{e_addr:06X}")
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
