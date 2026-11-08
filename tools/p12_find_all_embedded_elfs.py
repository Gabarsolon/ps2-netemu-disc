from pathlib import Path

data = Path('local_only/fw493/lv1.elf').read_bytes()

idx = 0
while True:
    idx = data.find(b'\x7fELF', idx)
    if idx == -1:
        break
    print(f"ELF header at file off 0x{idx:x}")
    # inspect first 64 bytes
    idx += 4
