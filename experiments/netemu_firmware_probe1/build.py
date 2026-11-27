"""Offline inert owned_control build. No JVM, git or device/console operations."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import struct
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'local_only/firmware_probe1'
TEMPLATE=ROOT/'experiments/netemu_autoreturn'
LLVM=Path('C:/Program Files/LLVM/bin')
ELF_SHA='63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'
SELF_SHA='bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a'
SLOT,END,CSTART=0x4800,0x7ff0,0x5000

def sha(b): return hashlib.sha256(b).hexdigest()
def phdrs(b):
    p=struct.unpack_from('>Q',b,32)[0]
    return [struct.unpack_from('>IIQQQQQQ',b,p+56*i) for i in range(struct.unpack_from('>H',b,56)[0])]
def vaoff(b,a):
    return next(p[2]+a-p[3] for p in phdrs(b) if p[0]==1 and p[3]<=a<p[3]+p[5])
def run(args):
    p=subprocess.run([str(x) for x in args],cwd=HERE,capture_output=True,text=True)
    with (OUT/'build.log').open('a',encoding='utf-8') as f:
        f.write(subprocess.list2cmdline([str(x) for x in args])+'\n'+p.stdout+p.stderr)
    assert p.returncode==0,p.stdout+p.stderr
def asm(source,pc):
    a=runpy.run_path(str(TEMPLATE/'ppcasm.py'))['Assembler'](pc)
    a.asm(source); return a.finish()
def trampoline(pc,target,toc):
    text=(f'mflr r0\nstd r0,16(r1)\nstdu r1,-128(r1)\nstd r2,120(r1)\n'
          f'lis r2,{(toc+0x8000)>>16}\naddi r2,r2,{((toc+0x8000)&65535)-32768}\n'
          f'lis r12,{(target+0x8000)>>16}\naddi r12,r12,{((target+0x8000)&65535)-32768}\n'
          f'bl {target}\nnop\nld r2,120(r1)\naddi r1,r1,128\nld r0,16(r1)\nmtlr r0\nblr\n')
    b,rows=asm(text,pc); assert len(b)<=64
    return b,rows

def build():
    # Read-only templates; no import of their build/validator scripts.
    assert 'local_only/' in (ROOT/'.gitignore').read_text(), 'private outputs must be ignored'
    stock=(ROOT/'local_only/stock.elf').read_bytes()
    template=(ROOT/'local_only/stock_ps2_netemu.self').read_bytes()
    assert sha(stock)==ELF_SHA and sha(template)==SELF_SHA
    assert stock[vaoff(stock,0xbc168):vaoff(stock,0xbc168)+4].hex()=='f821fec1'
    assert stock[vaoff(stock,0x11243c):vaoff(stock,0x11243c)+4].hex()=='48009581'
    assert not any(stock[vaoff(stock,SLOT):vaoff(stock,SLOT)+END-SLOT])
    assert not any(stock[vaoff(stock,0x930f20):vaoff(stock,0x930f20)+96])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'tmp').mkdir(exist_ok=True)
    for key in ('TMP','TEMP','TMPDIR'): os.environ[key]=str(OUT/'tmp')
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    assert stock[vaoff(stock,0x18cb4):vaoff(stock,0x18cb4)+4].hex()=='480a10a1'
    context=runpy.run_path(str(HERE/'context_proof.py'))['prove']()
    assert context['status']=='PASS_STATIC_CONTEXT_PATTERN'
    flags=['--target=powerpc64-unknown-linux-gnu','-mcpu=970','-mbig-endian',
           '-mabi=elfv2','-mno-altivec','-mno-vsx','-msoft-float','-ffreestanding',
           '-fno-builtin','-fno-stack-protector','-fno-pic','-fno-asynchronous-unwind-tables',
           '-fno-unwind-tables','-Oz','-fno-vectorize','-fno-slp-vectorize',
           '-Wall','-Wextra','-Werror','-S','-emit-llvm']
    run([LLVM/'clang.exe',*flags,HERE/'src/owned.c','-o',OUT/'payload.ll'])
    ll=(OUT/'payload.ll').read_text().replace(', target_mem: none','')
    (OUT/'payload.ll').write_text(ll)
    auditors=runpy.run_path(str(HERE/'audit.py'))
    ir=auditors['audit_ir'](OUT/'payload.ll')
    import llvmlite.binding as llvm
    llvm.set_option('owned_control','-disable-ppc-ctrloops')
    llvm.initialize_all_targets(); llvm.initialize_all_asmprinters()
    m=llvm.parse_assembly(ll); m.verify()
    tm=llvm.Target.from_triple(m.triple).create_target_machine(cpu='970',features='-altivec,-vsx',reloc='static',codemodel='small',abiname='elfv2')
    (OUT/'payload_compiler.s').write_text(tm.emit_assembly(m))
    # Assemble the SAME reviewed listing that is linked/executed. Independent
    # emit_object/emit_assembly runs can choose different register allocations.
    run([Path('E:/tools/ps3dk/ps3-sdk-v0.26.0-windows-x86_64/ppu/bin/powerpc64-ps3-elf-as.exe'),
         '-m64','-mbig','-mppc64',OUT/'payload_compiler.s','-o',OUT/'payload.o'])
    assert struct.unpack_from('>I',(OUT/'payload.o').read_bytes(),48)[0]==2
    linker='''OUTPUT_FORMAT(elf64-powerpc)
ENTRY(owned_refresh)
SECTIONS {
 . = 0x5000;
 .text : { *(.text .text.*) }
 .rodata : { *(.rodata .rodata.*) }
 . = ALIGN(8);
 .toc : { *(.toc .toc.*) }
 .data : { *(.data .data.*) }
 .bss : { *(.bss .bss.*) *(COMMON) }
 /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
native_refresh = 0x4840;
native_clock = 0x4880;
native_shutdown = 0x4900;
stock_ufs_open = 0x4940;
stock_ufs_stat = 0x4980;
stock_raw_write = 0x49c0;
stock_ufs_close = 0x4a00;
native_startup = 0x4b40;
native_repo_enum = 0x4a40;
native_repo_devid = 0x4a80;
native_repo_busid = 0x4d60;
native_alloc = 0x4b80;
irq_save = 0x4bc0;
irq_restore = 0x4c00;
read_msr = 0x4c40;
read_pir = 0x4c50;
lv1_open_device = 0x4c60;
lv1_close_device = 0x4ca0;
lv1_event_rx_port = 0x4ce0;
lv1_connect_irq_event = 0x4d20;
lv1_alloc_dma = 0x4da0;
lv1_map_dma = 0x4de0;
lv1_storage_read = 0x4e20;
lv1_get_async_status = 0x4e60;
dcache_flush = 0x4ea0;
'''
    (OUT/'link.ld').write_text(linker)
    run([LLVM/'ld.lld.exe','-m','elf64ppc','-T',OUT/'link.ld','--no-undefined',
         '--Map='+str(OUT/'payload.map'),OUT/'payload.o','-o',OUT/'payload.elf'])
    from elftools.elf.elffile import ELFFile
    with (OUT/'payload.elf').open('rb') as f:
        pe=ELFFile(f)
        syms={s.name:s['st_value'] for s in pe.get_section_by_name('.symtab').iter_symbols()}
        for name in ('.data','.bss','.sdata','.sbss','.opd'):
            sec=pe.get_section_by_name(name); assert sec is None or sec['sh_size']==0,name
        assert all(CSTART<=s['sh_addr']<s['sh_addr']+s['sh_size']<=END for s in pe.iter_sections() if s['sh_flags']&2 and s['sh_size'])
    run([LLVM/'llvm-objcopy.exe','-O','binary',OUT/'payload.elf',OUT/'payload.bin'])
    code=bytearray(CSTART-SLOT)+(OUT/'payload.bin').read_bytes()
    entries=[('entry_refresh',0x4800,syms['owned_refresh'],syms['.TOC.']),
             ('native_refresh',0x4840,0x4ac0,0x751280),('native_clock',0x4880,0xb9cd0,0x751280),
             ('entry_shutdown',0x48c0,syms['owned_shutdown'],syms['.TOC.']),
             ('native_shutdown',0x4900,0x11b9bc,0x751280),
             ('stock_ufs_open',0x4940,0x1ecc5c,0x751280),('stock_ufs_stat',0x4980,0x1ec760,0x751280),
             ('stock_raw_write',0x49c0,0x1ed458,0x751280),('stock_ufs_close',0x4a00,0x1ecb10,0x751280),
             ('native_startup',0x4b40,0xb9d54,0x751280),
             ('native_alloc',0x4b80,0xb9848,0x751280),
             ('irq_save',0x4bc0,0x11a604,0x751280),
             ('irq_restore',0x4c00,0x11a5f8,0x751280),
             # Firmware-route probe 7a/7b: netemu's repository enumerator + dev-id
             # extractor (read the repository via forwarded sc0 internally; no
             # hardware). r2=TOC set by the trampoline.
             # native_repo_enum(bus_type,dev_type,idx,&o1,&o2)->found;
             # native_repo_devid(o1,o2)->numeric dev_id (the storage_read id arg).
             ('native_repo_enum',0x4a40,0x1e9ba0,0x751280),
             ('native_repo_devid',0x4a80,0x1ea1e8,0x751280),
             ('native_repo_busid',0x4d60,0x1ea240,0x751280)]
    listing=[]
    for name,pc,target,toc in entries:
        block,rows=trampoline(pc,target,toc)
        code[pc-SLOT:pc-SLOT+len(block)]=block
        listing.extend(rows); syms[name]=pc
    reloc,rows=asm('stdu r1,-320(r1)\nb 0xbc16c\n',0x4ac0)
    assert reloc[:4]==bytes.fromhex('f821fec1')
    code[0x2c0:0x2c8]=reloc; listing.extend(rows)
    # Ninth C argument carries the exact incoming continuation, preserving r3..r10.
    block,rows=trampoline(0x4b00,syms['owned_startup'],syms['.TOC.'])
    source='\n'.join(r['op']+' '+','.join(r['args']) for r in rows)
    source=source.replace('stdu r1,-128(r1)','stdu r1,-128(r1)\nstd r0,96(r1)')
    block,rows=asm(source,0x4b00)
    assert len(block)==64
    code[0x300:0x340]=block; listing.extend(rows); syms['entry_startup']=0x4b00
    # Checked leaf mfmsr / SPR088: only reads, no raw MSR writes.
    for name,pc,word in [('read_msr',0x4c40,0x7c6000a6),('read_pir',0x4c50,0x7c6822a6)]:
        code[pc-SLOT:pc-SLOT+8]=struct.pack('>II',word,0x4e800020)
        listing.extend([dict(address=pc,word=f'{word:08x}',op=name,args=[]),dict(address=pc+4,word='4e800020',op='blr',args=[])])
        syms[name]=pc
    # Firmware-route probe: LV1 hypercall wrappers via netemu's FORWARDED guest-sc
    # bridge (li r11,N; oris r11,r11,0x8000; sc 0) -- the exact convention netemu's
    # own device code uses (e.g. fn_0012be04 HDD open). Riding the bridge means the
    # call is already authorized by netemu's guest kernel (open_device is whitelisted,
    # the HDD uses it), so the probe should NOT need the live LV1 patch A that a bare
    # sc 1 required. We still preserve LR+CR across the sc in a 128-byte frame (the
    # bridge is a guest call that may clobber volatiles). Args in r3.. (ELFv2); ret r3.
    for name,pc,num in [('lv1_open_device',0x4c60,170),('lv1_close_device',0x4ca0,171),
                        ('lv1_connect_irq_event',0x4d20,197)]:
        source=(f'mflr r0\nstd r0,16(r1)\nstdu r1,-128(r1)\nmfcr r12\nstd r12,120(r1)\n'
                f'li r11,{num}\noris r11,r11,0x8000\nsc 0\nld r12,120(r1)\nmtcr r12\naddi r1,r1,128\n'
                f'ld r0,16(r1)\nmtlr r0\nblr\n')
        block,rows=asm(source,pc); assert len(block)<=64 and pc+len(block)<=CSTART
        code[pc-SLOT:pc-SLOT+len(block)]=block
        listing.extend(rows); syms[name]=pc
    # construct_event_receive_port (18): 0-in; HV returns status r3 + port r4.
    # The stub returns the PORT (mr r3,r4) so the C payload can feed it to 197.
    for name,pc,num in [('lv1_event_rx_port',0x4ce0,18)]:
        source=(f'mflr r0\nstd r0,16(r1)\nstdu r1,-128(r1)\nmfcr r12\nstd r12,120(r1)\n'
                f'li r11,{num}\noris r11,r11,0x8000\nsc 0\nmr r3,r4\nld r12,120(r1)\nmtcr r12\n'
                f'addi r1,r1,128\nld r0,16(r1)\nmtlr r0\nblr\n')
        block,rows=asm(source,pc); assert len(block)<=64 and pc+len(block)<=CSTART
        code[pc-SLOT:pc-SLOT+len(block)]=block
        listing.extend(rows); syms[name]=pc
    # allocate_device_dma_region (174): 5-in (bus,dev,size,a,b); HV returns status r3
    # + dma bus address r4. The stub returns the DMA ADDRESS (mr r3,r4); a 0 return =
    # alloc failed (store audit forbids writing to a caller-supplied out pointer).
    for name,pc,num in [('lv1_alloc_dma',0x4da0,174)]:
        source=(f'mflr r0\nstd r0,16(r1)\nstdu r1,-128(r1)\nmfcr r12\nstd r12,120(r1)\n'
                f'li r11,{num}\noris r11,r11,0x8000\nsc 0\nmr r3,r4\nld r12,120(r1)\nmtcr r12\n'
                f'addi r1,r1,128\nld r0,16(r1)\nmtlr r0\nblr\n')
        block,rows=asm(source,pc); assert len(block)<=64 and pc+len(block)<=CSTART
        code[pc-SLOT:pc-SLOT+len(block)]=block
        listing.extend(rows); syms[name]=pc
    # map_device_dma_region (176): 6-in (bus,dev,lpar,dma,size,flags), status in r3.
    for name,pc,num in [('lv1_map_dma',0x4de0,176)]:
        source=(f'mflr r0\nstd r0,16(r1)\nstdu r1,-128(r1)\nmfcr r12\nstd r12,120(r1)\n'
                f'li r11,{num}\noris r11,r11,0x8000\nsc 0\nld r12,120(r1)\nmtcr r12\naddi r1,r1,128\n'
                f'ld r0,16(r1)\nmtlr r0\nblr\n')
        block,rows=asm(source,pc); assert len(block)<=64 and pc+len(block)<=CSTART
        code[pc-SLOT:pc-SLOT+len(block)]=block
        listing.extend(rows); syms[name]=pc
    # storage_read (245): 6-in (dev,2,lba,count,4,dma_buf); HV returns status r3 + tag
    # r4. PROBE 7h: the stub returns the STATUS r3 (no mr r3,r4) so the probe can
    # tell an accepted read (status 0) from a rejected one (region/dev/args). The
    # poll below is untagged (loops on async_result&0xffffff==0), so the tag is not
    # needed. 7f/7g already proved the chain "completes" with 0 bytes transferred.
    for name,pc,num in [('lv1_storage_read',0x4e20,245)]:
        source=(f'mflr r0\nstd r0,16(r1)\nstdu r1,-128(r1)\nmfcr r12\nstd r12,120(r1)\n'
                f'li r11,{num}\noris r11,r11,0x8000\nsc 0\nld r12,120(r1)\nmtcr r12\n'
                f'addi r1,r1,128\nld r0,16(r1)\nmtlr r0\nblr\n')
        block,rows=asm(source,pc); assert len(block)<=64 and pc+len(block)<=CSTART
        code[pc-SLOT:pc-SLOT+len(block)]=block
        listing.extend(rows); syms[name]=pc
    # get_async_status (249): 1-in (dev); HV returns status r3 + tag r4 + result r5.
    # The stub returns the RESULT (mr r3,r5); result & 0xffffff == 0 means complete.
    for name,pc,num in [('lv1_get_async_status',0x4e60,249)]:
        source=(f'mflr r0\nstd r0,16(r1)\nstdu r1,-128(r1)\nmfcr r12\nstd r12,120(r1)\n'
                f'li r11,{num}\noris r11,r11,0x8000\nsc 0\nmr r3,r5\nld r12,120(r1)\nmtcr r12\n'
                f'addi r1,r1,128\nld r0,16(r1)\nmtlr r0\nblr\n')
        block,rows=asm(source,pc); assert len(block)<=64 and pc+len(block)<=CSTART
        code[pc-SLOT:pc-SLOT+len(block)]=block
        listing.extend(rows); syms[name]=pc
    # Probe 7g: dcache_flush(addr=r3, lines=r4) -- hand-assembled, no stores, no
    # sub-calls, no sc. Invalidates `lines` 128-byte D-cache lines at addr so the
    # CPU readback of the DMA target is the device-written sector, not a stale
    # cached line. sync; mtctr r4; loop: dcbf 0,r3; addi r3,r3,128; bdnz loop;
    # sync; blr. dcbf is unprivileged; a clean line is only invalidated.
    pc=0x4ea0
    dc_words=[0x7c0004ac,  # sync
              0x7c8903a6,  # mtctr r4
              0x7c0018ac,  # dcbf 0,r3
              0x38630080,  # addi r3,r3,128
              0x4200fff8,  # bdnz -8 (back to dcbf)
              0x7c0004ac,  # sync
              0x4e800020]  # blr
    dc_ops=['sync','mtctr r4','dcbf 0,r3','addi r3,r3,128','bdnz -8','sync','blr']
    dc_block=b''.join(struct.pack('>I',w) for w in dc_words)
    assert pc+len(dc_block)<=CSTART
    code[pc-SLOT:pc-SLOT+len(dc_block)]=dc_block
    for i,(w,o) in enumerate(zip(dc_words,dc_ops)):
        listing.append(dict(address=pc+4*i,word=f'{w:08x}',op=o,args=[]))
    syms['dcache_flush']=pc
    aa=auditors['audit_assembly'](OUT/'payload_compiler.s',listing)
    # Own stack frames/trampolines are small compared with the traced 256KiB
    # control stack. Native helper depth/liveness retain their stock behavior.
    assert sum(aa['frames'].values())+3*128+320<8192
    final=bytearray(stock); off=vaoff(stock,SLOT)
    final[off:off+len(code)]=code
    hooks={0xbc168:'b 0x4800',0x11243c:'bl 0x48c0',0x18cb4:'bl 0x4b00'}
    for pc,source in hooks.items():
        patch,_=asm(source,pc); assert len(patch)==4
        final[vaoff(stock,pc):vaoff(stock,pc)+4]=patch
    assert len(final)==len(stock) and phdrs(final)==phdrs(stock)
    ranges=[(off,off+len(code))]+[(vaoff(stock,a),vaoff(stock,a)+4) for a in hooks]
    assert all(a==b or any(lo<=i<hi for lo,hi in ranges) for i,(a,b) in enumerate(zip(stock,final)))
    (OUT/'trampolines.json').write_text(json.dumps(listing,indent=2)+'\n')
    elf=OUT/'ps2_netemu_firmware_probe1.elf'; self_path=OUT/'ps2_netemu_firmware_probe1.self'
    elf.write_bytes(final)
    runpy.run_path(str(TEMPLATE/'resign_self_installed.py'))['main'](elf,self_path)
    assert self_path.with_suffix('.roundtrip.elf').read_bytes()==final
    review=dict(status='BUILT_OFFLINE_PARENT_VALIDATION_REQUIRED',stock_elf_sha256=ELF_SHA,stock_self_sha256=SELF_SHA,
        elf_sha256=sha(final),self_sha256=sha(self_path.read_bytes()),code_bytes=len(code),code_end=hex(SLOT+len(code)),
        source_sha256=sha((HERE/'src/owned.c').read_bytes()),source_inputs={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in str(p)},symbols=syms,frames=aa['frames'],
        context_proof_sha256=sha((OUT/'context_proof.json').read_bytes()),ir_audit=ir['status'],assembly_audit=aa['status'],
        only_slot_and_three_hooks_changed=True,segment_headers_unchanged=True,decrypt_roundtrip_exact=True,
        ppc_validation='PENDING: exclusive JVM authorized for this offline task',hardware='NOT RUN',
        risk='Native UFS waits remain unbounded. Neither watchdog recovery nor durable owned_control delivery is proven.')
    (OUT/'build_review.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(review,indent=2))

if __name__=='__main__': build()
