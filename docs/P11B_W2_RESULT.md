# P11b W2 result (console test, 2026-11-01)

Build `ps2_netemu_p11_W2.self` (sha256 ea58d1c6...8f02). PS2 DVD (Test Drive Unlimited) in the drive. Log pulled read-only (copy in `local_only/p11/`), decoded with `tools/decode_netemu_log.py`. Clean shutdown, 46 records, END record present: the retrying log writer fixed the W1 silence.

## Results (PROVEN by the log)

- Preparatory commands all completed rc 0, async 0: GET CONFIGURATION, READ DISC STRUCTURE, GET CONFIGURATION again (then the same VUART param queries as before).
- The auth request was sent once (write rc 0, 112 bytes) and a 112-byte reply came back (54128 polls): **status 0x0016 again, key flags 0** (`ERR_STAT`). The preparatory sequence did NOT change the outcome.
- READ(10) PIO LBA 16, 0, 17 and DMA LBA 16: rc 0, async 0, buffer UNCHANGED (all 0xA5). Data still withheld. Teardown rc 0 everywhere.

## What the log does not show (UNKNOWN)

- The drive's MMC profile before and after the preparatory commands. The log records only rc/polls, not the profile words; they are on the glance menu (row 1: `PROF1=0x.... PROF2=0x.... RDS=0x....`), which the owner has to read from the screen.
- Whether the profile was already the PS2 profile (0xFF60/0xFF61) and the 0x16 comes from something else in the handler. The static finding "0x16 = not a PS2 disc profile" (P11b analysis) is therefore still unconfirmed on the console.
