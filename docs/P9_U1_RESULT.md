# P9 U1 result (console, 2026-11-01, Test Drive Unlimited PS2 DVD inserted)

Log read over FTP and decoded (`local_only/netemu_log_U1_ps2.bin`, clean shutdown, `finish: ps2_netemu_p9_u1 clean success`).

PROVEN (console):
- READ CAPACITY again `lba=0x001da34f blk=2048` (the real disc size).
- ATAPI READ(10) with the PIO data-in protocol (proto 1, blocks 2048 x block size 1, as INQUIRY does) of LBA 16, 0 and 17: each `rc=0 async=0`, **cls=UNCHANGED** (2048 x 0xA5 still there), after ~1,700 polls (the command really ran for a while).
- ATAPI READ(10) with the DMA protocol (proto 3, 1 block x 2048) of LBA 16: `rc=0`, **UNCHANGED**, 3,166 polls.
- (PS3 BD control with the previous build T1: same behaviour for DMA READ(10) and storage_read, see P8_T1_BD_CONTROL_RESULT.md.)

## Reading
- Data-sector reads return success and ZERO data with BOTH protocols (PIO and DMA) and on BOTH media (PS2 DVD, PS3 BD). Non-media commands (INQUIRY, READ CAPACITY) work. So the transfer protocol and the buffer mapping are not the cause (PIO is copied by the hypervisor, yet no data either).
- INFERRED (best explanation now): the hypervisor/drive withholds media DATA from a partition that has not completed the disc authentication. GameOS authenticates every disc at mount (sys_ss_disc_auth: 0x5007 for BD, 0x5004/0x29 for DVD/CD); that is why the earlier LV2 probe read the PS3 BD fine but the PS2 DVD failed (ENXIO) until a manager authenticated it. softemu calls `ps2_disc_auth` (secure service 0x5000 op 0x5005 over virtual UART 10) before its reads. Our netemu partition never authenticates, so READ commands "succeed" with no data. The earlier note "not PS2 protection" was right, but the conclusion "not authentication" was premature: the control only shows the gate is not PS2-specific.
- UNKNOWN: whether the netemu partition can reach the secure service at all (P0I: virtual UART 10 is not bound to PS2_NE_LPAR by default).
