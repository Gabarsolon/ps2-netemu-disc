# P15 follow-up audit (2026-11-09)

Resumed conversation `fc13349c-d476-43f8-8fde-aa7625f2321d` after two
physical-disc launches produced black screens. No new console experiment was
run during this audit. Initial HTTP requests were blocked by session
permissions. After full access was enabled, read-only HTTP and FTP checks
succeeded. The snapshot is in `local_only/resume_20261109_004106/`.

**Current console checks:** the Cobra callsite is stock and its complete
160-byte trampoline region is zero. Both ss_server1 target words are stock.
The installed emulator SHA-256 is
`bb5bb127ae3575b4d680c78cd8322daf094ae9979dce6ac71627781109424ca4`.
The remote log is still the all-zero placeholder described below. FTP reports
`ps2emu.dat` unavailable and returns a 9,972-byte `ps2bootparam.dat`; neither
proves that netemu executed.

## Evidence from saved files

- **PROVEN (local decode):** `local_only/netemu_log_run2.bin` and
  `local_only/netemu_log_tdu.bin` are both 65,536 zero bytes, SHA-256
  `de2f256064a0af797747c2b97505dc0b9f3df0de4f489eac731c23ae9ca9cc31`.
  Neither contains a header, records, or evidence that the probe ran.
- **PROVEN (local decode):** the saved `local_only/run_test_log.bin` has a clean
  W3 run with 37 records. Its auth reply reports status `0x0016`, key flags 0,
  verdict `ERR_STAT`. The LBA 16 buffer remains `a5a5a5a5`. A successful command
  completion code does not demonstrate sector data was returned.
- **PROVEN (local binary comparison):** `local_only/stage2.cex` contains the
  expected 16-byte Cobra signature at file offset `0x108b0`, followed by the
  stock callsite bytes. This supports the existing target constants for that
  saved binary; it does not identify the console's current firmware state.
- **PROVEN (saved webMAN source):** `local_only/webman_debug_mem.h` aligns the
  displayed peek address down to 16 bytes before rendering. The previous
  conversation's ad hoc eight-byte dump read the first eight bytes for each
  request without using the displayed address. This explains its duplicated
  instruction pairs. Do not use that dump as a reliable disassembly.

## Patcher fixes

`tools/patch_cobra_netemu_disc.py` now parses displayed row addresses, strips
highlight tags, and rejects incomplete or duplicate rows. It verifies the
whole 160-byte region from `0x0053bd00` through `0x0053bd9f`, including gaps,
before classifying an installation as active.

Apply accepts only an exact stock callsite and an empty region, or an exact
already-active installation. Unknown states cause no writes. Every code/data
word is read back before activating the callsite. Revert accepts only the
exact known installation and confirms the stock branch before clearing code.
Failures return a nonzero exit code. The emitted PPC instructions and target
addresses have not changed.

**Validation:** `python -I -B tools/test_cobra_patcher.py` passes 16 tests entirely offline.
It covers highlighted/aligned HTML, missing/duplicate rows, stock/active/unknown
states, each corrupted byte, dropped payload writes, failed activation, and
failed unhooking. This tests the host patcher, not execution on the Cell CPU.
The corrected parser also passed a live read-only `--check` against webMAN.
Live HTML exposed a navigation label adjoining the first dump row; parsing is
now restricted to the memory `<pre>` block, with a regression test for this case.

## Claims still unknown

- A black screen does not prove `ps2_netemu` started, nor establish why it hung.
- The saved results do not establish when the LV1 patches disappear, whether
  the launch-time hypercalls succeed, or whether their changes persist.
- The diagnostic W3 probe is attached to the in-game PS menu. An all-zero log
  cannot distinguish failure before the hook from failure to open the menu.
- A carrier ISO can provide a known working environment for that probe, but
  its launch does not exercise the physical-disc-only Cobra hook. Treat a
  carrier test and a direct-disc launch as separate experiments.
- Authentication, sector 16 reads, and physical-disc boot remain unproven.

## Next console work

First read the current hook state and hash the installed emulator. Preserve
the existing remote log before launching anything. If a carrier diagnostic is
run, save its log to a new path and report auth status and actual buffer data;
an END record alone is not success. Do not repeat the direct-disc launch until
there is a way to establish which launch stage executed. Unknown patcher states
require investigation rather than automatic overwrite.
