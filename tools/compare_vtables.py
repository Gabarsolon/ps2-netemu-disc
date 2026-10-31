from pathlib import Path
import struct

elf = Path('local_only/analysis/p0i/modules/sysmgr_ss.elf').read_bytes()
toc = 0xc0012f40

def ptr_to_off(p):
    if 0x80000000 <= p < 0x80040000:
        return p - 0x80000000 + 0x10000
    if 0xc0000000 <= p < 0xc0010000:
        return p - 0xc0000000 + 0x50000
    return None

def get_vtable_entries(disp, name):
    va = toc + disp
    off = ptr_to_off(va)
    vtable_va = struct.unpack_from('>Q', elf, off)[0]
    print(f"\n=== Vtable for {name} at {hex(vtable_va)} (TOC disp {disp}) ===")
    v_off = ptr_to_off(vtable_va)
    entries = []
    for i in range(25): # first 25 virtual methods
        method_va = struct.unpack_from('>Q', elf, v_off + i * 8)[0]
        m_off = ptr_to_off(method_va)
        if m_off:
            fn_code, fn_toc, _ = struct.unpack_from('>QQQ', elf, m_off)
            entries.append((i * 8, hex(method_va), hex(fn_code)))
            print(f"  +{hex(i*8)}: desc={hex(method_va)} code={hex(fn_code)}")
        else:
            entries.append((i * 8, hex(method_va), "non-descriptor"))
            print(f"  +{hex(i*8)}: {hex(method_va)}")
    return entries

ne_vt = get_vtable_entries(-28392, "PS2_NE_LPAR")
sw_vt = get_vtable_entries(-28408, "PS2_SW_LPAR")
hw_vt = get_vtable_entries(-28400, "PS2_LPAR")

# Compare method by method
print("\n=== Diff: PS2_SW_LPAR vs PS2_NE_LPAR ===")
for i in range(min(len(sw_vt), len(ne_vt))):
    off, desc_sw, code_sw = sw_vt[i]
    _, desc_ne, code_ne = ne_vt[i]
    diff = "DIFF!" if code_sw != code_ne else "same"
    print(f"  +{hex(off):5s}: SW={code_sw:12s} NE={code_ne:12s} [{diff}]")
