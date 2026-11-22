# Owned-memory control — result, 2026-11-22

**PROVEN ON CONSOLE (2026-11-22 19:28Z): `status: owned`, clean XMB return at 73s,
no freeze, durable snapshot written.** Disc boot still UNKNOWN (no optical read here).

## Console run (controller-free Buzz carrier)

- Launched `play.ps3 /dev_hdd0/PS2ISO/Buzz…iso`; offline (PS2 mode) at 24s,
  returned to XMB at 73s (matches the ~72s auto-return baseline). No plug action.
- Installed SELF `7bd27754257d59537404ae4a282ed1685aede9c6a9cb38196d157e8959ea194a`;
  stock `bad3e45c…` backed up, then restored + read-back verified after the run.
- Snapshot `/dev_hdd0/tmp/netemu_owned_snapshot.bin` (sha
  `aa66345e1dfe18ae637b6de10bcd4e57acf1eb88a2fb88bdfe14c742e297280a`), `OWNSEC1`,
  decoded to `local_only/owned_control/decoded_console_snapshot.json`.

**Live owned memory (the data the drive-read step was blocked on):**

| Region | CPU EA | LPAR |
|---|---|---|
| owned block A (N=0x2000) | `0x80022440` | `0x3b22440` |
| command | `0x80023480` | `0x3b23480` |
| data | `0x80023500` | `0x3b23500` |

Pool P=`0x3b00000`, E=`0x80000000` (confirms `P + (A - E)` live). `pattern_pass:
true`, `ui_hdd_valid: true`, admission B=3 (headroom 0xff9), startup native
result `0x80022400`, saved/inside MSR `0x8000000002002030`, SPR088 `0x80c00000`.
The one real allocator call granted ownership; our own write/read patterns in the
block verified; the shutdown UFS write completed (fd=2, size 0x10000) — **no
unbounded-wait freeze on this run.**

Still absent (by design): physical sector read, DMA, cache attribute/visibility,
hardware execution, UFS deadline / durable-delivery guarantee.

---

## Offline validation (pre-console)

**PROVEN offline. Disc boot still UNKNOWN.**

`experiments/netemu_owned_control/` is the frontier build after the
controller-free mapping snapshot ([MAPPING_SNAPSHOT_RESULT.md](MAPPING_SNAPSHOT_RESULT.md)).
Its sole new behavior is to obtain **one fresh retained 8 KiB owned block** from
the native allocator under the admitted cold-start window and verify that
block's CPU-EA / LPAR subranges against its own patterns. It issues **no optical
command, no DMA setup, no device open/map, no ATAPI** — it is the memory-ownership
prerequisite, not a sector read.

## What passed (offline)

- **Build:** store audit `PASS_BOUNDED_STORE_POINTERS` +
  `PASS_ALL_STORE_WORDS_MATCH_BOUNDED_IR_TRANSLATION`; only code slot + the three
  hooks changed; segment headers unchanged; SELF decrypt round-trip exact.
- **Exclusive JVM PPC64 validation:** `status: PASS`, **194 cases**, 595 hook
  native calls, 136 fresh-allocator calls, 622 trap intercepts, 0 real syscalls
  executed. Covered: actual lazy geometry + native 23D0/18 post-return fixtures,
  compiled startup/refresh/shutdown normal-return control, allocation matrix
  (0x1032/0x9032 × EA 0x80000000/0xc0000000), all 26 fixed-bank admission
  rejections + declined snapshots, publication/pointer/timer/UI/HDD/session/
  one-shot and UFS-error matrices.
- Current final ELF SHA256 `11b570a1b03beba4e532238e87ae12c06b58ac104f162ff05166e4d6661f3e51`.
  (Earlier `pc_attempt_1.json` FAIL = superseded ELF `247b6c64…`, not current.)

Private receipts: `local_only/owned_control/pc_results.json`, `report.md`,
`build_review.json`, store audits, `ps2_netemu_owned_control.verification.json`.

## Flagged risk (unchanged, blocks unattended console test)

> Native UFS waits remain unbounded. Neither watchdog recovery nor durable
> owned_control delivery is proven.

An unbounded native UFS wait can hang the worker (console freeze). A console
test therefore requires the owner **present and reachable** for the power-cut /
manual-reboot recovery path. Not run while owner is away / out of usage.

## Console test to run when the owner is back

Preconditions the parent must set before launch (per build README):
precreate a 65536-byte `/tmp/netemu_owned_snapshot.bin`. The build does not
create that file, install a SELF, or launch a game by itself.

Then: install the owned_control SELF via `tools/install_netemu.ps1` (backup
stock first, read-back + hash-compare, `dev_blind?0` in `finally`), launch the
Buzz carrier (controller-free; auto-returns to XMB), FTP the snapshot back,
decode with
`python -B experiments/netemu_owned_control/decode_snapshot.py <bin> --output <json>`,
then restore stock and read-back verify.

## Next step (do NOT build ahead of this)

Only after the above console run proves a real fresh allocation `A` and its
CPU/LPAR subranges live: build the drive-read control (ATAPI read into the owned
buffer, matching completion, bounded polling, DMA quarantine instead of
teardown). No optical request belongs in the ownership control; the drive proof
needs live ownership first.
