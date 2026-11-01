import re

code = open('netemu_p2e/src/probe.c', 'r', encoding='utf-8').read()
strings = re.findall(r'"([^"]*)"', code)
matches = 0
for s in strings:
    b = s.encode('utf-8')
    for i in range(len(b) - 3):
        w = int.from_bytes(b[i:i+4], 'big')
        if (w & 0xFC000003) == 0x44000002:
            print(f'Match in string "{s}" at offset {i}: {b[i:i+4]} (0x{w:08x})')
            matches += 1
print(f'String scan completed: {matches} matches found.')
