# Tooling and workflow

How a change goes from idea to a console test. Proven in the Buzz! Bridge work; templates are in `reference/buzz-netemu-build/`.

## Get the stock file (once)

1. Read it from the console (read-only, owner approves): `curl.exe -o local_only\stock_ps2_netemu.self ftp://192.168.0.169/dev_flash/ps2emu/ps2_netemu.self`.
2. Check sha256 = `bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`. Any other hash: stop, the addresses in the notes do not apply.
3. Decrypt to ELF with `reference/buzz-netemu-build/selfdec.py` (keys from the public `key_vault.cpp`, see `docs/NETEMU_KNOWLEDGE.md`). Keep the ELF in `local_only/`.

## Analysis (P0)

- pyghidra, headless, JDK 21, `-Xmx3G`. Import the ELF as PowerPC:BE:64:default, analyze, then script. Template: `reference/buzz-netemu-build/gh_run.py`.
- Searches to start with:
  - `sc` instructions (LV1 hypercalls use `sc 1`; the call number is in r11): list all sites and the wrapper functions around them.
  - callers of `0x1ED5CC` (UFS raw_read), `0x1ecc5c`, `0x1ec760`: how the HDD device is opened and which id it uses.
  - strings: `ufs`, `storage`, `bdvd`, `cdvd`, `disc`, `atapi`, `media`, `iso`.
  - the CDVD emulation: callers of `0x3CFC`/`0x3960`/`0x39B0` and what they do with the returned size.
- Write findings to `docs/` immediately, labeled PROVEN / INFERRED / UNKNOWN.

## Build (when there is a payload)

- Copy `reference/buzz-netemu-build/{build.py,make_package.py,ppcasm.py,selfdec.py,resign_self_installed.py}` into a new `netemu/` dir; adapt the config (hook list, code slot, labels). Do not edit the reference copies.
- Compile with LLVM (flags in `CLAUDE.md`), link into the code slot, patch entry points, repack the SELF. Output goes to `local_only/` (never git).
- Code slot is 14,320 bytes; Buzz used all but 16. A disc backend probably needs its own space: plan how to extend (see `NETEMU_KNOWLEDGE.md`, memory rules).

## Validate on the PC before any console test

- PPC64 emulation harness (`gh_run.py` + `gh_harness.py`): runs the real final code with the real original handlers; add fake LV1 storage hypercalls (return codes, delays, short reads, failures) and a fake disc image.
- Store-target audit (`gh_store_scan.py`): no store outside proven RW.
- SELF round trip: decrypt the output and compare to the intended ELF; headers/HMACs valid.
- Parse-check the installers.

## Console test

1. The owner runs `tools\install_netemu.ps1 -File <build>` (backup and read-back built in). Never run it yourself.
2. Fixed test: start a PS2 game from webMAN as usual, open the PS-button menu, read the `Debug Information` row (photo; I read it over adb). Labels carry return codes.
3. Restore with `tools\restore_netemu.ps1`.

One basic pass, then hand over. Give the owner the exact steps and what to send back.

## PS3 homebrew probes (P0 drive test)

- PS3DK v0.26.0 + CMake + Ninja; template app `C:\Users\remus\ps3buzz-console\buzzbridge_app` (video, pads, logging, build script `ps3/build_ps3.ps1` in the Buzz repo).
- Keep probes read-only on the drive. Log result codes to `/dev_hdd0/tmp/<probe>.log` and also on screen.
- Packaging and install of a .pkg: the owner installs (webMAN/package manager); offer a send script like `send_to_ps3.ps1` in buzzbridge_app, never run it.

## Delegation

- **Codex** for long builds/analysis: self-contained prompt file (see `reference/codex_prompt_example.txt`), `codex exec` as a tracked background task, no dangerous bypass, skip updates, no Monitor watchers; check `codex_*.jsonl` for "usage limit".
- **agy** for web research (psx-place, psdevwiki, Linux ps3rom, webMAN source): `agyp gabar -p "<prompt>" --dangerously-skip-permissions --add-dir <dir>` (only because the owner said so), output to a REPORT.md; verify claims before relying on them.
- Never kill their processes; ask the owner to close windows.

## Diagnostic tricks

- Label strings are the only feedback channel on the console. Encode bytes as `B3=7F` style pages; page chosen by `selected & 3`.
- Heartbeat/log files on the HDD for homebrew probes.
- When a test is inconclusive, say so; do not guess a cause (the Buzz freeze was never proven).
