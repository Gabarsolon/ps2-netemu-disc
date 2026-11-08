from pathlib import Path
import struct

data = Path('local_only/stock.elf').read_bytes()
e_entry = struct.unpack_from('>Q', data, 0x18)[0]
print(f"e_entry: {hex(e_entry)}")
# e_entry points to OPD: (func_addr, toc_addr)
# Map e_entry to file off:
# Seg 0: off 0x10000 -> VA 0x0
# Seg 1: off 0x310000 -> VA 0x300000
entry_off = e_entry + 0x10000
func_addr, toc_addr = struct.unpack_from('>QQ', data, entry_off)
print(f"Entry function: {hex(func_addr)}, Native TOC: {hex(toc_addr)}")
