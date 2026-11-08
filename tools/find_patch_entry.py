from pathlib import Path

ROOT = Path(r"C:\Users\remus\ps2-netemu-disc")
c_file = ROOT / "local_only" / "storage_ext_cobra7.c"
lines = c_file.read_text(encoding="utf-8", errors="ignore").splitlines()

for i, l in enumerate(lines):
    if "patch_ps2emu_entry" in l:
        print(f"{i+1}: {l}")
