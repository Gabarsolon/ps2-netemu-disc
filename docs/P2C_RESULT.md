# P2C result (console, 2026-11-01; PS2 disc inserted; read from the owner's phone video `20261101_004509.mp4`)

Build `local_only/p2c/ps2_netemu_p2c.self` (sha256 `32a346ba...a07b`): no hypercalls, only loads from stock memory, 36-item pager. Values read from the video (PROVEN unless noted):

| Item | Value |
|---|---|
| 16 words at the "global heap block" 0x930F80 | all `0000000000000000` |
| HEAP CUR / LIM / FREE (what the pre-guard read) | `0x00000000` / `0x00000000` / 0 KB |
| mapped-EA cursor variable (address 0xB28A10) | `0x0000000006000000` |
| HDD driver state H (0x241c850) +08 BUS/DEV | 4 |
| H+10 DEV_ID | 3 (the netemu's HDD) |
| H+20 BUF_EA (CPU address of the HDD 1 MiB buffer) | `0x0000500002d00000` |
| H+28 LPARBUF (LPAR address of that buffer) | `0x0000000084800000` |
| H+30 DMA_RGN (HDD DMA region id) | `0x00000000d0000000` |
| H+38 TAGSTAT / H+40 / H+48 STATUS | 0 / 0 / 0 (idle) |
| pool descriptors 0x934980 / 0x24565B8 / 0x2446588 | `0x80000000` / `0x80000000` / `0x80020000` |
| native allocator 0xB9848 arena (EA) | `0x000000008003e140` |
| runtime TOC r2 | `0x751280` |
| TOC slots: -7B30, -7E50, -6F58 addresses | 0x749750, 0x749430, 0x74a328 |
| summary | `P2C DIAG OK HC=0 OPENS=0007` |

## Reading
- **PROVEN:** the block at 0x930F80 that the P2b pre-guard treated as the stock heap descriptor reads all zeros. So the guard's "RESOURCE_SHORTAGE" in H1 was a false positive from a misread structure (cursor = limit = 0), not evidence that the heap is full. The static heap model in P2B/P2C notes (a descriptor at 0x930F80 with cursor 0x58 / limit 0x5c, "13 MiB heap, 4 MiB used") is WRONG or incomplete. The real allocator state is not yet located.
- **PROVEN:** the HDD driver state is live and idle: bus 4, dev 3, BUF_EA 0x500002d00000 maps LPAR 0x84800000, HDD DMA region id 0xd0000000 (so DMA region ids on the HDD are large; the optical H0 region id was >= 8).
- **INFERRED:** the native allocator pool (EA 0x80000000.., arena at 0x8003e140) is in a different address range than the page-table-mapped DMA buffers (EA 0x5000...); whether EA 0x8003e140 equals an LPAR address (real-mode/identity) is UNKNOWN.
- **UNKNOWN:** the safe source of a DMA buffer with a known LPAR address for the optical device.
