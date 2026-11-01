#!/usr/bin/env python3
"""
tools/p12_scan_ss1.py - Read-only LV1 memory scan via webMAN MOD HTTP peek

Performs read-only HTTP GET requests:
  http://192.168.0.169/peek.lv1?<hexaddr>
Scanning range 0x100000..0x300000 in overlapping 512-byte windows (step 0x1F0).
Searches for ss_server1 profile check pattern:
  81 21 00 70 3D 29 FF FF 39 29 00 A0 2B 89 00 01
and ss_server3 Cobra pattern:
  40 9E 00 70 2F BE 00 01

Usage:
  python -I tools/p12_scan_ss1.py --dry
  python -I tools/p12_scan_ss1.py --test
  python -I tools/p12_scan_ss1.py
"""

import sys
import os
import time
import re
import urllib.request
import urllib.error
from pathlib import Path

CONSOLE_IP = "192.168.0.169"
START_ADDR = 0x100000
END_ADDR = 0x300000
WINDOW_SIZE = 0x200   # 512 bytes
STEP = 0x1F0          # 496 bytes (16 bytes overlap)
REQUEST_PAUSE = 0.15  # 0.15 s pause between requests
REQUEST_TIMEOUT = 10  # 10 s timeout per request

PATTERN_SS1 = bytes.fromhex("812100703D29FFFF392900A02B890001")
PATTERN_SS3 = bytes.fromhex("409E00702FBE0001")

TAG_RE = re.compile(r'<[^>]+>')
HEX_LINE_RE = re.compile(r'([0-9A-Fa-f]{8})\s+((?:[0-9A-Fa-f]{2} ){16})')

def generate_window_addresses(start=START_ADDR, end=END_ADDR, win_size=WINDOW_SIZE, step=STEP):
    """Generate list of starting addresses for the scan windows."""
    addrs = []
    curr = start
    while curr + win_size <= end:
        addrs.append(curr)
        curr += step
    # Include final window ending exactly at end_addr if not already aligned
    if addrs and (addrs[-1] + win_size < end):
        final_addr = end - win_size
        if final_addr not in addrs:
            addrs.append(final_addr)
    return addrs

def parse_peek_html(html_text, expected_addr):
    """
    Parse webMAN MOD peek.lv1 HTML reply.
    Strips HTML tags, regex-matches hex lines, and verifies structure.
    Returns (bytes_512, None) on success or (None, error_str) on failure.
    """
    # Strip HTML tags
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
        return None, f"First line address 0x{first_addr:08X} does not match expected 0x{expected_aligned:08X}"
    
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

