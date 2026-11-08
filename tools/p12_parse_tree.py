import json
from pathlib import Path

data = json.loads(Path('local_only/mamba_tree.json').read_text(encoding='utf-8', errors='ignore'))
if 'tree' in data:
    for item in data['tree']:
        path = item['path']
        if 'patch.h' in path or 'storage_ext' in path or 'lv1' in path:
            print(path)
else:
    print("API response:", data.get('message', 'no tree'))
