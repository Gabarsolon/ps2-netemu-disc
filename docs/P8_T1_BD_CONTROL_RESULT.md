# P8 T1 control result (console, 2026-11-01): PS3 game disc, same behaviour

Same build (`ps2_netemu_p8_T1.self`) run with the PS3 BD game disc (GTA IV) inserted instead of the PS2 DVD; log read over FTP (`local_only/netemu_log_T1_bd.bin`).

PROVEN (console):
- READ CAPACITY: `lba=0x0054185f blk=2048` = 5,511,263 / 2048 (the same value the LV2 probe read from this disc in the very first baseline).
- ATAPI READ(10) (DMA protocol) of LBA 16, 0, 17 and `lv1_storage_read` region 0 of LBA 16: every one `rc=0 async=0`, the 2 KiB data area still 100% 0xA5 (no data). Region 1: -6 (no such region). Sense afterwards 0/0/0.

Conclusion: the empty reads are NOT caused by PS2-media protection or authentication: a normal PS3 disc, which reads fine under GameOS, behaves identically. What fails is the data-sector transfer itself (device DMA into our mapped buffer, via both HV 248 READ(10) with DMA protocol and HV 245), while small PIO-protocol inbound commands (INQUIRY 36 B, READ CAPACITY 8 B) deliver their data. The cause is in our DMA/interrupt/setup context, not in the PS2 disc.
Candidate causes (UNKNOWN): the stock HDD driver also creates and connects an event receive port and interrupt for its device before any I/O and completes reads by interrupt; we poll without them; the IOPTE flags/IOID for this device; the way LV1 translates our LPAR buffer to the device bus address for DMA; transfer length/alignment constraints. Cheap test: a READ(10) with the PIO data-in protocol.
