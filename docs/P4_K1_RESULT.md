# P4 K1 result (console, 2026-11-01): first write-ahead log; the DMA map is refused (-17)

Build `local_only/p4/ps2_netemu_p4_K1.self`; log read over FTP by the orchestrator and decoded (`local_only/netemu_log_K1.bin`): 14 records, clean shutdown flag, no crash point.

| Step | Logged (PROVEN) |
|---|---|
| BOOT / SCAN | `boot: ps2_netemu_p4_k1`, `rom_cnt=1 hdd=1 bus=4 dev=2` |
| GRD | `grd ok: lpar & ea sanity pass`, LPAR 0x84000000, EA 0x500002C00000 (the EA/LPAR fix works) |
| open(4,2) | rc 0 |
| DMA alloc (sz 0x80000, page exp 12) | rc 0, region (bus address) `0xC0000000` |
| MAP `lv1_map_device_dma_region(4,2, lpar=0x84000000, bus_addr=0xC0000000, 0x80000, flags 0xe000000000000800)` | **rc = 0xFFFFFFEF = -17 (invalid parameter)** |
| free region | rc 0 |
| close | rc 0 |
| END | `failed step=4` (the map) |

## Reading
- **PROVEN:** the write-ahead log works exactly as designed (PRE/POST pairs with args and return codes; per-record cost about 0.1 ms). From now on no videos/photos are needed.
- **PROVEN:** with these arguments the hypervisor refuses to map the SB_CDVD buffer into the optical device's DMA region. Everything before it (open, region allocation) is accepted; free and close work.
- **UNKNOWN:** which argument is wrong. Differences from the stock HDD map (HDD: dev 3, LPAR 0x84800000, region 0xd0000000, same size 0x80000 and the same flags 0xe000000000000800 as hard-coded in the stock helper 0x160fc): the device id, the LPAR range (the CDVD buffer), the bus address, and maybe the flags (IO identifier / IOPTE bits might be device-specific). Next: read the exact allocate/map arguments the softemu/gxemu/phat emulators use for the OPTICAL device and try candidate argument sets (a failing map is harmless: it returned -17 cleanly).
