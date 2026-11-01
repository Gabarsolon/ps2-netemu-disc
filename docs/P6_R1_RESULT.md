# P6 R1 result (console, 2026-11-01): the optical DMA map WORKS with the real LPAR address

Build `local_only/p6/ps2_netemu_p6_R1.self` (sha256 `895be567...a355`); log read over FTP and decoded (`local_only/netemu_log_R1.bin`; records 1..16 are the current boot, later sectors are stale records of the previous Q1 run and are marked STALE by the decoder).

PROVEN (console), current boot, clean shutdown, `finish: ps2_netemu_p6_r1 cand #1 ok!`:
- `scan: rom_cnt=1 hdd=1 bus=4 dev=2`; `grd ok` with LPAR `0x0000500002C00000` and EA `0x0000000084000000`.
- `open(4,2)` rc 0; `dma_alloc sz=0x100000 pexp=20` rc 0, region (bus address) `0xC0000000`.
- **`map #1: lpar=0x0000500002c00000 len=0x00100000 flg=0xe000000000000800` rc = 0 (SUCCESS).**
- `unmap` rc 0, `free` rc 0, `close` rc 0.

Conclusion: the netemu partition CAN map a DMA buffer for the optical device (bus 4, dev 2). The earlier -17 refusals were caused by passing the CPU address 0x84000000 as the LPAR address (my wrong "swap" diagnosis). The working parameters equal the official emulators': region size 0x100000, page exponent 20, map length 0x100000, flags 0xe000000000000800, LPAR = the value read at 0x2458438 (SB_CDVD), CPU address = the value read at 0x2458428.
Next: TEST UNIT READY, INQUIRY, READ CAPACITY and the read of sector 16 with the write-ahead log (the P4/K variants with the corrected addresses and these DMA parameters).
