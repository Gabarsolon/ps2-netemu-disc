"""P0G adapter for the existing Ghidra extractor; all outputs stay local_only.

Run only one job at a time. Inputs are the official 3.55 ELFs, or stock netemu.
The shared extractor records hashes, OPDs, syscall context, callers and decomps.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'tools' / 'p0d_ghidra.py').read_text(encoding='utf-8')
source = source.replace("choices=['ps2_emu', 'ps2_gxemu']", "choices=['ps2_softemu', 'ps2_emu', 'ps2_gxemu', 'netemu', 'vsh']")
source = source.replace("ROOT/'local_only'/'ghidra'/'p0d'", "ROOT/'local_only'/'analysis'/'p0g'/'ghidra'")
source = source.replace("ROOT/'local_only'/'analysis'/'p0d'/args.variant", "ROOT/'local_only'/'analysis'/'p0g'/args.variant")
source = source.replace("ROOT/'local_only'/'variants'/(args.variant+'.elf')", "ROOT/'local_only'/('stock.elf' if args.variant == 'netemu' else 'fw355/out/'+args.variant+'.elf')")
source = source.replace("descriptors = {}", "if args.variant == 'vsh': toc = 0x6f7370\ndescriptors = {}")
source = source.replace("entry, candidate = struct.unpack_from('>QQ', binary, pos)", "entry, candidate = struct.unpack_from('>II' if args.variant == 'vsh' else '>QQ', binary, pos)")
source = source.replace("for pos in range(off, off+size-16, 8):\n        entry, candidate", "for pos in range(off, off+size-16, 4 if args.variant == 'vsh' else 8):\n        entry, candidate")
# Recover all function bodies in the requested driver range, including direct
# internal entries without descriptors, after the base analyzer has run.
source = source.replace("targets.update(n for n in entries if low <= n < high)", "targets.update(int(f.getEntryPoint().getOffset()) for f in fm.getFunctions(True) if low <= int(f.getEntryPoint().getOffset()) < high)")
exec(compile(source, str(ROOT / 'tools' / 'p0d_ghidra.py'), 'exec'))
