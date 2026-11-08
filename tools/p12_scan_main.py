from pathlib import Path

content = Path('local_only/main_cobra7.c').read_text(encoding='utf-8', errors='ignore')
lines = content.splitlines()

for idx, line in enumerate(lines, 1):
    if 'storage_ext_patches' in line or 'main(' in line or 'stage2' in line:
        print(f"Line {idx}: {line.strip()}")
