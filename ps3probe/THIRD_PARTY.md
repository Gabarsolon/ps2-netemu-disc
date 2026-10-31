# Provenance

- `ui_layout.c`, `ui_layout.h`: copied from the owner's Buzz! Bridge app `ps3/plugin/autoload`, with title/footer edits. Original header declares MIT. The font is that project's original 5x7 alphabet. `main.c` adapts its GCM framebuffer, event, pad, and watchdog approach into a smaller standalone app.
- `pkg_inspect.py`: copied from the same app's `tools/pkg_inspect.py`. Its header documents independent implementation from public PSL1GHT/ps3sdk package-format facts. The probe builder uses it only on the PC. PyCryptodome is an external host dependency.
- `storage_abi.h`: new small ABI adapters; factual argument order and constants checked against IRISMAN (SACD Ripper-derived, GPL-2.0-or-later), webMAN MOD, and SDK numeric syscall declarations. URLs, ambiguities, and the absence of a pinned upstream revision are documented in README.md. No upstream storage control/authentication code is copied.
- `probe.c`, `main.c`, build/send scripts: project source. No Sony-derived binary or decompiler text is included in this directory or the package.
