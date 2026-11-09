# P16: native HDD ownership and logger serialization

## Result

The stock HDD worker already demonstrates a better serialization mechanism
than requiring zero tag words: take the native UFS try-lock, perform the cache
flush while owning it, then release it. This is a justified implementation
candidate for a follow-up diagnostic build. A snapshot of matching tags alone
does not acquire ownership.

Do not manually zero tag words or the UFS lock. Do not hold this lock while
calling the public stock UFS open/read/write/close routines: those routines
acquire it themselves and would wait for their own caller to release it.

## Primary evidence

The exact stock ELF SHA-256 is
`63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`.
The targeted pyghidra extraction and direct-branch scan are private in
`local_only/p16_hdd_ownership/evidence/`. The extraction used one JVM,
`-Xmx3G`, and did not access the console.

### Bounded native try-lock: `0x1EBB24`

The helper has no required arguments and returns the previous signed 32-bit
UFS lock word. Its instructions:

1. call `0x11A604` to mask interrupts, preserving the returned IRQ state;
2. load the context pointer from stock TOC `r2-0x42F8`;
3. load its first word, increment it, store it, and execute `eieio`;
4. call `0x11A5F8` with the preserved IRQ state;
5. return the previous lock word, sign-extended in `r3`.

Thus return **0 means acquired**. A nonzero return means another owner held
the lock. It is not a conventional compare-and-swap that leaves memory
unchanged on failure: even a failed attempt increments the word. The native
caller does **not** unlock on that failed path; the existing owner eventually
resets the lock to zero. Clearing it after a failed acquisition would release
somebody else's lock.

This helper contains no wait/retry loop. Its ABI uses the native stock TOC
`0x751280`; a payload must enter through its normal stock trampoline convention.

### Native unlock: `0x1EC61C`

Targeted decoding proves this is a pure unlock, not filesystem metadata sync:

```
001ec61c: e922bd08  ld    r9,-0x42f8(r2)
001ec620: 38000000  li    r0,0
001ec624: 90090000  stw   r0,0(r9)
001ec628: 7c0006ac  eieio
001ec62c: 4e800020  blr
```

No required arguments; its return value is unspecified and ignored by callers.
It performs no allocation, filesystem write, or event wait. `0x1EBB0C` has the
same five instruction semantics, but `0x1EC61C` is the one used after the native
worker's guarded cache flushes.

### Native worker pairs

The whole executable-segment direct `bl` scan finds these pairs in HDD worker
`0x12C110`; saved Ghidra disassembly verifies their branch conditions:

| Try-lock call | Acquired branch | Unlock call | Work protected |
|---|---|---|---|
| `0x12C510` | return 0 proceeds; nonzero goes to `0x12C94C` | `0x12C664` | full dirty-block sweep |
| `0x12C7F8` | return 0 proceeds; nonzero goes to `0x12C220` | `0x12C940` | dirty cache block flush and list update |
| `0x12CA18` | return 0 proceeds; nonzero goes to `0x12C220` | `0x12CB40` | tail dirty-block flush |

These are the actual storage-write/completion loops, not just state checks.
They set `H+0x38=-1`, issue LV1 storage write, save the tag at `H+0x48`, wait
for the completion IRQ, verify matching tags and status zero, then clear dirty
bits. The acquired UFS lock spans those operations. Failed acquisitions skip
the work and do not call unlock.

The worker's timer path uses this same protected sweep. It does not call the
standalone `0x12CC98` directly; the latter contains an equivalent sweep but
does not take this outer lock itself.

### Native public UFS operations

Saved exact-stock `fn_001ecc5c`, `fn_001ecb10`, `fn_001ed458`, and
`fn_001ed5cc` show that public open/close/write/read acquire the same context
word, hold it through filesystem/cache work, and clear it with `eieio` before
returning. Contended public operations wait and retry using the stock timer and
event mechanism. A logger should call those routines without holding the lock.

The aligned sector backend at `0x1EB780` calls cache write `0x12D0AC` or cache
read `0x12D224`. The direct branch scan finds the synchronous physical-read
helper `0x12B5FC` called only from the cache-read path, and the cache-eviction
helper called from those cache routines. This supports the UFS lock as the
normal-runtime serialization boundary. The scan covers direct branches;
indirect function-pointer callers and unusual shutdown contexts are not a
general mathematical exclusion proof.

## Why the zero-tag guard is not an ownership test

The exact stock flush and read helpers leave completed and expected tag words
equal after successful completion. They do not clear both to zero. Matching
nonzero tags and status zero therefore can describe completed I/O.

Nevertheless, equal tags do not prove a suspended caller has finished consuming
the result or updating cache state. Replacing the old predicate with equality
without taking the native lock would retain a check-then-act race. The native
try-lock removes that race for the normal UFS/cache callers described above.

`H+0x00` is not established as a universal active/idle flag. Worker `0x12C110`
uses its values in image/state transitions, handling values 3, 4, and 0,
writing 1 during transition work and 2 on completion. `H+0x58` selects a queued
read/write operation. Its value can remain after the operation; it should be
telemetry, not a sole idle guard. Pending fields `H+0xA0/+0xA4` are manipulated
under IRQ masking when writes are queued or chained; checking them without
ownership would also be a snapshot rather than synchronization.

## Justified follow-up design

1. Keep the proven driver-health checks: enabled, no driver error, expected
   device, valid arena, preallocated file, aligned bounded writes.
2. Use the stock UFS open/write/close calls normally. They acquire and release
   their own ownership. A completed nonzero tag is not grounds by itself to
   refuse those serialized operations.
3. Before calling standalone flush, call native try-lock **once**. If its
   returned prior value is nonzero, defer the summary without unlocking.
4. If acquired, re-read health and tag/status state under ownership. Allow
   initial zero/zero or matching completed nonzero tags with status zero;
   reject mismatched tags, the -1 in-flight sentinel, or unhealthy state.
5. If the owned guard passes, call stock standalone flush. Release with native
   `0x1EC61C` on every return path after successful acquisition, including
   health-check and flush failures. Do not call public UFS helpers while held.
6. Advance the logger's committed cursor/summary state only after that flush
   succeeds. Defer with a finite attempt/time budget otherwise.

The extra matching-tag check under ownership is conservative; the native
worker normally relies on its lock and driver-health state rather than
requiring zero tags. This design copies the established ownership pattern
instead of repairing fields by hand.

## Validation required before console use

Run the actual compiled PPC native try-lock/unlock, including:

- initial lock 0 becomes 1 and returns 0; release resets it to 0;
- initial lock 1 becomes 2 and returns 1; caller does not release it;
- no wait or I/O on failed acquisition;
- completed equal nonzero tags permit one owned flush;
- mismatched tags, -1 sentinel, disabled/error state prevent flush and still
  release an acquired lock;
- no public UFS call executes while the payload owns the outer flush lock;
- every error path preserves lock ownership and bounded summary retries.

Stock standalone flush still waits for a hardware completion event without a
new timeout. The ownership fix prevents overlapping normal I/O; it does not
make a failing drive or the stock flush implementation hard time-bounded.
