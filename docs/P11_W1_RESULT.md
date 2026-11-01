# P11 W1 result (console test, 2026-11-01)

Build `ps2_netemu_p11_W1.self` (sha256 2b4d69d8...6562). PS2 DVD (Test Drive Unlimited) in the drive. Log pulled read-only from `/dev_hdd0/tmp/netemu_log.bin` (copy in `local_only/p11/`), decoded with `tools/decode_netemu_log.py`.

## Results (PROVEN by the log)

- Storage sequence and port queries as in V1: open, DMA alloc/map, TUR, INQUIRY, READ CAPACITY (last LBA 0x001da34f, block 2048) all rc 0; port 2 and port 10 param queries rc 0 (0x800 / 0x1000 / 0).
- **The auth request was sent**: `lv1_write_virtual_uart` on port 10, 0x70 bytes, rc 0, 112 bytes accepted (one call).
- **A reply came back**: 112 bytes read from port 10 (after 72072 polls, about 0.11 s), status word at +0x22 = **0x0016**, key flags = 0 (verdict `ERR_STAT`). So the secure service answered and rejected the request; no keys were produced. The meaning of status 0x16 is UNKNOWN.
- **The log ends right after this record**: no READ(10) records, no teardown records, no END record; the header says `UNCOMMITTED / CRASH`. Either the netemu or the console stopped between the auth reply and the first sector read. Cause UNKNOWN (what the console did must be taken from the owner's description).

## Not proven

- Why the service returned 0x16 (candidates, all INFERRED: a field of the request is wrong for this caller, e.g. the LAID or disc-type byte; the caller is not allowed; the drive needs preparation first).
- Whether authentication would unlock READ(10) data.
