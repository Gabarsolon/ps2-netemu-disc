# P10 V1 result (console test, 2026-11-01)

Build: `ps2_netemu_p10_V1.self` (sha256 834a4e53...2bee). PS2 DVD (Test Drive Unlimited) in the drive before launch. Log pulled read-only from `/dev_hdd0/tmp/netemu_log.bin`; decoded with `tools/decode_netemu_log.py`. Clean shutdown, 40 records.

## Results (PROVEN by the log)

- Storage sequence as before: open rc 0, DMA alloc/map rc 0, TUR rc 0, INQUIRY rc 0 (`SONY    PS-SYSTE...`), READ CAPACITY rc 0 (last LBA 0x001da34f, block 2048), unmap/free/close rc 0.
- **VUART port 10 answers for the netemu partition.** `get_virtual_uart_param` (HV 165): port 2 param 3 = rc 0, val 0x800 (control); port 10 param 3 = rc 0, val 0x1000; port 10 param 0 = rc 0, val 0. Zero-length `read_virtual_uart` on port 10 (HV 162): rc 0, 0 bytes. Zero-length `write_virtual_uart` on port 10 (HV 163): rc 0, 0 bytes. No -6 (LV1_NO_ENTRY): the "port 10 not bound" case did not happen.
- READ(10) PIO LBA 16 / 0 / 17 and DMA LBA 16: rc 0, async 0, buffer UNCHANGED (all 0xA5), same as P9. Data is still withheld.
- The records after sequence 40 belong to an older boot (P5, marked STALE by the decoder); ignore them.

## What this does not prove (UNKNOWN)

- That a 0x5005 request would be accepted from this partition (rc 0 on a zero-length write only shows the port accepts calls; the secure service may still reject the caller or ignore it).
- What param 3 = 0x1000 on port 10 means (port 2 = 0x800); not decoded.
- That authentication would unlock READ(10) data. This remains the leading hypothesis (INFERRED), not tested.
- The request layout comes from agy's static decode of softemu (INFERRED, not independently re-derived by the orchestrator).

## Next (needs owner decision)

P11: send the real 0x5005 request (112 bytes, layout in `docs/P10_BUILD_NOTES.md`) on port 10, read the reply by polling `read_virtual_uart` with a bounded wait (no event queue / interrupt setup, which was judged unsafe), log status and key flags, then repeat READ(10) LBA 16. Worst case: the secure service rejects or ignores the request and nothing changes; a hang is bounded by the timeout; a bad netemu only breaks PS2 games and `tools\restore_netemu.ps1` restores.
