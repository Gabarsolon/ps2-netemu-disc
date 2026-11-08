from pathlib import Path

content = Path('local_only/mamba_main.c').read_text(encoding='utf-8', errors='ignore')
lines = content.splitlines()

for idx, line in enumerate(lines, 1):
    if 'lv1_peekd' in line or 'lv1_pokew' in line or 'lv1_poked' in line:
        print(f"Line {idx}: {line.strip()}")
