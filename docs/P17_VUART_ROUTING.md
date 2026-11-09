# P17: which ss_server1 code handles the netemu VUART `0x5005` request

Question (from P16 remaining investigation offline): which service instance/mapping
of `ss_server1` handles the VUART `0x5005` disc-auth request that
`ps2_netemu` sends, and can the P16 negative result be explained by structure
rather than by an exotic cause. Analysis is offline: fw 4.93 SS module ELFs
(`local_only/analysis/p0i/modules/`) and the two LV1 dumps
(`local_only/lv1_mem_<lo>_<hi>.bin`, windows encoded in the names).

Tools (this phase, `local_only/p16_service_context/`): `diff_lv1_vs_elf.py`
(window-aware, clip-safe), `elfphdrs.py`, `elfwords.py` (fixed VA mapping),
`dumpfind.py`, `dumpstrs.py`, `elfsearch.py` (verified correct), `callscan.py`,
`fnat.py`. Note: `elfwords.py` had a mapping bug during this phase; all numbers
below come from the fixed version plus `elfphdrs.py` cross-checks.

## PROVEN: op-class wiring of the service 0x5000 driver family

`ss_server1` registers its ops through a base constructor
`0x8000057C(obj, op, service)`: `obj[0]` = the 64-bit value at a per-op global
cell in the data segment (a `{0, vtable}` pair, so effectively the vtable),
`obj[1]` = op, `obj[2]` = service. Registered ops and their constructors:

- service 0x5000 (disc/optical family): `0x5001` (`0x8001C300`),
  `0x5002` (`0x8001C34C`), `0x5003` (`0x8001C390`), `0x5004` (`0x8001C3D4`),
  `0x5005` (`0x8001C418`), `0x5006` (`0x8001C500`), `0x5007` (`0x8001C45C`),
  `0x5008` (`0x8001C544`), `0x5009` (`0x8001C5A0`), `0x500A` (`0x8001C5E8`),
  `0x5010` (`0x8001C2B4`), `0x5011` (`0x8001C4AC`).
- one registration outside the family: op `0x25002`/service `0x25000`
  (`0x80000320`, sensor family).

Global cells live in the data segment (`0xC000E268..0xC000E2C8` region), each an
8-byte `{0, vtable}` pair:

| op | cell | vtable |
|---|---|---|
| 0x5004 | `0xC000E288` | `0x80058718` |
| 0x5005 | `0xC000E290` | `0x800586A8` |
| 0x5007 | `0xC000E298` | `0x80058638` |
| 0x5011 | `0xC000E2A0` | `0x800585C8` |
| 0x5006 | `0xC000E2A8` | `0x80058558` |
| 0x5008 | `0xC000E2B0` | `0x800584E8` |
| 0x5009 | `0xC000E2B8` | `0x80058478` |

(systematically: eight `0x70`-byte vtables from `0x80058478..0x80058788`; the
cells for ops 0x5001/0x5002/0x5010 map into lower members not individually
dumped here). Each vtable is a 64-bit-slot array of `{0, ptr}` pairs; slot
index 9 (byte offset +0x48) is the request-executor descriptor pointer.

The descriptors themselves are a static 24-byte-stride row array in the data
segment at `0xC00074A0`, row shape `{0, executor_fn, 0, 0xC0014CC0, 0, 0}`
(the `0xC0014CC0` pointer is beyond the module's own data end
`0xC0011340`, i.e. an LV1-global runtime object). Executor rows:

| row base | executor |
|---|---|
| `0xC00074A0` | `0x8001E6E8` |
| `0xC00074B8` | **`0x8001E724`** |
| `0xC00074D0` | **`0x8001E760`** |
| `0xC00074E8` | `0x8001E7CC` |

The serializer devices use the same row shape in `0xC000C060..0xC000C1A0`
(`0x8003D14C, 0x8003D180, 0x8003D1B4, 0x8003D1BC, 0x8003D1C8, 0x8003D214,
0x8003D26C, 0x8003D31C, 0x8003D408, 0x8003D458, 0x8003D4A0, 0x8003D4FC,
0x8003D590, 0x8003D7A0`); the P16-documented serializer `0x8003D31C` is the row
at `0xC000C108`.

## PROVEN: the two executors that matter for P16/P17

1. **op 0x5005**: ctor `0x8001C418` → cell `0xC000E290` → vtable
   `0x800586A8`, `vtable[9] = 0xC00074B8` → row executor `0x8001E724`.
   `0x8001E724` calls `0x80020638(ctx @0xC000E2C8, req 8-byte field at
   obj+0x38)` and stores the result word at obj+0x18 (the reply status).
   `0x80020638` is the auth helper: `/dev/rbd0` profile query
   (`(profile - 0xFF60) <= 1` branch at `0x80020710`, phys `0x714710`),
   INQUIRY product check (`0x8001F0E4`, patch site `0x8001F210`, phys
   `0x713210`), secure dispatch `0x8003220C(0xC, 0x38, req)`.

