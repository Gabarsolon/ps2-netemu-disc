"""Independent offline receipts/final report. Never starts a JVM or hardware."""
from pathlib import Path
import ast,hashlib,json,runpy,struct,re
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'local_only/owned_control'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text())
def dump(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2)+'\n')
def main():
    r=read('build_review.json');pc=read('pc_results.json');inputs=read('input_review.json')
    assert pc['status']=='PASS' and pc['jvm_done'] and pc['elf_sha256']==r['elf_sha256']
    assert pc['compiled_store_site_coverage']['missing']==[]
    assert pc['counts']['real_sc_executed']==0 and pc['original_before']==pc['original_after']==r['stock_elf_sha256']
    for rel,info in inputs['complete_evidence_read_and_hashes'].items():assert sha(ROOT/rel)==info['sha256'],rel
    for rel,digest in r['source_inputs'].items():assert sha(ROOT/rel)==digest,rel
    for c in pc['calls']:
        assert c['abi_preserved'] and c['irq_restored'] and c['original_result_preserved']
        if c['kind']=='startup':assert c['original_calls']==1 and c['allocator_calls']<=1
        if c['kind']=='refresh':assert c['allocator_calls']==0 and not {'open','stat','write','close'}&set(c['calls'])
        if c['kind']=='shutdown':
            assert c['original_calls']==1 and c['allocator_calls']==0
            for op in ('open','stat','write','close'):assert c['calls'].count(op)<=1
    elf=OUT/'ps2_netemu_owned_control.elf';self_file=OUT/'ps2_netemu_owned_control.self'
    assert sha(elf)==r['elf_sha256'] and sha(self_file)==r['self_sha256']
    assert elf.read_bytes()==self_file.with_suffix('.roundtrip.elf').read_bytes()
    assert sha(ROOT/'local_only/stock.elf')==r['stock_elf_sha256']
    assert sha(ROOT/'local_only/stock_ps2_netemu.self')==r['stock_self_sha256']
    stock=(ROOT/'local_only/stock.elf').read_bytes();patched=elf.read_bytes()
    def phdrs(b):
        off=struct.unpack_from('>Q',b,32)[0]
        return [struct.unpack_from('>IIQQQQQQ',b,off+56*i) for i in range(struct.unpack_from('>H',b,56)[0])]
    ph=phdrs(stock);assert ph==phdrs(patched) and len(stock)==len(patched)
    def off(a):return next(p[2]+a-p[3] for p in ph if p[0]==1 and p[3]<=a<p[3]+p[5])
    bounds=[(off(0x4800),off(0x4800)+int(r['code_end'],16)-0x4800)]+[(off(a),off(a)+4) for a in (0xbc168,0x11243c,0x18cb4)]
    differences=[i for i,(a,b) in enumerate(zip(stock,patched)) if a!=b]
    assert all(any(lo<=i<hi for lo,hi in bounds) for i in differences)
    assert patched[off(0x112444):off(0x112444)+4]==stock[off(0x112444):off(0x112444)+4]
    verification=read('ps2_netemu_owned_control.verification.json')
    assert verification['selfdec_roundtrip_exact'] and all(s['hmac_sha1_verified'] and s['payload_exact'] for s in verification['sections'])
    assert read('ir_store_audit.json')['status']=='PASS_BOUNDED_STORE_POINTERS'
    assert read('assembly_store_audit.json')['status']=='PASS_ALL_STORE_WORDS_MATCH_BOUNDED_IR_TRANSLATION'
    assembly=(OUT/'payload_compiler.s').read_text()
    assert not re.search(r'^\s*(?:sc|mtmsr\w*|dcb\w*|icbi|tlbi\w*|slbi\w*)\b',assembly,re.M)
    # Validate the decoder on actual compiled-PPC output and independently
    # corrupt schema, publication, lease, checksums, UI, stat and reserved bytes.
    decoder=runpy.run_path(str(HERE/'decode_snapshot.py'))['decode']
    sample=(OUT/'pc_success_snapshot.bin').read_bytes();decoded=decoder(sample)
    assert decoded['status']=='owned' and decoded['pattern_pass']
    dump('decoded_pc_snapshot.json',decoded)
    declined=decoder((OUT/'pc_declined_snapshot.bin').read_bytes())
    assert declined['owned_pointer'] is None and declined['allocator_return']==hex((1<<64)-1-0x1000)
    dump('decoded_pc_declined.json',declined)
    rejected=0
    for index in (0,1,2,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,54,55,61,62,63):
        data=bytearray(sample);value=struct.unpack_from('>Q',data,index*8)[0]
        # Some enum/pattern/flag corruption must use a meaningful invalid value.
        replacement=(8 if index==55 else 0 if index in (2,4,5,14,15,20,21,22,23,24,25,26,27,28,29,30,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,54,61) else value^1)
        if replacement==value:replacement=value^1
        struct.pack_into('>Q',data,index*8,replacement)
        try:decoder(bytes(data))
        except ValueError:rejected+=1
        else:raise AssertionError(('decoder accepted malformed field',index))
    # Neither helper version nor game/disc content is written to source dirs.
    for p in HERE.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
    sources={str(p.relative_to(ROOT)):sha(p) for p in HERE.rglob('*') if p.is_file()}
    external=[ROOT/'experiments/netemu_autoreturn/ppcasm.py',ROOT/'experiments/netemu_autoreturn/resign_self_installed.py',
        ROOT/'experiments/netemu_autoreturn/selfdec.py',
        Path('C:/Users/remus/ps3buzz-console/raw_capture_debug11/dependencies/dl/key_vault.cpp')]
    external_hashes={str(p):sha(p) for p in external}
    tool_paths=[Path('C:/Program Files/LLVM/bin')/n for n in ('clang.exe','ld.lld.exe','llvm-objcopy.exe')]
    tool_paths.append(Path('E:/tools/ps3dk/ps3-sdk-v0.26.0-windows-x86_64/ppu/bin/powerpc64-ps3-elf-as.exe'))
    tool_hashes={str(p):sha(p) for p in tool_paths}
    artifacts={str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file() and p.suffix in ('.elf','.self','.bin','.ll','.s','.o')}
    history=[dict(jvm=1,status='HARNESS_STOPPED',jvm_done=True,reason='sync CALLOTHER unsupported; JVM closed and process exited1 before next start'),
        dict(jvm=2,status='PASS_SUPERSEDED',cases=177,reason='Earlier object/assembly emissions differed; exact-listing build replaced it',jvm_done=True),
        dict(jvm=3,status='PASS_SUPERSEDED',cases=194,reason='Exact-listing build/read fences passed; final schema then retained the opaque rejected allocator return',jvm_done=True),
        dict(jvm=4,status='PASS_FINAL',suite_attempts=pc['suite_attempts'],jvm_done=True)]
    final=dict(status='PASS_OFFLINE',hardware='NOT RUN',all_jvms_done=True,jvm_slot_released=True,
        sequential_jvm_processes=4,max_simultaneous_jvms=1,jvm_history=history,
        cases=pc['counts']['cases'],pc_counts=pc['counts'],store_site_coverage=pc['compiled_store_site_coverage'],
        source_inputs=sources,external_source_inputs=external_hashes,artifact_sha256=artifacts,
        tool_inputs=tool_hashes,no_added_sc_raw_msr_write_cache_or_mapping_instruction=True,
        parsed_all_python_sources=True,decoder_positive=2,decoder_negative_fields=rejected,
        input_evidence_unchanged=True,stock_unchanged=True,patch_only_slot_and_three_words=True,
        no_segment_extension=True,subsequent_flush_unchanged=True,exact_self_decrypt_hmac=True,
        limitations=['B9D54/native refresh/native shutdown/UFS/context/trap boundaries are modeled explicitly.',
            'sync words are verified/counted, not a cache/SMP/memory-order simulation.',
            'PR1 rejection tests model a context-read return, not execution of privileged mfmsr in PR1.',
            'Cold startup other-thread exclusion is source-supported inference, no scheduler model/global lock.',
            'Supplied live P/E are samples; fresh A here is actual PPC allocation on an offline synthetic pool fixture.',
            'No optical read, DMA, cache attribute/visibility, hardware behavior, bounded UFS wait or durable delivery is established.'])
    dump('final_checks.json',final)
    r.update(status='PASS_OFFLINE_HARDWARE_NOT_RUN',ppc_validation=dict(status='PASS',counts=pc['counts'],
        result_sha256=sha(OUT/'pc_results.json')),source_inputs=sources,external_source_inputs=external_hashes,
        tool_inputs=tool_hashes,
        generated_assembly_sha256=sha(OUT/'payload_compiler.s'),jvm_slot_released=True,
        assembler='GNU PowerPC64 PS3 binutils2.42; ELFv2 from .abiversion2; CPU970 LLVM generation',
        all_store_sites_exercised=True,final_checks_sha256=sha(OUT/'final_checks.json'))
    dump('build_review.json',r)
    report=f'''# Owned-memory control — offline result

**PROVEN on PC: PASS, {pc['counts']['cases']} final cases. Hardware NOT RUN.**
All JVMs closed; the exclusive slot is released. Four JVM processes ran
sequentially, never concurrently. See final_checks.json for honest attempt history.

Fresh8KiB B9848 ownership, native first-fit allocation, independent command/data
LPAR translation, retained lifetime, bounded pattern writes, declined snapshots,
native-first timer and original-first startup/shutdown all passed the actual
compiled-PPC checks under the explicitly modeled boundaries. The startup body
B9D54 itself is modeled; its post-return fixture comes from actual stock lazy
initialization and stock23D0/18 allocations. No allocator-result stub supplies
the valid ownership path. Deliberately altered returns are labeled fault injection.

Native metadata/stack stores and our mailbox/reason/owned stores have separate
fences. Every compiled payload store site was exercised. IR bounds cover every
store, and assembly operands were checked against the exact linked words.
The build assembles the reviewed LLVM listing with GNU as: separate LLVM
object/assembly emissions were found to choose different register allocations.
The earlier passing177-case binary is preserved under pre_final/ and is superseded.

Final code: {r['code_bytes']} bytes, [4800,{r['code_end']}); no segment extension,
data or BSS. Only that slot and the three guarded hook words changed. Stock
112444->12D420 remains untouched. ELFv2 BE970 freestanding Oz; native TOC751280.
Fresh-return equality uses the admitted first-fit prediction; a contained stale
address cannot be initialized as a fresh allocation. Pointer seals precede heap
reads. Validated retained addresses are kept locally for dependent pattern reads.

Final cases include both outer EE states and primary h0/h1, all26 corrupt heap
classes, maximal physically possible exact-fit/split counts, B4091 no-fit,
fragmentation, wrong contexts/epoch/flags, failed and altered returns, foreign
and partial publication, timer/UI/HDD/session/publication races, retained block
disjointness, bounded reads/writes, one-shot exit, owned/declined file faults.
Only verified trap5/6 SC sites are modeled; zero real SC instructions executed.
The admitted native helper takes precisely22 PCs and writes only H+20.
No growth/removal/free/retry path is certified or used.

OWNSEC1 schema and decoder are in the source README/header. The actual PPC
snapshot decodes correctly; {rejected} malformed field tests are rejected.
State and command/data samples contain our initialized patterns only, no disc
or stale heap bytes. The precreated65536-byte file must be supplied by the parent
before any later console test; this task did not access or create it on hardware.

**INFERRED:** the supplied normal cold-start handshake provides other-thread
exclusion until18D8C, while outer trap5/6 closes the local interrupt interval.
This is not a global lock or an arbitrary warm-reentry contract. h is derived
from SPR088 bit30; primary entry requires its signed low word negative.

**UNKNOWN / not established:** real fresh allocation at this new checkpoint,
hardware behavior of this build, cache attributes/visibility, physical-sector
delivery, DMA, optical acceptance, cold-cache UFS liveness, native-helper hard
deadlines and durable snapshot delivery. mfmsr/SPR088 and sync are explicit
emulator boundaries; wrongPR is a modeled returned context value, not PR1
privileged-instruction execution. Native UFS still has unbounded waits. A
healthy carrier's live-proven normal return is not a general watchdog.

ELF SHA256: `{r['elf_sha256']}`

SELF SHA256: `{r['self_sha256']}`

C SHA256: `{sha(HERE/'src/owned.c')}`

All source/header/assembly and external input hashes, full PC receipts, exact
SELF decrypt/HMAC checks and original before/after hashes are in build_review.json,
final_checks.json, pc_results.json, input_review.json and the store audits.
Stock ELF/SELF and all supplied evidence recheck unchanged. No network,
hardware/device/console action, flash/install/game launch, driver/registry/
pairing/input/screenshot action, process termination, child agent or git mutation
occurred. All created text sources stay under experiments/netemu_owned_control/;
all generated binaries/reports stay under ignored local_only/owned_control/.
'''
    (OUT/'report.md').write_text(report,encoding='utf-8')
    print(json.dumps({k:v for k,v in final.items() if k not in ('source_inputs','external_source_inputs','artifact_sha256','limitations','jvm_history')},indent=2))
if __name__=='__main__':main()
