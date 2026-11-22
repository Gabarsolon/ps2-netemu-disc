# Automatic snapshot control, 2026-11-22

**PROVEN on this console:** one Buzz! Schools Quiz carrier run saved a fresh
diagnostic snapshot, returned cleanly to XMB without controller input or plug
action, and allowed the snapshot to be retrieved over FTP. Stock netemu was
then restored and read-back hash verified. No physical sector was read.

This extends [the automatic return control](AUTOMATIC_RETURN_CONTROL.md).
It provides a tested way to retrieve diagnostics without the absent Pico or
working Bluetooth button input. Physical TDU disc boot remains **UNKNOWN**.

## Scope and implementation

Text sources: `experiments/netemu_snapshot/`. Private binary outputs and
offline receipts: `local_only/snapshot/`. Console receipts and captures:
`local_only/snapshot_console/console_20261122T160625Z/`.

The native-first refresh hook retains the guarded 20-second/100-callback
timer. It samples fixed UI, HDD and CDVD mapping fields, publishes a terminal
96-byte mailbox schema once, and requests stock reason 2. It never dereferences
the captured CDVD EA or adds an optical command, allocation, or UFS call to
the refresh loop.

An original-first wrapper at the existing shutdown callsite `0x11243C`
preserves native `0x11B9BC` arguments, result and ABI. After the original
returns, a valid fresh snapshot/reason permits one transaction against the
separate, pre-created private file `/tmp/netemu_snapshot.bin`. It checks a
valid native handle and exact 65,536-byte file size, writes the 512-byte
snapshot at offset zero, and closes. The unchanged subsequent stock cleanup
performs its normal dirty-cache flush and teardown. It does not create,
truncate, resize, retry, or add a standalone flush.

**INFERRED static context evidence:** stock makes public UFS transactions in
this same ordered shutdown context and releases their lock before returning.
The control task's stock setup provides a 256 KiB stack; added frames and
scratch fit within the audited budget. Neither observation proves universal
worker quiescence or a hard native-helper deadline.

## Observed result

The console went offline for PS2 mode and GameOS returned at about 73 seconds.
Direct PS3 HDMI capture confirmed XMB afterward. The retrieved file remained
65,536 bytes; bytes beyond the snapshot sector remained zero. Its fresh
`SNAPSEC1` marker, timestamp, context, and fields matched the intended schema.

| Field | Before exit request | During ordered shutdown |
|---|---|---|
| CDVD CPU EA | `0x84000000` | `0x84000000` |
| CDVD size | `0x100000` | `0x100000` |
| CDVD LPAR | `0x500002C00000` | `0x500002C00000` |
| HDD device | 3 | 3 |
| HDD completed/status/expected | 0 / 0 / 0 | 0 / 0 / 0 |
| UFS lock sample | 0 | 0 |
| Exit reason | 0 | 2 |

These are samples across individual loads, not atomic snapshots or ownership
reservations. Their agreement does not prove cache visibility or sector data
delivery. The native first shutdown helper returned 1; its return was preserved.

**PROVEN offline:** 41 compiled PPC cases passed before the console test;
the final canonical validator passed all 62 cases after its added malformed-state
checks were consolidated. These use native/UFS boundaries
explicitly modeled. They checked both real hooks/trampolines, native-first
ABI, timer/publication guards, errors and allowed RAM writes. A parent fixture
correction let the deliberate poisoned-EA case check capture without requiring
the default EA; the payload was unchanged. Compile/store audits, unchanged
segment headers, patch-only diff and exact SELF decrypt round-trip passed.

Test SELF SHA256:
`3bbbbef1e28ba1f1228bc1655620a5d6ea0cce557491635eecdd4a2eb54743c1`.

Test ELF SHA256:
`2d30b1b3d26b458dc67a7cf0b23cde110d19dafce4bc4349781f51cf253d38cb`.

Retrieved diagnostic file SHA256:
`2f84aceb972434ecd9756a8bad0c8867456fcbae419190752b4f76f1bd237bf9`.

Restored stock SELF SHA256:
`bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`.

## Limits and next work

**UNKNOWN:** a general bounded logger/exit API, recovery from hung workers,
atomic or universal durable sector writes, optical staging ownership, and
physical-disc boot. Native UFS helpers retain unbounded waits. This one healthy
carrier result does not eliminate those risks.

The next optical diagnostic needs a retained allocator-owned buffer and its
verified LPAR translation. A separate review identified the first native pool's
LPAR/EA descriptor and startup allocation checkpoint; their proposed use still
needs compiled validation and live evidence. The read-only HPTE query can then
add cache-attribute evidence without changing mappings or issuing cache ops.
