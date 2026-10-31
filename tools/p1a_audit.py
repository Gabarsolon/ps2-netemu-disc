"""Independent audit of a P1a build vs the stock ELF.
usage: python -I tools/p1a_audit.py local_only/stock.elf local_only/p1a/ps2_netemu_p1a.elf
Reports: changed byte ranges (by segment), every `sc` in changed/added code, every store (st*) in changed/added code with its base register.
"""
import struct, sys, hashlib
a = open(sys.argv[1], 'rb').read()
b = open(sys.argv[2], 'rb').read()
print('stock sha256', hashlib.sha256(a).hexdigest())
print('p1a   sha256', hashlib.sha256(b).hexdigest())
print('sizes', len(a), len(b))

def phdrs(d):
    off, = struct.unpack_from('>Q', d, 0x20)
    n, = struct.unpack_from('>H', d, 0x38)
    return [struct.unpack_from('>IIQQQQQQ', d, off + i * 0x38) for i in range(n)]

pa, pb = phdrs(a), phdrs(b)
for x in pb:
    print('p1a phdr type=%d flags=%d off=%#x va=%#x filesz=%#x memsz=%#x' % (x[0], x[1], x[2], x[3], x[5], x[6]))
for x in pa:
    print('stock phdr type=%d flags=%d off=%#x va=%#x filesz=%#x memsz=%#x' % (x[0], x[1], x[2], x[3], x[5], x[6]))

# changed ranges per stock LOAD segment (compare by vaddr)
def seg_bytes(d, ph):
    return {p[3]: d[p[2]:p[2] + p[5]] for p in ph if p[0] == 1}
sa, sb = seg_bytes(a, pa), seg_bytes(b, pb)
changed = []
for va, da in sa.items():
    db = sb.get(va)
    if db is None:
        print('segment %#x missing in p1a' % va); continue
    n = min(len(da), len(db))
    i = 0
    while i < n:
        if da[i] != db[i]:
            j = i
            while j < n and (da[j] != db[j] or (j + 1 < n and da[j + 1] != db[j + 1] and j - i < 64)):
                j += 1
            changed.append((va + i, va + j, db[i:j]))
            i = j
        else:
            i += 1
    if len(db) > len(da):
        changed.append((va + len(da), va + len(db), db[len(da):]))
print('changed ranges: %d' % len(changed))
tot = 0
for lo, hi, _ in changed:
    tot += hi - lo
print('total changed/added bytes: %d' % tot)
for lo, hi, _ in changed[:80]:
    print('  %#x..%#x (%d)' % (lo, hi, hi - lo))

# scan changed/added executable ranges for sc and stores
EXEC_LIMIT = 0x300000
stores = {0x90: 'stw', 0x94: 'stwu', 0x98: 'stb', 0x9C: 'stbu', 0xB0: 'sth', 0xB4: 'sthu', 0xD0: 'stfs', 0xD4: 'stfsu', 0xD8: 'stfd', 0xDC: 'stfdu'}
sc_list, st_list, other = [], [], []
# Changed ranges are bytewise and can cut words in half (zero bytes equal stock), so
# re-read every touched word, 4-byte aligned, from the new image.
words = set()
for lo, hi, data in changed:
    if lo >= EXEC_LIMIT:
        continue
    for va in range((lo // 4) * 4, hi, 4):
        words.add(va)
def seg_word(d, ph, va):
    for p in ph:
        if p[0] == 1 and p[3] <= va < p[3] + p[5]:
            return struct.unpack_from('>I', d, p[2] + va - p[3])[0]
    return None
for va in sorted(words):
    if True:
        w = seg_word(b, pb, va)
        if w is None:
            continue
        data = None; lo = va; k = 0
        if w & 0xFC000003 == 0x44000002:
            sc_list.append((va, (w >> 5) & 0x7F))
        op = w >> 26
        if op in (36, 37, 38, 39, 44, 45, 52, 53, 54, 55):
            st_list.append((va, w))
        if op == 62 and (w & 3) in (0, 1):  # std/stdu
            st_list.append((va, w))
        if op == 31 and ((w >> 1) & 0x3FF) in (151, 215, 407, 662, 149, 181, 247, 439, 695, 663, 727, 918):
            st_list.append((va, w))
print('sc instructions in changed/added executable ranges:', sc_list)
print('stores in changed/added executable ranges: %d' % len(st_list))
bases = {}
for va, w in st_list:
    op = w >> 26
    ra = (w >> 16) & 31
    bases.setdefault((op, ra), []).append(va)
for (op, ra), v in sorted(bases.items()):
    print('  op=%d base=r%d count=%d first=%#x' % (op, ra, len(v), v[0]))
