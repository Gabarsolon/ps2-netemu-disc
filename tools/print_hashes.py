import json

data = json.load(open('netemu_p2e/evidence/p2e_patch_table.json'))
for k in ['K0', 'K1', 'K2', 'K3']:
    print(f'{k}:')
    print(f'  ELF:  {data[k]["elf_sha256"]}')
    print(f'  SELF: {data[k]["self_sha256"]}')
    print(f'  Size: {data[k]["code_size"]} bytes')
