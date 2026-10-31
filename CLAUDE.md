# CLAUDE.md: ps2-netemu-disc

Project: make the PS3 slim's PS2 emulator (`ps2_netemu.self`) **play a PS2 disc straight from the Blu-ray/DVD drive**, no copy to the HDD. Plug in a PS2 disc, start it from the XMB, play.

Owner: Gabarsolon (hobbyist, own console, own discs). Console: PS3 slim CECH-25xx, CFW Evilnat 4.93 + Cobra, webMAN MOD 1.47.48, PS3 at `192.168.0.169`. Everything is the owner's own accessory/compatibility hobby work on their own hardware.

This project starts from the knowledge gathered in the sibling project **Buzz! Bridge** (`C:\Users\remus\buzz-pad-bridge`, public repo `Gabarsolon/buzz-bridge`, release v1.3.0), where we patched `ps2_netemu.self` successfully (four real Buzz! buzzers + lamps) and learned how to hook, rebuild, sign, install and test it. READ `docs/NETEMU_KNOWLEDGE.md` FIRST. Then `docs/GOAL_AND_PLAN.md` and `docs/OPEN_QUESTIONS.md`.

## Status (honest)

Nothing for this goal is built yet. Everything about the disc path is a hypothesis until a console test says otherwise. What is PROVEN (from Buzz! Bridge) is the patching/hooking/install pipeline and the netemu's file-read layer; what is UNKNOWN is whether the slim's drive can be read for PS2 media and whether the emulator's partition may talk to the drive. Mark every claim PROVEN / INFERRED / UNKNOWN in notes and commit messages.

## Safety rules (hard)

- **Never run install scripts or anything that writes to the PS3 yourself.** Write the script, parse-check it (`[System.Management.Automation.Language.Parser]::ParseFile` / `bash -n`), give the user the exact command, and let them run it. Reading from the PS3 (FTP `curl.exe ftp://192.168.0.169/...`, webMAN GET pages) only when the user asks or has approved that step, and read-only.
- **Never write to `/dev_flash` except through the proven procedure** (webMAN `dev_blind?1`, FTP to `/dev_blind/ps2emu/ps2_netemu.self`, read back and hash-compare, `dev_blind?0` in a `finally`), with a hash allow-list of known files, a backup of the current file first (PC `backups/` plus `/dev_hdd0/<project>/netemu_backup/`), and a restore script ready BEFORE the first experiment. No restart is needed after replacing the netemu.
- A bad netemu only breaks PS2 games; restore with the script or reinstall firmware. Still: ask before each new risky experiment, say what the worst case is, and keep every build **fail-open** (if anything is not exactly as expected, do nothing and let stock behavior run).
- Any store into the emulator's read-only memory powers the PS3 off. See the memory rules in `docs/NETEMU_KNOWLEDGE.md`; keep every write inside proven RW ranges and audit store targets on the PC before shipping a build.
- Never modify the user's original ISOs/zips or discs' dumps. Patched copies only. Do not distribute game data or discs' contents.
- Sony-derived files (`ps2_netemu.self`, ELF dumps, `stock.elf`, decrypted binaries) never go into git or any public place by default. Keep them in `local_only/` (gitignored). Publishing a patched Sony file is the owner's explicit decision per release.
- Never kill or stop any process you did not start (agy, codex, claude). Ask the user to close windows. Never bring a window to the foreground, simulate keyboard or mouse input, or take desktop screenshots. Do not launch games or PCSX2 unless asked.
- Confirm before anything outward-facing or hard to reverse: git push, tags, releases, deleting files you did not create.

## How we work (preferences learned)

