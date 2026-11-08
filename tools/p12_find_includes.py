from pathlib import Path

content = Path('local_only/main_cobra7.c').read_text(encoding='utf-8', errors='ignore')
lines = content.splitlines()

for idx, line in enumerate(lines[:50], 1):
    if line.strip().startswith('#include'):
        print(f"Line {idx}: {line.strip()}")
