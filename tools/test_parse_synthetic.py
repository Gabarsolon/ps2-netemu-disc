import re

def parse_webman_html(html_text, expected_addr):
    # Strip HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', html_text)
    pattern = re.compile(r'([0-9A-F]{8})\s+((?:[0-9A-F]{2} ){16})')
    matches = pattern.findall(clean_text)
    
    if len(matches) != 32:
        return None, f"Expected 32 lines, got {len(matches)}"
    
    first_addr_int = int(matches[0][0], 16)
    expected_aligned = expected_addr & ~0xF
    if first_addr_int != expected_aligned:
        return None, f"First line address 0x{first_addr_int:08X} != expected 0x{expected_aligned:08X}"
    
    window_bytes = bytearray()
    for i, (addr_str, hex_str) in enumerate(matches):
        line_addr = int(addr_str, 16)
        if line_addr != expected_aligned + (i * 16):
            return None, f"Discontinuous address at line {i}: 0x{line_addr:08X}"
        line_bytes = bytes.fromhex(hex_str.strip())
        if len(line_bytes) != 16:
            return None, f"Line {i} has {len(line_bytes)} bytes instead of 16"
        window_bytes.extend(line_bytes)
        
    if len(window_bytes) != 512:
        return None, f"Window bytes length {len(window_bytes)} != 512"
        
    return bytes(window_bytes), None

# Test with synthetic HTML
lines = []
lines.append("<html><body><pre>")
addr = 0x1001F0
for i in range(32):
    b_str = " ".join(f"{(addr + i*16 + j) & 0xFF:02X}" for j in range(16))
    lines.append(f"{addr + i*16:08X}  {b_str}  ................<br>")
lines.append("</pre></body></html>")
sample = "\n".join(lines)

b, err = parse_webman_html(sample, addr)
print("Parse test result:", "OK" if b and not err else f"ERR: {err}")
if b:
    print(f"Parsed {len(b)} bytes from 0x{addr:X}")
