# P16: HDD tag guard audit

The existing logger requires both the completed tag (`H+0x38`) and expected
tag (`H+0x48`) to be zero. Primary stock instructions show that this is
stronger than the condition used by a completed stock I/O operation.

## Static evidence

Saved Ghidra output from the exact stock netemu is private in
`local_only/analysis/`:

- `fn_0012cc98.asm`, standalone cache flush: at `0x12CD34` it sets the
  completed tag to -1; at `0x12CD88` it stores the newly issued tag at
  `H+0x48`. At `0x12CDCC..0x12CDE4` it waits for completed tag to equal
  expected tag and checks completion status `H+0x40 == 0`. It then clears
  the cache's dirty bits and returns 0 at `0x12CE24`. Neither tag is reset
  to zero along that successful return path.
- `fn_0012b320.asm`, completion IRQ handler: at `0x12B364/0x12B368` it stores
  completion status and returned tag at `H+0x40` and `H+0x38`. It signals
  event `0x2000` and returns without clearing either field.
- `fn_0012b5fc.asm`, synchronous read: it similarly waits for matching tags
  and successful completion without clearing both tag words afterward.
- `fn_0012c110.c`, HDD worker: its completion path sets the state word at
  `H+0x00` to 2. The command selector at `H+0x58` distinguishes read and
  write requests. Their complete ownership/locking meaning still needs
  review before using them as a replacement guard.

Consequently, matching nonzero tags with status 0 can be a completed I/O
state. The existing logger would report tag-busy bits `0x28` for that state.
Its mocked flush previously returned success without modeling those retained
tag values, so passing that harness did not settle this distinction.

## Measurement before changing the guard

P16 L1 keeps the conservative predicate unchanged and exposes raw completed
tag, expected tag, and status, along with the predicate bitmask. If it refuses
to write, menu telemetry remains available without issuing unsafe disk calls.

Matching tags alone do not establish that another stock caller has finished
using shared cache state. Do not replace the guard with simple tag equality
without checking the UFS lock, driver health, pending worker ownership, and
the calling context. Do not manually clear the driver's tag or lock words.

The next decision must use the measured tag values and worker state, together
with the native completion/ownership paths. This audit does not claim that
tag retention caused the earlier record-25 cutoff; it identifies a concrete
unmodeled condition that could prevent later logger retries.
