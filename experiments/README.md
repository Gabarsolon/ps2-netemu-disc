# Netemu experiments

The 27 original root build directories moved here on 2026-11-22, preserving
their names and contents. Historical commands need the `experiments/` prefix.
The later `netemu_autoreturn` control was created here directly.

| Directory | Current interpretation |
|---|---|
| `netemu_p16` | Trusted historical optical/authentication measurements and durable logger. Reads did not deliver sector data. Its probe needs the PS menu. |
| `netemu_autoreturn` | One controller-free Buzz carrier return to XMB proven on console; stock restored afterward. No added optical commands. |
| `netemu_snapshot` | One fresh HDD snapshot retrieved after controller-free normal return; 62 compiled PPC cases passed, stock restored. No optical commands. |
| `netemu_disc` | Unfinished backend. Stat-buffer overwrite and virtual read-return defects fixed and checked offline. Full safety and physical-disc boot remain unknown; not installed during this follow-up. |
| Other `netemu*` directories | Preserved historical variants. Their existence, names, or successful builds do not establish a successful physical read. Consult the corresponding evidence and corrected notes. |

Read [the foundational knowledge](../docs/NETEMU_KNOWLEDGE.md),
[P16 results](../docs/P16_CONSOLE_RESULT.md), and
[automatic-return evidence](../docs/AUTOMATIC_RETURN_CONTROL.md) first.
P8/P9/P18 notes retain their original observations with review annotations
where their conclusions exceeded the evidence.

Builds are experiments, not interchangeable installers. Only the proven
installer may replace `ps2_netemu.self`; Sony-derived binaries belong in
ignored private storage. No physical-disc game has booted in this project yet.
