# P8 T1 result (console, 2026-11-01, Test Drive Unlimited PS2 DVD inserted)

Log read over FTP and decoded (`local_only/netemu_log_T1.bin`): 34 records, clean shutdown, `finish: ... step failed=12`.

PROVEN (console):
- Steps up to READ CAPACITY as before (open, region, map, TUR rc 0 (822 polls), INQUIRY `SONY    `, capacity lba 0x001da34f blk 2048).
- ATAPI READ(10) (DMA protocol, 1 sector, via HV 248) of LBA 16, LBA 0 and LBA 17: each `rc=0 async=0` and the 2048-byte data area is still 100% the 0xA5 pre-fill (`a5=2048`): NO data transferred, no error. REQUEST SENSE afterwards: sense key 0, ASC 0, ASCQ 0 (no sense).
- `lv1_storage_read` (HV 245) lba 16 region 0: `rc=0 async=0`, buffer unchanged (0xA5 x 2048). Region 1: `rc = 0xFFFFFFFA (-6 NO_ENTRY)`: region 1 does not exist (n_regs = 1, region 0 only).
- unmap, free, close rc 0.

## Reading
- Small inbound commands work (INQUIRY 36 B, READ CAPACITY 8 B: data arrives), but every 2048-byte data-sector read reports success with ZERO data and no sense, through both paths (ATAPI READ(10) and block read). Region 0 is the right region.
- INFERRED candidates: (1) the drive/LV1 withholds data of PS2 media until the PS2 authentication (the secure-service handshake softemu does) has happened; (2) device DMA transfers into our mapped region do not deliver data at all (the small commands may be copied by LV1 without the device's DMA engine): a CONTROL test with a PS3 game disc (readable media) separates (1) from (2).