def run_self_tests():
    """Unit-test the address generator, HTML parser, and pattern matcher."""
    print("[TEST] Running unit tests...")
    
    # Test 1: Window address generation
    addrs = generate_window_addresses()
    assert len(addrs) == 4229, f"Expected 4229 addresses, got {len(addrs)}"
    assert addrs[0] == 0x100000, f"First address != 0x100000: 0x{addrs[0]:x}"
    assert addrs[-1] == 0x2FFE00, f"Last address != 0x2FFE00: 0x{addrs[-1]:x}"
    assert addrs[-1] + WINDOW_SIZE == 0x300000, "Last window does not end at 0x300000"
    for a in addrs:
        assert (a & 0xF) == 0, f"Address 0x{a:x} is not 16-byte aligned"
        assert a + WINDOW_SIZE <= 0x300000, f"Window at 0x{a:x} extends past 0x300000"
    print(f"  [PASS] Window generation verified: {len(addrs)} windows (0x{addrs[0]:x}..0x{addrs[-1]:x})")
    
    # Test 2: Full coverage
    cov = bytearray(END_ADDR - START_ADDR)
    for a in addrs:
        off = a - START_ADDR
        cov[off : off + WINDOW_SIZE] = b'\x01' * WINDOW_SIZE
    assert all(cov), "Coverage gaps detected"
    print("  [PASS] Full 2 MiB coverage verified with zero gaps")
    
    # Test 3: Synthetic HTML parser
    sample_lines = ["<html><body><pre>"]
    t_addr = 0x1001F0
    for i in range(32):
        hex_b = " ".join(f"{(t_addr + i*16 + j) & 0xFF:02X}" for j in range(16))
        sample_lines.append(f"{t_addr + i*16:08X}  {hex_b}  ................<br>")
    sample_lines.append("</pre></body></html>")
    sample_html = "\n".join(sample_lines)
    parsed_b, err = parse_peek_html(sample_html, t_addr)
    assert err is None, f"Synthetic parse failed: {err}"
    assert len(parsed_b) == 512, "Synthetic parse length != 512"
    assert parsed_b[0] == (t_addr & 0xFF), "Synthetic byte mismatch"
    print("  [PASS] Synthetic HTML parser verified")
    
    # Test 4: Pattern matching on ss_server1.elf
    elf_p = Path(__file__).resolve().parent.parent / "local_only" / "analysis" / "p0i" / "modules" / "ss_server1.elf"
    if elf_p.exists():
        elf_data = elf_p.read_bytes()
        pos = elf_data.find(PATTERN_SS1)
        assert pos != -1, "Pattern SS1 not found in ss_server1.elf"
        assert pos == 0x30700, f"Pattern SS1 at 0x{pos:x} != expected 0x30700"
        four_bytes = elf_data[pos + 0x10 : pos + 0x14]
        assert four_bytes == bytes.fromhex("409D001C"), f"Unexpected opcode at +0x10: {four_bytes.hex()}"
        print(f"  [PASS] ss_server1.elf pattern match verified at offset 0x{pos:x}")
    else:
        print("  [WARN] ss_server1.elf not found, skipped elf test")
        
    print("[TEST] All unit tests PASSED successfully!\n")

def fetch_peek_window(addr, retry_count=1):
    """
    Fetch a single 512-byte window from webMAN MOD.
    URL: http://192.168.0.169/peek.lv1?<hexaddr>
    Retries once on HTTP/network error.
    Returns (raw_html, error_msg).
    """
    url = f"http://{CONSOLE_IP}/peek.lv1?{addr:x}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    
    last_err = None
    for attempt in range(retry_count + 1):
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                if resp.status != 200:
                    last_err = f"HTTP {resp.status}"
                else:
                    html = resp.read().decode('latin1', errors='replace')
                    return html, None
        except urllib.error.HTTPError as e:
            last_err = f"HTTPError {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            last_err = f"URLError: {e.reason}"
        except Exception as e:
            last_err = f"Exception: {type(e).__name__}: {e}"
        
        if attempt < retry_count:
            time.sleep(0.5)
            
    return None, f"Failed GET {url} after {retry_count + 1} attempts: {last_err}"