2. **op 0x5004**: ctor `0x8001C3D4` → cell `0xC000E288` → vtable
   `0x80058718`, `vtable[9] = 0xC00074D0` → row executor `0x8001E760`.
   `0x8001E760` is a *different op's* executor: if the req field equals
   `0x5A` it calls `0x80020BC8`, otherwise
   `0x800207E8(ctx @0xC000E2C8, req field as u32, &stack)`.
   `0x800207E8` branches on the sub-op id `0x1e/0x8d/0x29/4/0x46/0x52/0x2b/1..4`
   — matching the known op-0x5004 sub-ops (0x29 = reset/clean-key,
   0x46 = drive auth, 0x52 = PS2 insert policy).
   Call site `0x8001E7AC` sits inside `0x8001E760` (NOT inside `0x8001E724`;
   `callscan` finds no static bl/ba caller of `0x8001E760` anywhere — it is
   reached only through the descriptor slot).
   Phys mapping (base `0x6F4000`, seg1 static − `0x80000000` + `0x6F4000`):
   helper `0x800207E8` → `0x7147E8`; executor `0x8001E760` → `0x713760`;
   op-0x5005 helper `0x80020638` → `0x714638`; executor `0x8001E724` →
   `0x713724`.

Resident-copy corroboration: the static word `0xC00074B8` (vtable[9] of the
0x5005 object) appears in the RAM copy at file offset `0x4C6F4` → phys
`0x74C6F4` = `0x6F4000 + 0x586F4`, exactly static va `0x800586F4` = vtable[9]'s
hi-word. `0xC00074D4`/`0xC00074D0` words appear nowhere else statically and not
in either dump outside the vtables' own region.

## PROVEN: resident vs dump-1 state

- `diff_lv1_vs_elf.py lv1_mem_700000_800000.bin 0x6f4000 ss_server1`:
  **diff words 0, runs 0 over 79,684 words covered** (img `0xC000..0x59D10`,
  phys `0x700000..0x74DD10`). The first 48 KB (img `0..0xC000`, phys
  `0x6F4000..0x700000`) lies below the dump2 window start and is **not
  covered** by this proof (`ss_server1` text ends `0x80059D10`; covered text
  spans 311.3 of 359.3 KB).
- dump1 (`0x100000..0x300000`) contains **no byte-identical copy** of any
  tested module (all clipped full-segment diffs):

| candidate | diffs |
|---|---|
| `sysmgr_ss` @ `0xFB000` | 49,830 words / 1,370 runs (lots of zeros-vs-strings at window edge) |
| `ss_server1` @ `0x13828C` | 88,405 / 2,976 |
| `ss_server1` @ `0x15E028` | 87,364 / 3,983 |
| `ss_server2` @ `0x15E000` | 43,580 / 1,178 |
| `ss_server3` @ `0x165000` | 25,623 / 500 (misalignment of the 0x169000 copy) |
| `ss_server3` @ `0x169000` | 7,936 / 705, but img `0x4000..0x14000` fully clean (contains `vuart_received` `0x80006878` and the bind/listener `0x8000B444`) |

  The `0x169000` scan is therefore a real `ss_server3`-family image that is
  **not** the retail 4.93 text — version/origin UNKNOWN (see UNKNOWN).
- `SCE_CELLOSS_SS_SPM` is **absent from both dumps** (`dumpfind`, literal
  search) and absent from all 7 module ELFs (`elfsearch`). The old
  misoffset-read claims about a `SCE_CELLOSS_SS_SPM`/ACM region at
  "phys ~0x269000" were artifacts of the offset bug: with corrected tools that
  region (phys `0x268000..0x270000`) contains only code-like printable byte
  runs, and the string is nowhere in the dumps. Retracted as unattributable.

## INFERRED: the delivery path for netemu's 0x5005

From P16_SERVICE_CONTEXT / earlier ss_server3 analysis (re-stated with its
evidence class): `ss_server3` is the listener/router: dispatcher binds socket
port 0x25, `vuart_received` resolves function-id against the static port table
(`0xC0000600..0xC0000718`, `0x5005 → 0x51`, only populated there among the 7
ELFs) and connects/forwards. Among the dumped modules only `ss_server1`
implements op `0x5005`; no module carries a `0x51` immediate (the port is data
or runtime-assigned). Combining: **contextually, the netemu `0x5005` request
should be served by `ss_server1`'s op-0x5005 executor `0x8001E724` →
`0x80020638`**, which in the dumped copy is retail byte-identical.

