import subprocess, struct
from pathlib import Path
LLVM = Path(r'C:\Program Files\LLVM\bin')
c_code = """
unsigned long long get_tb(void) {
    unsigned long long tb;
    __asm__ volatile("mftb %0" : "=r"(tb));
    return tb;
}
"""
Path('tmp_tb.c').write_text(c_code)
flags = [
    '--target=powerpc64-unknown-linux-gnu', '-mcpu=970', '-mabi=elfv2',
    '-mno-altivec', '-mno-vsx', '-msoft-float', '-ffreestanding',
    '-O2', '-S', '-emit-llvm', 'tmp_tb.c', '-o', 'tmp_tb.ll'
]
res = subprocess.run([str(LLVM / 'clang.exe'), *flags], capture_output=True, text=True)
print('clang ret:', res.returncode)
if res.returncode != 0:
    print(res.stderr)
else:
    ll_text = Path('tmp_tb.ll').read_text().replace(', target_mem: none', '')
    import llvmlite.binding as llvm
    llvm.initialize_all_targets()
    llvm.initialize_all_asmprinters()
    mod = llvm.parse_assembly(ll_text)
    mod.verify()
    tm = llvm.Target.from_triple(mod.triple).create_target_machine(
        cpu='970', features='-altivec,-vsx', reloc='static', codemodel='small', abiname='elfv2'
    )
    obj = tm.emit_object(mod)
    asm_text = tm.emit_assembly(mod)
    print('Generated ASM:\n', asm_text)
    print('Compilation SUCCEEDED!')
Path('tmp_tb.c').unlink(missing_ok=True)
Path('tmp_tb.ll').unlink(missing_ok=True)
Path('tmp_tb.o').unlink(missing_ok=True)
