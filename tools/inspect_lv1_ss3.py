with open(r'C:\Users\remus\ps2-netemu-disc\local_only\fw493\lv1.elf', 'rb') as f:
    f.seek(0x3a7b00)
    data = f.read(256)

print('Data around 0x3a7b50:')
for i in range(0, 256, 16):
    print(f'0x{0x3a7b00+i:x}:', data[i:i+16].hex())
