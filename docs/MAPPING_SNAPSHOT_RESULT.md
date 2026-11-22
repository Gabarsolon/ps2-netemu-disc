# Mapping snapshot result, 2026-11-22

**PROVEN on console:** one controller-free Buzz carrier saved a fresh `MAPSEC1`
snapshot and returned to XMB. Stock netemu was restored and read-back verified.
No physical-sector command or allocation was added by this control.

| Observed field | Value |
|---|---|
| First native pool useful extent | `0x60000` |
| Pool flags | 1 |
| Pool LPAR base P | `0x03B00000` |
| Pool CPU EA base E | `0x80000000` |
| Published native E | `0x80000000` |
| Allocator payload base / initialized sentinel | `0x80020000` |
| First bank head | `0x2446598` |
| First bank next / growth marker | 0 / 0 |
| CDVD EA / size / LPAR | `0x84000000` / `0x100000` / `0x500002C00000` |
| Sampled HTAB handle / size fields | 0 / 0 |

**PROVEN:** both HPTE scans skipped because the sampled HTAB size was unsupported
(zero). **No call-95 query executed on this console run.** Cache attributes,
active SLB/TLB selection and physical backing remain **UNKNOWN**. The zeros
must not be replaced with a guessed table size. Whether these fields differ
earlier in the run or follow another lifecycle remains unestablished.

The pool's low LPAR and the borrowed CDVD buffer's high LPAR give a concrete
reason to test a different, independently owned staging allocation. **UNKNOWN:**
whether this difference explains the unchanged A5 sector buffers. LPAR numbers
alone do not prove cache policy, physical memory type or DMA eligibility.

The exact native pool producer establishes the conditional translation
`P + (A - E)` for a **fresh retained allocator result A** wholly within the
same pool. The snapshot itself neither allocates nor reserves memory. Do not
treat a plausible contained pointer or unused pool tail as owned.

**PROVEN offline:** 160 compiled PPC cases passed for the final candidate,
including the five-output query bridge, matching/error/ambiguity handling,
native-first ABI, file faults and store bounds. The exact stock handler has
a zero-handle current-table lookup path, so an unsupported unconditional
zero-handle rejection was removed before final validation. Failed outputs
remain uninterpreted. That correction did not override the separate size guard.

Private console evidence:
`local_only/mapping_snapshot_console/console_20261122T162950Z/`, including
`receipt.json`, `decoded_mapping_snapshot.json`, `returned_mapping_snapshot.bin`
and direct PS3 HDMI `returned.png`. GameOS returned at about 72 seconds.

Test SELF SHA256:
`b85499709c35455b733e6bf365c0e59791d85df1784725c399a10fa036f502e0`.

Test ELF SHA256:
`38ce9efcb9639199b86a1f3fd403a1c84766302bdaa0ac63fae98e5a229ba63e`.

Retrieved diagnostic file SHA256:
`a0a6598941bb7e8eb9904b40573d560a0f1c25bb412bce0e14e5527f470b34ee`.

Restored stock SELF SHA256:
`bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`.

## Owned-memory preparation

**PROVEN offline:** original native allocator code passed 41 scenario receipts
plus 26 admission rejections. Actual allocation loops/stores ran with only
verified IRQ trap boundaries and initial context modeled. Split, exact-fit,
no-fit, nested interrupt state and malformed metadata were covered. This does
not establish an installed startup wrapper or an observed fresh allocation.

**INFERRED from checked startup control flow:** an original-first wrapper at
`0x18CB4 -> 0xB9D54`, followed by bounded admission and allocation under native
outer IRQ save/restore, can use the normal interval in which the other hardware
thread is parked until the later `0x18D8C` release. This is specific to that
cold-start path; it is not a general SMP allocator lock.

The next control must validate the complete single-bank geometry/headroom,
obtain one fresh retained 8 KiB block, verify its CPU/LPAR subranges and test
only our own patterns. No optical request belongs in that ownership control.
The subsequent drive proof still needs matching completion, exclusive buffer
lifetime, bounded polling, and quarantine rather than teardown of pending DMA.
