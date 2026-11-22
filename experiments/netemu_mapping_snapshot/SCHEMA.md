MAPSEC1 version 1 uses exactly 64 big-endian qwords (512 bytes). It is written
once at offset zero to the parent-precreated 65,536-byte regular file
`/tmp/netemu_mapping_snapshot.bin`. No create/truncate/flush/retry. Native
raw_write checks regular-file kind; the first native stat word is not a mode.
SNAPSEC1 is unchanged in the original experiment and is never overwritten.

| Qword | Meaning |
|---|---|
| 0 | `4d41505345433100` (`MAPSEC1` and NUL) |
| 1 | `0001000000000200`: version 1, byte length 512 |
| 2,3 | Terminal marker before consumption; shutdown timebase |
| 4,5,6 | Native object `b46100`, reason 2, preserved original 11B9BC result |
| 7 | Reserved zero |
| 8..19 | Exact 96-byte capture: original terminal marker then MAIL[1..11], same sampling/publication protocol as snapshot |
| 20..22 | Shutdown CDVD EA, size, LPAR at 2458428/30/38 |
| 23,24 | HTAB handle 930f98; byte size 930fb0 |
| 25..28 | First descriptor extent 934960, flags 934968, P 934970, E 934980 |
| 29..32 | Published E 24565b8; payload 2446588; heap H+28 = 2446588 (intentionally redundant same word); sentinel 24565a0 |
| 33..35 | First bank head 2446568, first bank next 2446598, growth-marker attribute 2456568. Fixed metadata samples, no ownership/headroom proof |
| 36,37 | Stat size (must be 65536); fd 0..7 |
| 38,39 | Reserved zero |
| 40..47 | Captured CDVD mapping result |
| 48..55 | First heap pool mapping result |
| 56..63 | Reserved zero |

Each eight-qword mapping record:

| Relative qword | Meaning |
|---|---|
| 0 | Captured EA; never dereferenced |
| 1 | VSID virtual = EA-10000000 (zero for rejected tuple) |
| 2 | Expected primary V = ((virtual>>23)<<7)\|5; secondary V = primary\|2 |
| 3 | Primary group start in high 32 bits, secondary start in low 32 bits |
| 4 | Outcome: 0 invalid tuple; 1 bad HTAB; 2 changed HTAB/coverage failure; 3 syscall error; 4 absent; 5 ambiguous; 6 unique |
| 5 | Last call95 status, full 64 bits. Zero also means no call; see count |
| 6 | Query count high 32, exact-V match count low 32 (partial count on error) |
| 7 | Only for outcome 6: index high 32, low-R16 bits 31..16, WIMG=low-R16&78 bits 15..0. Otherwise FFFFFFFF00000000 |

Queries run only after original 11B9BC returns and fresh snapshot/reason/object/
HDD guards pass. Each valid target scans primary+0,+4 then secondary+0,+4,
four entries per call, at most eight calls total. Every call rechecks captured
native handle (zero uses the stock current-table lookup) and one of exact byte sizes 40000/80000/100000; postchecks also
reject a change during the last call. A failed call ends that target's scan;
its five outputs are not interpreted. A unique interpretation requires all
four calls and exactly one exact V match across both groups. Counts on errors
do not establish uniqueness. A scan across calls is not an atomic HTAB snapshot.

All segment-8 1MiB page formula cases are byte-checked against stock mapper
MD instructions in mapping_evidence.json, using a pure arithmetic model.
Those models are not compiled PPC execution or a real HV call. Full RPN/LPAR
identity, currently selected CPU SLB/TLB, cold UFS/IRQ liveness, cache visibility,
durability and physical-disc delivery remain UNKNOWN. Pool metadata is not an
allocation; P+(A-E) requires a future fresh owned A and is not used here.

The fixed call95 bridge takes handle/index and a compiler-proven local 40-byte
stack output, returns status, captures all five BE qwords r4..r8 and preserves
SP/LR/TOC/CR/r31. Other nonvolatile registers are untouched. Its syscall is
exactly `li r11,95; oris r11,r11,8000; sc 0`, matching stock forwarding.

Parent only, after checking the sole JVM is free:

```powershell
python -B experiments/netemu_mapping_snapshot/validate_pc.py --allow-jvm
```

Offline decode (no JVM):

```powershell
python -B experiments/netemu_mapping_snapshot/decode.py local_only/mapping_snapshot/netemu_mapping_snapshot.bin
```
