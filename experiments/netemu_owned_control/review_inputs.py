"""Read ALL required evidence, verify stock words/receipts; no JVM or devices."""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'local_only/owned_control'
REQUIRED=['docs/NETEMU_KNOWLEDGE.md','docs/GOAL_AND_PLAN.md','docs/OPEN_QUESTIONS.md',
    'docs/AUTOMATIC_SNAPSHOT_CONTROL.md','local_only/private_staging_review/report.md',
    'local_only/private_staging_review/helper_gate.json','local_only/private_staging_review/startup_serialization.md',
    'local_only/private_staging_review/startup_serialization_evidence.json','local_only/allocator_pc/report.md',
    'local_only/allocator_pc/check_allocator.py','local_only/allocator_pc/results.json',
    'local_only/allocator_pc/final_checks.json',
    'local_only/mapping_snapshot_console/console_20261122T162950Z/decoded_mapping_snapshot.json']
def main():
    sources={};values={}
    for rel in REQUIRED:
        p=ROOT/rel;b=p.read_bytes();t=b.decode('utf-8-sig')
        sources[rel]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':len(t.splitlines())}
        values[rel]=json.loads(t) if p.suffix=='.json' else t
    stock=(ROOT/'local_only/stock.elf').read_bytes()
    assert hashlib.sha256(stock).hexdigest()=='63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'
    ph=struct.unpack_from('>Q',stock,32)[0]
    seg=[struct.unpack_from('>IIQQQQQQ',stock,ph+56*i) for i in range(struct.unpack_from('>H',stock,56)[0])]
    def rd(a,n):
        return next(stock[p[2]+a-p[3]:p[2]+a-p[3]+n] for p in seg if p[0]==1 and p[3]<=a and a+n<=p[3]+p[5])
    instructions=0
    for rel in ['local_only/private_staging_review/helper_gate.json','local_only/private_staging_review/startup_serialization_evidence.json']:
        for row in values[rel]['instructions']:
            assert rd(int(row['address'],16),4).hex()==row['word'];instructions+=1
    a=values['local_only/allocator_pc/results.json'];f=values['local_only/allocator_pc/final_checks.json']
    assert a['status']=='PASS' and a['jvm_done'] and f['all_jvms_done'] and f['status']=='PASS'
    helper=values['local_only/private_staging_review/helper_gate.json']['single_bank_gate']['helper_path_pcs']
    calls=a['calls'];alloc=[x for x in calls if x['entry']=='0xb9848']
    assert len(alloc)==43 and len(a['rejected'])==26
    for c in alloc:assert c['helper_pcs']==helper and c['helper_only_write_H20'] and c['abi_preserved']
    m=values[REQUIRED[-1]]['metadata']
    assert m['pool LPAR P']=='0x3b00000' and m['pool CPU EA E']=='0x80000000'
    assert m['HTAB handle']==m['HTAB bytes']=='0x0'
    # Exhaust every physically possible aligned placement, independent of C.
    placements=[]
    for aa in range(0x80020000,0x80060000-8192+1,64):
        cc=(aa+0x107f)&~127;dd=cc+128;p=0x3b00000;e=0x80000000
        assert aa+4096<=cc<cc+64<=dd<dd+2048<=aa+0x18c0<=aa+8192
        assert cc%128==dd%128==(p+cc-e)%128==(p+dd-e)%128==0
        assert p+0x20000<=p+aa-e<p+dd-e+2048<=p+0x60000
        placements.append(aa)
    assert len(placements)==3969
    report=dict(status='PASS',complete_evidence_read_and_hashes=sources,stock_instruction_words_verified=instructions,
        previous_native_allocator_calls_verified=len(alloc),previous_rejected_classes=26,
        placement_cases=len(placements),P='0x3b00000',E='0x80000000',
        live_P_E_scope='Supplied mapping snapshot sample only; no fresh allocation or cache attribute proof.',
        count_bound=dict(exact_fit_max_B=3969,split_max_B=3968,B4091_largest_block_units=6),
        no_network_hardware=True,no_jvm=True)
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'input_review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='complete_evidence_read_and_hashes'},indent=2))
if __name__=='__main__':main()
