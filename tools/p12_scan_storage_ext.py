from pathlib import Path

content = Path('local_only/storage_ext_cobra7.c').read_text(encoding='utf-8', errors='ignore')
lines = content.splitlines()

keywords = ['ps2', 'ps2emu', 'ss_server', 'auth', '409e', '2fbe', 'disc', 'optical', 'lv1_poke', 'lv1_peek']

for idx, line in enumerate(lines, 1):
    low = line.lower()
    for kw in keywords:
        if kw in low:
            print(f"Line {idx} [{kw}]: {line.strip()}")
            break
