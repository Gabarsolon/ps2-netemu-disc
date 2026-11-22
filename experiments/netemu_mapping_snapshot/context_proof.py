"""Pure Python evidence from existing stock listings/ELF; never starts a JVM."""
from pathlib import Path
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'local_only/mapping_snapshot'
SHA = '63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3'

def prove():
    b = (ROOT/'local_only/stock.elf').read_bytes()
    assert hashlib.sha256(b).hexdigest() == SHA
    ph = struct.unpack_from('>Q', b, 32)[0]
    seg = [struct.unpack_from('>IIQQQQQQ', b, ph+56*i)
           for i in range(struct.unpack_from('>H', b, 56)[0])]
    def rd(a, n):
        return next(b[p[2]+a-p[3]:p[2]+a-p[3]+n] for p in seg
                    if p[0] == 1 and p[3] <= a and a+n <= p[3]+p[5])
    files = ['normal_exit_analysis/stock_111e6c.asm',
             'normal_exit_analysis/stock_112100.asm',
             'normal_exit_analysis/stock_123b24.asm',
             'normal_exit_analysis/stock_11b700.asm',
             'analysis/fn_00017324.asm', 'analysis/fn_001ecc5c.asm',
             'analysis/fn_001ecb10.asm', 'analysis/fn_001ec760.asm',
             'analysis/fn_001ed458.asm', 'analysis/fn_001ec084.asm',
             'analysis/fn_001ebb70.asm', 'analysis/fn_001eb780.asm',
             'analysis/fn_0012d0ac.asm', 'analysis/fn_0012ce80.asm']
    rows, hashes = {}, {}
    checked = []
    # Independent encoding checks for relevant loads/stores/immediates/branches.
    dops = {'addi':14, 'addis':15, 'ori':24, 'oris':25, 'lwz':32,
            'lbz':34, 'stw':36, 'stb':38, 'lhz':40, 'sth':44}
    for rel in files:
        data = (ROOT/'local_only'/rel).read_bytes()
        hashes[rel] = hashlib.sha256(data).hexdigest()
        for line in data.decode('utf-8-sig').splitlines():
            m = re.match(r'^([0-9a-f]{8}): (.*?)(?: ;.*)?$', line)
            if not m:
                continue
            pc, ins = int(m[1],16), m[2]
            rows[pc] = ins
            word = int.from_bytes(rd(pc,4),'big')
            dm = re.fullmatch(r'(ld|std|stdu|lwz|lbz|stw|stb|lhz|sth) r(\d+),(-?0x[0-9a-f]+)\(r(\d+)\)',ins)
            bm = re.fullmatch(r'(b|bl) 0x([0-9a-f]+)',ins)
            im = re.fullmatch(r'(addi|addis|ori|oris) r(\d+),r(\d+),(-?0x[0-9a-f]+)',ins)
            lm = re.fullmatch(r'(li|lis) r(\d+),(-?0x[0-9a-f]+)',ins)
            expected = None
            if dm:
                op, rt, disp, ra = dm[1],int(dm[2]),int(dm[3],16),int(dm[4])
                code = 58 if op == 'ld' else 62 if op in ('std','stdu') else dops[op]
                expected = code<<26 | rt<<21 | ra<<16 | (disp & 0xffff)
                if op == 'stdu': expected |= 1
            elif im:
                op, rt, ra, imm = im[1],int(im[2]),int(im[3]),int(im[4],16)
                if op in ('ori','oris'): rt,ra = ra,rt
                expected = dops[op]<<26 | rt<<21 | ra<<16 | (imm & 0xffff)
            elif lm:
                expected = (14 if lm[1]=='li' else 15)<<26 | int(lm[2])<<21 | (int(lm[3],16)&0xffff)
            elif bm:
                expected = 0x48000000 | ((int(bm[2],16)-pc)&0x3fffffc) | (bm[1]=='bl')
            if expected is not None:
                assert word == expected, (hex(pc),ins,hex(word),hex(expected))
                checked.append(pc)
    required = {
        0x111e94:'stb r0,0x100(r9)', 0x111ea0:'std r11,0x0(r9)',
        0x112428:'bl 0x00111e6c', 0x11243c:'bl 0x0011b9bc',
        0x112444:'bl 0x0012d420', 0x11bbd4:'bl 0x001ecc5c',
        0x11bdcc:'bl 0x001ed458', 0x11bde0:'bl 0x001ecb10',
        0x11bb90:'bl 0x001ed458', 0x11bb9c:'bl 0x001ecb10',
        0x1ed594:'stw r0,0x0(r31)', 0x1ecc2c:'stw r0,0x0(r31)',
        0x12d18c:'bl 0x00118a90', 0x12d21c:'rlwinm r3,r25,0x9,0x0,0x16',
        0x180bc:'std r9,0x148(r8)', 0x180c4:'std r11,0x150(r8)',
        0x18934:'std r0,0xa98(r31)', 0x18940:'std r8,0xa80(r31)',
    }
    for pc, ins in required.items(): assert rows[pc] == ins, (hex(pc),rows.get(pc))
    assert rd(0x11243c,4).hex() == '48009581'
    assert int.from_bytes(rd(0x749668,8),'big') == 0x722d20
    assert int.from_bytes(rd(0x722d20,8),'big') == 0x123b70
    # Startup loop: index 6 gets +0xc0000; next index 7 gets 4<<18.
    stack_lo = (0xaaa<<32) | 0x70000000 | (4<<18)
    stack_hi = stack_lo + 0x40000
    initial_sp = stack_hi - 0x200
    assert initial_sp % 16 == 0
    result = dict(status='PASS_STATIC_CONTEXT_PATTERN', stock_sha256=SHA,
        encoded_instruction_checks=len(checked), listing_sha256=hashes,
        critical_instructions={hex(pc):dict(text=rows[pc],word=rd(pc,4).hex()) for pc in required},
        stack=dict(context_index=7, entry='0x123b70', descriptor='0x722d20',
                   low=hex(stack_lo), high_exclusive=hex(stack_hi),
                   initial_sp=hex(initial_sp), bytes=0x40000,
                   shutdown_callsite_sp=hex(initial_sp-0x80-0x90)),
        interpretation='INFERRED from byte-checked startup and stock same-context UFS pattern; not runtime concurrency proof',
        quiescence='UNKNOWN', native_UFS_completion_deadline='UNBOUNDED',
        stat_kind='NOT established in 48-byte stat; native raw_write rejects nonregular inode through slot+4')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'context_proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

if __name__ == '__main__':
    r=prove()
    print(json.dumps({k:r[k] for k in ['status','encoded_instruction_checks','stack']},indent=2))