def run_scan(is_dry=False):
    """Execute the LV1 memory scan."""
    root_dir = Path(__file__).resolve().parent.parent
    log_file = root_dir / "local_only" / "p12_scan_ss1.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    addrs = generate_window_addresses()
    total_reqs = len(addrs)
    
    print(f"=== PS3 LV1 Memory Scan (P12-scan) ===")
    print(f"Target: http://{CONSOLE_IP}/peek.lv1?<hexaddr>")
    print(f"Address Range: 0x{START_ADDR:08X}..0x{END_ADDR:08X} (2 MiB)")
    print(f"Window Size: {WINDOW_SIZE} bytes, Step: {STEP} bytes (Overlap: {WINDOW_SIZE - STEP} bytes)")
    print(f"Total Requests: {total_reqs}")
    print(f"First URL: http://{CONSOLE_IP}/peek.lv1?{addrs[0]:x}")
    print(f"Last URL:  http://{CONSOLE_IP}/peek.lv1?{addrs[-1]:x}")
    print(f"Dry run: {is_dry}\n")
    
    if is_dry:
        print("[DRY] Dry run complete. No network requests sent.")
        return 0
    
    # Load decrypted ss_server1.elf for context verification
    elf_path = root_dir / "local_only" / "analysis" / "p0i" / "modules" / "ss_server1.elf"
    elf_data = None
    if elf_path.exists():
        elf_data = elf_path.read_bytes()
        print(f"Loaded reference ss_server1.elf: {len(elf_data)} bytes")
    else:
        print(f"WARNING: Reference {elf_path} not found!")

    # Preallocate 2 MiB buffer
    mem_size = END_ADDR - START_ADDR
    mem = bytearray(mem_size)
    covered = bytearray(mem_size)
    
    start_time = time.time()
    req_success = 0
    parse_errors = 0
    aborted = False
    abort_reason = ""
    
    log_lines = []
    log_lines.append(f"Scan started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log_lines.append(f"Target: http://{CONSOLE_IP}/peek.lv1?<hexaddr>")
    log_lines.append(f"Range: 0x{START_ADDR:08X}..0x{END_ADDR:08X}, Windows: {total_reqs}")
    log_lines.append("-" * 60)
    
    try:
        for idx, addr in enumerate(addrs):
            html, net_err = fetch_peek_window(addr, retry_count=1)
            if net_err:
                aborted = True
                abort_reason = f"Network abort at window {idx+1}/{total_reqs} (0x{addr:08X}): {net_err}"
                print(f"\n[ABORT] {abort_reason}")
                break
                
            w_bytes, p_err = parse_peek_html(html, addr)
            if p_err:
                parse_errors += 1
                msg = f"Parse error at window {idx+1}/{total_reqs} (0x{addr:08X}): {p_err}"
                print(f"\n[PARSE ERROR] {msg}")
                log_lines.append(msg)
                if parse_errors >= 3:
                    aborted = True
                    abort_reason = f"Exceeded max parse errors (3) at 0x{addr:08X}"
                    print(f"\n[ABORT] {abort_reason}")
                    break
            else:
                # Store into full buffer
                off = addr - START_ADDR
                mem[off : off + WINDOW_SIZE] = w_bytes
                covered[off : off + WINDOW_SIZE] = b'\x01' * WINDOW_SIZE
                req_success += 1
            
            # Progress display every 100 windows
            if (idx + 1) % 100 == 0 or (idx + 1) == total_reqs:
                elapsed = time.time() - start_time
                rate = (idx + 1) / elapsed if elapsed > 0 else 0
                eta = (total_reqs - (idx + 1)) / rate if rate > 0 else 0
                print(f"\rProgress: {idx+1:4d}/{total_reqs} ({(idx+1)/total_reqs*100:5.1f}%) | "
                      f"Addr: 0x{addr:08X} | Rate: {rate:4.1f} req/s | ETA: {eta:4.0f}s", end="", flush=True)
            
            # Inter-request delay
            time.sleep(REQUEST_PAUSE)
            
    except KeyboardInterrupt:
        aborted = True
        abort_reason = "Scan interrupted by user (SIGINT)"
        print(f"\n[ABORT] {abort_reason}")
    
    elapsed_total = time.time() - start_time
    print(f"\n\nScan completed in {elapsed_total:.2f}s ({req_success}/{total_reqs} requests successful).")
    
    # Pattern Analysis
    matches_ss1 = []
    matches_ss3 = []
    
    # Search collected memory for PATTERN_SS1
    p = 0
    raw_mem = bytes(mem)
    while True:
        pos = raw_mem.find(PATTERN_SS1, p)
        if pos == -1:
            break
        phys_addr = START_ADDR + pos
        matches_ss1.append((pos, phys_addr))
        p = pos + 1
        
    # Search collected memory for PATTERN_SS3
    p = 0
    while True:
        pos = raw_mem.find(PATTERN_SS3, p)
        if pos == -1:
            break
        phys_addr = START_ADDR + pos
        matches_ss3.append((pos, phys_addr))
        p = pos + 1
    
    print("\n=== PATTERN SEARCH RESULTS ===")
    print(f"ss_server1 pattern matches (0x812100703D29FFFF392900A02B890001): {len(matches_ss1)}")
    
    verified_ss1_match = None
    for idx, (pos, phys_addr) in enumerate(matches_ss1):
        opcode_bytes = raw_mem[pos + 0x10 : pos + 0x14]
        opcode_hex = opcode_bytes.hex().upper()
        
        # Context comparison: 64 bytes starting 0x20 before match
        ctx_mem = raw_mem[pos - 0x20 : pos - 0x20 + 64] if pos >= 0x20 else b""
        ctx_match = False
        ctx_details = "N/A (reference ELF not available)"
        if elf_data:
            ref_pos = elf_data.find(PATTERN_SS1)
            if ref_pos != -1 and ref_pos >= 0x20:
                ref_ctx = elf_data[ref_pos - 0x20 : ref_pos - 0x20 + 64]
                ctx_match = (ctx_mem == ref_ctx)
                if ctx_match:
                    ctx_details = f"IDENTICAL to ss_server1.elf at offset 0x{ref_pos:X}"
                else:
                    ctx_details = f"MISMATCH against ss_server1.elf at offset 0x{ref_pos:X}"
        
        match_info = (f"  Match #{idx+1}: Physical Address 0x{phys_addr:08X}\n"
                      f"    4 bytes at +0x10: 0x{opcode_hex} (Expected: 0x409D001C)\n"
                      f"    Context (64 bytes from -0x20): {ctx_details}")
        print(match_info)
        log_lines.append(match_info)
        
        if ctx_match and opcode_hex == "409D001C":
            verified_ss1_match = phys_addr

    print(f"\nss_server3 Cobra pattern matches (0x409E00702FBE0001): {len(matches_ss3)}")
    for idx, (pos, phys_addr) in enumerate(matches_ss3):
        opcode_bytes = raw_mem[pos + 0x10 : pos + 0x14]
        opcode_hex = opcode_bytes.hex().upper()
        cobra_state = "STOCK (38600002 = li r3, 2)" if opcode_hex == "38600002" else \
                      ("COBRA PATCHED (38600029 = li r3, 0x29)" if opcode_hex == "38600029" else f"OTHER (0x{opcode_hex})")
        info = f"  Match #{idx+1}: Physical Address 0x{phys_addr:08X} | +0x10: 0x{opcode_hex} ({cobra_state})"
        print(info)
        log_lines.append(info)

    # Summary
    log_lines.append("-" * 60)
    log_lines.append(f"Requests Total: {total_reqs}, Successful: {req_success}, Parse Errors: {parse_errors}")
    log_lines.append(f"Duration: {elapsed_total:.2f}s")
    log_lines.append(f"Aborted: {aborted} ({abort_reason if aborted else 'None'})")
    log_lines.append(f"ss_server1 match count: {len(matches_ss1)}")
    if verified_ss1_match:
        log_lines.append(f"VERIFIED UNIQUE SS_SERVER1 PROFILE CHECK ADDRESS: 0x{verified_ss1_match:08X}")
    else:
        log_lines.append("VERIFIED UNIQUE SS_SERVER1 MATCH: NONE")
    log_lines.append(f"Scan finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save log
    log_file.write_text("\n".join(log_lines), encoding="utf-8")
    print(f"\nScan log saved to: {log_file}")
    
    return 0 if (len(matches_ss1) == 1 and verified_ss1_match is not None) else 1

if __name__ == "__main__":
    if "--test" in sys.argv:
        run_self_tests()
        sys.exit(0)
    is_dry = "--dry" in sys.argv
    sys.exit(run_scan(is_dry=is_dry))
