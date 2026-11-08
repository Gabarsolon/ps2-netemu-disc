import urllib.request
import re

HOST = "192.168.0.169"

def peek_lv1(addr):
    url = f"http://{HOST}/peek.lv1?{addr:x}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.read().decode('utf-8', errors='ignore')

def poke_lv1(addr, val_hex):
    url = f"http://{HOST}/poke.lv1?{addr:x}={val_hex}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.read().decode('utf-8', errors='ignore')

def get_word(html, addr):
    addr_str = f"{addr:08X}"
    m = re.search(rf"{addr_str}[ :]+([0-9a-fA-F ]+)", html)
    if m:
        parts = m.group(1).split()
        return "".join(parts[:4]).lower()
    return None

print("=== Checking ss_server3 PS2 auth patch sites ===")
h1 = peek_lv1(0x165b50)
w1 = get_word(h1, 0x165b50) # wait, addr 165b50 has two words, 165b50 and 165b54
# let's parse 165b54
parts1 = re.search(r"00165B50[ :]+([0-9a-fA-F ]+)", h1).group(1).split()
w1_50 = "".join(parts1[0:4])
w1_54 = "".join(parts1[4:8])
print(f"0x00165B50: {w1_50}")
print(f"0x00165B54: {w1_54} (Stock: 38600002 [li r3, 2], Patched: 38600029 [li r3, 0x29])")

h2 = peek_lv1(0x165cd0)
parts2 = re.search(r"00165CD0[ :]+([0-9a-fA-F ]+)", h2).group(1).split()
w2_d0 = "".join(parts2[0:4])
print(f"0x00165CD0: {w2_d0} (Stock: 3860001e [li r3, 30], Patched: 38600029 [li r3, 0x29])")