## Reconciliation with the P16 console runs

- GameOS positive control: `syscall864(0x5004, 0x46)` produced
  `0x8001055a` after patching helper entry `0x7147E8`. This is exactly the
  op-0x5004 executor chain proven above (`0x8001E760 → 0x800207E8`), including
  the returned `0x5A` surviving object-store/serialization only in the
  GameOS-visible scalar path. Consistent, no conflict.
- netemu `0x5005` with the patched `0x80020638` entry (`0x714638`, `li r3,0x5a;
  blr`): reply still `0x0016` — the patched bytes did not affect the reply.
  Since the SAME dumped copy demonstrably executes for op 0x5004, the blanket
  "the whole instance differs" explanation is unlikely; remaining candidate
  causes, in increasing speculativity:
  1. **stale instruction-cache line** for the `0x80020638` helper (it likely
     executed before the patch — boot/early flows use it; GameOS's
     `0x800207E8` helper may have been cold-cache at patch time, which would
     explain why IT picked up the patch and `0x80020638` did not);
  2. the `0x5005` request is answered by a genuinely different serving entity
     that is not bound to port `0x51` in the dumped windows (see UNKNOWN);
  3. a different runtime code path through the op-0x5005 object (serialization
     reply re-use) that avoids the helper entirely —
     contradicted by `0x8001E724` being the only static caller of
     `0x80020638`, but runtime dispatch could differ.
  All three remain UNKNOWN offline; candidate (1) is the most parsimonious.

## UNKNOWN (each one names what would settle it)

- **Who binds port `0x51`** (the tenant that actually receives
  `0x5005` requests forwarded by `ss_server3`): the `0x300000..0x700000` LV1
  window is not dumped. A dump of that window with `dumpfind ss_server1
  text-mask` scan would show whether a second `ss_server1`-family copy (or
  another module) exists there; `diff_lv1_vs_elf.py` then settles identity.
- **dump1's `ss_server3`-family image at `0x169000`**: same-family but not
  retail-identical (7,936 differing words; clean 64 KB middle). Segment-2 data
  (the routing tables at `0xC0000600..`) was not diffed by the current script
  (text-segment only). A seg2-aware diff would show whether ITS
  function-id2port table also says `0x5005→0x51`, and whether the differing
  words are version drift or live patching.
- **ss_server1 seg2 resident state**: only the vtable[9] word is corroborated
  in RAM. A dump2 scan for the whole seg2 (phys base unknown) would verify
  object cells/descriptors/serializers match static values.
- **Meaning of `0xC0014CC0`** (LV1-global pointer inside each descriptor row)
  and the fastpath `0x80020BC8`; the executor rows `0x8001E6E8`/`0x8001E7CC`
  belong to sibling ops but were not decompiled.
- Whether I-cache staleness is the true cause; can only be bounded on the
  console (e.g., a different, demonstrably-cold address in the same helper, or
  an executor-entry stub `li r0,0x5a; stw r0,0x18(r3); li r3,1; blr` at
  `0x8001E724`/phys `0x713724` — proposed, not run; needs owner approval
  round).

## Proposed next steps (console-side, owner-executed, one at a time)

1. Extend `tools/ss1_auth_sentinel.py` to a **multi-target scan of RAM** for
   the `0x80020638` helper's distinctive words (not probe-fragile prologues) to
   enumerate every live copy of the auth path (answers "second instance?").
2. If only one copy exists, prefer the **executor-entry stub** at
   `0x8001E724` (phys `0x713724`: `3800005a 90030018 38600001 4e800020`) rather
   than re-patching the same helper entry — different instruction window, same
   code, so it also tests the I-cache hypothesis by changing a different line.
3. Request a dump of the `0x300000..0x700000` window (read-only) with the
   console idle-at-XMB to resolve the port-`0x51` tenant and the
 `0x169000` image's identity.

## Artifacts

- `C:\Users\remus\ps2-netemu-disc\local_only\p16_service_context\`: the fixed
  toolset and this phase's runs (`elfphdrs`, `elfwords`, `dumpfind`,
  `dumpstrs`, `diff_lv1_vs_elf` clip-safe output lines quoted above).
- Module ELFs (`local_only/analysis/p0i/modules/`), decompiles
  (`ss_server1/fn_8001c*.c`, `fn_8001e72*.c`, `fn_8001e76*.c`,
  `fn_80020638.c`, `fn_800207e8.c`, `fn_8000057c.c`, `fn_80000320.c`).
- Dumps: `local_only/lv1_mem_700000_800000.bin`,
  `local_only/lv1_mem_100000_300000.bin`.
