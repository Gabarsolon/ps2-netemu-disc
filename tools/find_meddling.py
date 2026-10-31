from pathlib import Path

ROOT = Path('.')

def search_files(term):
    print(f"=== Searching for '{term}' ===")
    # search lv1.elf
    lv1_bytes = Path('local_only/fw493/lv1.elf').read_bytes()
    p = 0
    while True:
        idx = lv1_bytes.find(term.encode(), p)
        if idx == -1: break
        print(f"  In lv1.elf at file offset {hex(idx)}")
        p = idx + 1
    
    # search all modules
    mod_dir = Path('local_only/analysis/p0i/modules')
    for f in mod_dir.glob('*.elf'):
        b = f.read_bytes()
        p = 0
        while True:
            idx = b.find(term.encode(), p)
            if idx == -1: break
            print(f"  In {f.name} at file offset {hex(idx)}")
            p = idx + 1

search_files('meddling')
