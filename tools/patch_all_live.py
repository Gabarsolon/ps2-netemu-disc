import urllib.request
import re
import sys

HOST = "192.168.0.169"

def peek_lv1(addr):
    url = f"http://{HOST}/peek.lv1?{addr:x}"
    req = urllib.request.Request(url, headers={"User-Agent": "patch_all_live/1.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.read().decode('utf-8', errors='ignore')

def poke_lv1(addr, val_hex):
    url = f"http://{HOST}/poke.lv1?{addr:x}={val_hex}"
    req = urllib.request.Request(url, headers={"User-Agent": "patch_all_live/1.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.read().decode('utf-8', errors='ignore')

def extract_word(html, addr):
    addr_str = f"{addr:08X}"
    # find line starting with addr_str
    m = re.search(rf"{addr_str}[ :]+([0-9a-fA-F ]+)", html)
    if not m:
        # maybe it's aligned to 0x10 before
        base = addr & ~0xf
        offset = addr & 0xf
        base_str = f"{base:08X}"
        m2 = re.search(rf"{base_str}[ :]+([0-9a-fA-F ]+)", html)
        if m2:
            parts = m2.group(1).split()
            # each part is 1 byte
            byte_idx = offset
            return "".join(parts[byte_idx:byte_idx+4]).lower()
        return None
    parts = m.group(1).split()
    return "".join(parts[:4]).lower()

PATCHES = [
    {
        "name": "ss_server1 FW Support Check Bypass (0x80020690)",
        "addr": 0x00714690,
        "stock": "4bffea55",
        "patched": "38600000"
    },
    {
        "name": "ss_server1 Profile Check Bypass (0x80020710)",
        "addr": 0x00714710,
        "stock": "409d001c",
        "patched": "4800001c"
    },
    {
        "name": "ss_server1 Profile Canary (0x80020720)",
        "addr": 0x00714720,
        "stock": "3be00016",
        "patched": "3be00077"
    },
    {
        "name": "ss_server3 PS2 Auth Patch (0x80000b54)",
        "addr": 0x00165b54,
        "stock": "38600002",
        "patched": "38600029"
    },
    {
        "name": "ss_server3 PS2 Unauth Patch (0x80000cd0)",
        "addr": 0x00165cd0,
        "stock": "3860001e",
        "patched": "38600029"
    }
]

def check_all():
    print("[*] Checking Hypervisor Patch Status...")
    all_ok = True
    for p in PATCHES:
        html = peek_lv1(p["addr"])
        w = extract_word(html, p["addr"])
        status = "UNKNOWN"
        if w == p["patched"].lower():
            status = "PATCHED"
        elif w == p["stock"].lower():
            status = "STOCK"
            all_ok = False
        else:
            status = f"UNEXPECTED ({w})"
            all_ok = False
        print(f"  [{status:<10}] {p['name']} at 0x{p['addr']:08X}: curr={w} (stock={p['stock']}, patch={p['patched']})")
    return all_ok

def apply_all():
    print("[*] Applying Hypervisor Patches...")
    for p in PATCHES:
        html = peek_lv1(p["addr"])
        w = extract_word(html, p["addr"])
        if w == p["patched"].lower():
            print(f"  [ALREADY] {p['name']} at 0x{p['addr']:08X} is already patched.")
            continue
        print(f"  [POKING]  {p['name']} at 0x{p['addr']:08X}: {w} -> {p['patched']}...")
        poke_lv1(p["addr"], p["patched"])
    
    print("\n[*] Re-verifying...")
    check_all()

if __name__ == "__main__":
    if "--check" in sys.argv:
        check_all()
    else:
        apply_all()
