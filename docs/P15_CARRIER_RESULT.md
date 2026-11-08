# Carrier diagnostic result (2026-11-09)

One carrier launch was performed using the already-installed W3 diagnostic
SELF, SHA-256
`bb5bb127ae3575b4d680c78cd8322daf094ae9979dce6ac71627781109424ca4`.
No emulator file or firmware was installed. The physical TDU disc was present
(`SLES_544.66` in `/dev_bdvd`). The carrier was the existing
`Buzz! The Schools Quiz (Europe).iso`.

## Procedure and evidence

Both ss_server1 signature blocks and target words were checked before writing.
The two existing RAM patches at `0x00713210` and `0x00714710` were applied and
read back successfully before launch. The physical-disc Cobra hook was left
stock; a carrier launch does not exercise that hook.

The existing remote log was preserved locally before launch. After startup,
a PS tap opened the diagnostic menu. Its visible label read
`P11-W3 AUTH: ERR_STAT`; the numeric status was outside the captured region,
so this test does not establish the exact status code from the screen.

The normal quit dialogue was confirmed and the console returned to XMB.
webMAN responded again. Both ss_server1 target words then read stock.
This does not identify when they reverted, or prove their state during the
authentication request.

Artifacts are private in `local_only/carrier_20261109_004414/`:

- `before.bin`: 65,536 zero bytes, SHA-256
  `de2f256064a0af797747c2b97505dc0b9f3df0de4f489eac731c23ae9ca9cc31`.
- `after.bin`: SHA-256
  `93087790352331b119410f63102f5b90bedff64b566696b9f44442e3e3e4c34f`.
  Valid NETEMULG header, boot ID `0x434d1982`, 25 current records, clean flag 0,
  no END record. The final saved record is successful completion of
  READ DISC STRUCTURE. Auth reply and LBA 16 records are absent.
- `probe_menu.png`: visible ERR_STAT label; `exit_checkpoint2.png`: XMB return.

**PROVEN:** this carrier reached the diagnostic menu and generated a new log.
The screenshot shows that execution progressed beyond the last saved record.
The incomplete log is not proof that the emulator crashed. Authentication
success and actual sector data were not demonstrated.

## Controller timing fix

Pico firmware acknowledges `PRESS` immediately after setting a future release
time. The Python helper previously returned on that acknowledgement. Calling
`close()` immediately afterward sent `RELEASE`, potentially cancelling the tap
before a USB report carried it. A final confirmation tap given time to complete
allowed this run to exit.

The helper now waits for an accepted press's requested duration before returning;
PS helpers use the same method, and the 20 ms firmware minimum is preserved.
Four offline tests simulate an immediate acknowledgement and verify that closing
after a press does not cancel it. No Pico firmware update is needed.

## Next work

Improve diagnostic persistence before changing authentication again. Capture the
auth status, key flags, sector sample, and log failure/skip counters in a durable
final summary, with a bounded retry after the drive probe has completed. Keep
the existing signatures and bounded drive calls. Validate the new build on the
PC before a further console test.

Then use the complete result to locate the rejecting auth path and establish
whether the required patch survives into that execution context. Actual sector
16 data remains the prerequisite for a physical-disc backend.
