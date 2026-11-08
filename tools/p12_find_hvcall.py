from pathlib import Path

content = Path('local_only/mamba_lv1call.h').read_text(encoding='utf-8', errors='ignore')
for line in content.splitlines():
    if 'peek' in line.lower() or 'poke' in line.lower():
        print(line)
