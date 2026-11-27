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
(LBA), and (b) zero the destination buffer before the read so leftover data from
a prior command cannot masquerade as a result. Next probe (7u) zeros `ea2`
before the DMA READ(10); if `data8` is then 0, READ(10) delivered nothing.
