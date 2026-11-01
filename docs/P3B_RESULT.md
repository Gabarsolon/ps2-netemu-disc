# P3B result (console, 2026-11-01): the durable in-place HDD log works

Build `local_only/p3b/ps2_netemu_p3b_L0.self` (sha256 `57507f5d...ddb1`); placeholder `/dev_hdd0/tmp/netemu_log.bin` (64 KiB zeros) created by `tools/make_log_placeholder.ps1`; the file was read back over FTP by the orchestrator (read-only) and decoded with `tools/decode_netemu_log.py` (`local_only/netemu_log_L0.bin`).

- **PROVEN (console):** header magic `NETEMULG`, next record index #5, record count 4; records `BOOT`, `T1`, `T2`, `END` (sectors 1..4) with sequence numbers 1..4, payload text as written, A/B values as written (0/0, 1/0x1111, 2/0x2222, 4/0x4444). The log write path (stock ufs_open, raw_write, ufs_close, hdd_cache_flush) works from the menu hook on the real console, in place in the pre-allocated file, with no shutdown.
- **PROVEN:** timebase deltas between records are about 0x4E3C to 0x6800 ticks (79.8 MHz) = roughly 0.25-0.33 ms per durable record.
- The header's "UNCOMMITTED / CRASH" flag is just the unwritten shutdown marker of this test build, not an error.
- **UNKNOWN:** whether a log line survives an immediate power-off right after the flush (the flush returns when LV1 reports the write complete, which may be the drive's cache), and the filesystem state check (nothing abnormal reported by the owner).
- Next: use the logger in the probes as a write-ahead log (log BEFORE every risky hypercall and its result after), so a crash leaves the last line on disk, and the owner needs no videos or photos: run the ISO, exit, the orchestrator reads the file over FTP.