- **Test once, then hand over.** Run one basic automated pass, then give the user a short exact test (steps, what to read, what to send). No repeated launches or polish runs.
- **Research proven patterns first.** For console/homebrew code, copy what working open-source projects do (PSL1GHT samples, Cobra, webMAN MOD, Linux `ps3rom`, ps3dev wiki, psdevwiki) before inventing anything.
- **Heavy research and builds go to Codex** (`codex exec`, background, tracked task, no Monitor watchers on it) and web research to **agy** (`agyp gabar -p "<prompt>" --dangerously-skip-permissions --add-dir <dir>` only because the user said to; headless agy auto-denies shell commands otherwise). Rules go in the prompt; check the result at the end. A fresh Codex run knows nothing: the prompt must be self-contained (see `reference/codex_prompt_example.txt`). Codex hits usage limits: save the prompt file, check `codex_*.jsonl` tail for "usage limit" and the retry time, then take over or relaunch.
- Use **pyghidra** (not capstone) for disassembly/decompilation/emulation; JVM `-Xmx3G`, one job at a time on this machine (or more for batch only when asked).
- Prefer the dedicated tools over shell where possible; Windows paths with backslashes; Git Bash for POSIX scripts. **Heredoc gotcha:** backslash sequences inside bash heredocs and `python - <<'E'` get collapsed by the tool layer (`\\n` becomes a real newline, `\0` a NUL byte). Put code that contains backslashes into a file with the Write tool and run it. Many source files are CRLF: preserve line endings when patching (read bytes, normalize, write back with the original ending).
- Short answers. No unrequested walkthroughs. The user types casually and fast; answer the question asked first.
- User-facing text: avoid the word "multitap"; say "any slots". No `.CONFIG` files for users (users should not hand-edit config).
- Scripts for users: parse-check them, never run them, print the exact command. Windows PowerShell + a bash version for Linux/macOS when it makes sense.
- Releases: tag `vX.Y.Z`, emoji headings in notes, honest tested / not-tested sections, assets with `SHA256SUMS.txt`; create as a draft first so the user can review; pre-release when the build was not played yet. Git identity is set per repo: `Gabarsolon <Gabarsolon@users.noreply.github.com>`.

## Tool locations (this PC)

- Ghidra 12.1.3 `C:\ghidra_12.1.3_PUBLIC`, JDK 21 `C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot`, pyghidra `HeadlessPyGhidraLauncher` (see `reference/buzz-netemu-build/gh_run.py`: PPC64 BE emulation harness, `EmulatorHelper`).
- LLVM `C:\Program Files\LLVM\bin` (clang `--target=powerpc64-unknown-linux-gnu -mcpu=970 -mabi=elfv2 -Oz -ffreestanding`, `ld.lld -m elf64ppc`) builds the native payload (see `reference/buzz-netemu-build/build.py`).
- PS3 SDK (PPU homebrew, PS3DK v0.26.0, read only) `E:\tools\ps3dk\ps3-sdk-v0.26.0-windows-x86_64`; PS2 toolchain `C:\ps2dev` + MSYS2 `C:\msys64` (IOP modules, `export MSYSTEM=MINGW32; /c/msys64/usr/bin/bash.exe -lc "cd <dir> && source build/env.sh && make"`).
- Python 3.12 (`pillow-heif`, `hidapi` installed), `adb` for the owner's phone (wireless: `adb mdns services`; photos of the TV are how console labels get read; `pillow_heif` converts HEIC).
- The Buzz! Bridge working tree: `C:\Users\remus\buzz-pad-bridge`; its big workspace of builds, reports and prompts: `C:\Users\remus\ps3buzz-console\` (e.g. `raw_capture_debug11` = the final netemu build tree, `buzzbridge_app` = the PS3 app, `release_pc`, `netemu_simple`). READ ONLY unless the user says otherwise; copy what you need into this project.

## Layout

- `docs/` knowledge, plan, open questions, the starter prompt for a new chat.
- `reference/` copies of the working Buzz! netemu build/test/installer sources (text only). Use as templates.
- `tools/` this project's tools (installer for any finished SELF, etc.).
- `local_only/` gitignored: stock/modified SELFs, ELF dumps, logs, console captures.
