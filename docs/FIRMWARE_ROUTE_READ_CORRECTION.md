# CORRECTION: the "disc read" was INQUIRY leftover, not disc data, 2026-11-27

An earlier commit (019b86d, doc FIRMWARE_ROUTE_READ_BREAKTHROUGH.md, now removed)
claimed probe 7r + live A+B let the netemu partition read real sectors off the
physical TDU disc. **That claim is WRONG. Retracted.** Two controls disproved it:

1. **A+B were irrelevant.** Re-run 7s with ss_server3 and Cobra both STOCK
   (checked at launch, not applied) returned the *identical* bytes and survived.
   So the result did not depend on the A+B patches at all.
2. **The data is a fixed artifact, not disc data.** 7t changed the DMA READ(10)
   LBA from 16 to 4096; `data8` and `w1` came back byte-identical
   (`data8=0x058000339b000000`, `w1=0x444d001000000000`). A real sector read
   would change with LBA. It did not.

## What `0x058000339b000000` actually is

The standard SCSI **INQUIRY** response for the drive:
`05` = peripheral device type 5 (CD/DVD-ROM), `80` = RMB (removable), `00` =
version, `33` = response-data-format/flags, `9b` = additional length. The probe's
INQUIRY (first `run_atapi`, buffer `ea2`) writes this. The later DMA READ(10)
reads into the **same `ea2` buffer** and, because READ(10) transfers **0 bytes**
(the real wall, unchanged since 7q), `data8 = Q(ea2)` is the leftover INQUIRY
bytes. `w1` tag `0x444d` ("DM") fired only because `rd_dma = Q(ea2) != 0` — a
false positive from the shared buffer, not a successful read.

## Corrected status (PROVEN)

- **READ(10) still returns 0 disc bytes** from the netemu partition. The
  DISC_READ_WALL conclusion stands; nothing was bypassed.
- INQUIRY works (drive is a removable CD/DVD-ROM). This was already known (7q
  read "SONY" from the drive).
- `prof16 = 0x0010` (from GET CONFIGURATION at `ea2+0x100`, a separate buffer)
  *might* be a real DVD-ROM profile, but it is NOT yet trusted — it could also be
  residual. Needs a zeroed-buffer re-test before any claim.

## Process lesson

Reproducibility alone did NOT prove real data — a fixed artifact is also
reproducible. The real controls are: (a) vary an input the data must depend on
(LBA), and (b) separate the READ(10) buffer from prior commands so leftover data
cannot masquerade as a result.

## 7u definitive result (PROVEN console, snapshot `local_only/snap_7u.bin`)

7u does DMA READ(10) LBA 16, then REQUEST SENSE **after** it, and flags whether
`rd_dma` is just the INQUIRY leftover. `w1 = 0x100501`:

- `st_dma = 0`  -> READ(10) completed with **SUCCESS** status
- `sense24 = 0` (key/ASC/ASCQ all 0) -> **no sense error** (not not-ready 0x02,
  not illegal-request 0x05, not copy-protection ASC 0x6f)
- `leftover = 1` (`rd_dma == inq0`) -> READ(10) wrote **0 bytes** into `ea2`;
  `rd_pio = 0` too (PIO READ(10) also 0 bytes)
- `prof16 = 0x0010` -> GET CONFIGURATION returns **DVD-ROM** (real; separate
  buffer `ea2+0x100`)
- `cap_lba != 0` -> READ CAPACITY returns **nonzero disc capacity** (real)

### Interpretation (the real wall)

The drive, addressed from the netemu partition, answers **metadata** commands
with genuine data (DVD-ROM profile, disc capacity => it read the disc lead-in),
but **READ(10) sector content returns SUCCESS + 0 bytes with no sense error**.
This is NOT:
- a dead DMA path (8-36-byte data-in commands INQUIRY/GET CONFIG/READ CAP all
  delivered real data), nor
- a standard auth/not-ready failure (sense is clean, status is good).

It is the **PS2-disc content gate**: the drive accepts the media and serves
metadata, but silently withholds user-sector *content* for a PS2 DVD read over
generic ATAPI (no PS2-specific content unlock performed). A+B (ss_server3 Drive
Auth bypass) do not change this (7s with A+B STOCK was identical).

### Consequence for routing

Direct netemu ATAPI READ(10) cannot get sector content without the PS2 content
unlock the drive expects. GameOS/Cobra DOES read the disc (proven: full file
tree at /dev_bdvd), because it performs that unlock. So the viable route stays
**Cobra-feeds-netemu** (DISC_READ_WALL.md fork #1): have Cobra serve the live
`/dev_bdvd` sectors to the netemu via its normal file/container path, instead of
making the netemu partition read the drive itself.
