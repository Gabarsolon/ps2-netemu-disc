# P7 S0..S3 results (console, 2026-11-01, Test Drive Unlimited PAL DVD-5 inserted)

Logs read over FTP and decoded; all runs ended `clean success`; no hang or shutdown.

| Variant | Result (PROVEN, console) |
|---|---|
| S0 | open, DMA region (1 MiB, exp 20), map (LPAR 0x500002c00000), unmap, free, close all rc 0 |
| S1 | + TEST UNIT READY rc 0 (async 0, 444..487 polls); INQUIRY rc 0, data `05 80 00 33 9b 00 00 00 53 4f 4e 59 20 20 20 20` = standard header + "SONY    " (drive answers through our DMA buffer) |
| S2 | + READ CAPACITY(10) rc 0: **last LBA 0x001da34f, block size 2048**: exactly the Redump size of the TDU disc (1,942,352 sectors) |
| S3 | + `lv1_storage_read` lba 16, region 0, 1 sector, buffer lpar+0x1000: `rc=0 async=0`, BUT the first 16 bytes of the buffer afterwards are `00 1d a3 4f 00 00 08 00 53 4f 4e 59 20 20 20 20` = the previous READ CAPACITY data (8 bytes) followed by the old INQUIRY bytes 8..15, i.e. UNCHANGED: no sector data arrived (expected `01 43 44 30 30 31 01 00`) |

## Reading
- **PROVEN:** from the netemu partition we can run ATAPI commands on the optical drive and get their data into our DMA buffer (INQUIRY, READ CAPACITY with the real disc size).
- **PROVEN:** the `lv1_storage_read` of sector 16 reported success but wrote nothing to the buffer (or wrote elsewhere / data not transferred). Read time about 0x2550E ticks (~1.9 ms).
- **UNKNOWN which:** (a) the drive refuses PS2 media data without the authentication handshake and the hypervisor reports success with no data; (b) the read's buffer argument/region id is wrong so the DMA went elsewhere; (c) the data landed at a different offset of the buffer than logged; (d) the completion status was reported before the transfer. The log only recorded 16 bytes.
- Next: a variant that pre-fills the buffer with a pattern, logs several windows of the buffer and the async/sense words, and tries the READ(10)/READ CD through the ATAPI command path (which works for INQUIRY/capacity) to see whether the drive returns data or a CHECK CONDITION sense for the PS2 disc.
