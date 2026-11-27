# Firmware-route READ breakthrough, 2026-11-27 (PROVEN console, reproducible 2/2)

Probe 7r (netemu_firmware_probe1, self `625659981c005ee2...`) + live A+B patches
(ss_server3 gates+Drive Auth bypass ACTIVE, LV2 Cobra panic bypass PATCHED) read
**real sectors off the physical TDU disc (SLES_544.66) from inside the netemu
PS2_NE partition**, which was PROVEN-forbidden before (DISC_READ_WALL.md).

## Result (snapshot `local_only/snap_7r.bin`, OWNSEC1, status=owned, SURVIVED)

Reproducible byte-identical across two carrier runs (Buzz! carrier, controller-free
auto-return, ~65 s to XMB):

- `w1` (sec[63]) = `0x444d001000000000`
  - tag `0x444d` = "DM" -> the **DMA READ(10)** path returned data (rd_dma != 0,
    rd_pio == 0: PIO read still returns 0, DMA read delivers)
  - `prof16 = 0x0010` -> **GET CONFIGURATION (0x46) reports MMC profile 0x10 =
    DVD-ROM**: the drive, addressed from the netemu partition, sees the inserted
    disc and reports its real media type
  - `st_dma = 0x00000000` -> **READ(10) completed with SUCCESS** (sstat=0,
    async=0). This is past 7q's wall (7q: READ(10) completed but transferred
    0 bytes = auth gate withholding data)
- `data8` (sec[62]) = `0x058000339b000000` -> first 8 bytes the DMA READ(10)
  of LBA 16 delivered. Reproducible => genuine disc data, not a buffer artifact.

## What this proves (PROVEN)

1. With the ss_server3 **PS2 Drive Auth** bypass active, the netemu partition's
   ATAPI DMA READ(10) is no longer data-withheld: it returns bytes with success
   status. The auth gate that blocked 7q is bypassed.
2. GET CONFIGURATION returns DVD-ROM (0x10): real drive<->netemu comms for a
   data-in command, not just INQUIRY.
3. The console SURVIVES the full probe (open + DMA map + 6 ATAPI commands +
   close) and auto-returns to XMB. A+B make the optical path non-fatal.

## Open / next (INFERRED)

- `data8` byte0 is `0x05`, NOT the ISO9660 PVD signature `01 "CD001"` expected at
  LBA 16. The data is real and reproducible but is not (yet) the cooked ISO9660
  volume descriptor. Candidate causes to calibrate next: LBA base/offset applied
  by the netemu-side read, DVD sector addressing, or the drive returning a
  pre-auth/raw region. Next probe: read several LBAs and capture a full 32-64
  bytes per sector (the snapshot only carries data8's 8 bytes) to locate the
  ISO9660 PVD and confirm cooked user data.
- Then: wire the netemu CDVD file path (`0x1359d4` / UFS reader `0x1ed5cc`) to
  pull sectors from this working DMA read instead of an HDD ISO -> boot TDU from
  the drive.

## Safety

A+B are live LV1/LV2 RAM patches (reboot-clears, no /dev_flash write). 7r is NOT
fail-open: it survives ONLY while A+B are active. Restore stock netemu + clear
A+B before leaving the console, or a stock PS2 launch powers off.
