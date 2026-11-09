# P16 L1 diagnostic logger build

**PC-validated and console-tested diagnostic build.** See
[P16_CONSOLE_RESULT.md](P16_CONSOLE_RESULT.md): two fresh complete summaries
and END records recovered transient UFS-lock contention. Authentication and
sector reads remain unsuccessful.
This build measures the existing strict HDD guard and retains a bounded final
summary for a later menu callback. It does not implement a physical-disc backend
or change authentication request parameters.

## Build identity

- Source: `netemu_p16/`, forked from W3 in `netemu_p11c/`.
- Artifact: `local_only/p16/ps2_netemu_p16_L1.self` (CFW only).
- SELF SHA-256: `f90f166c5bfc7cc4039b5aa6e298bd0a5fc2e218f8fddee38148ad951519f987`.
- Payload: 14,128 of 14,320 bytes, `0x4800..0x7f30`.
- Arena: 2,744-byte structure in the existing validated 4,096-byte allocation.
- Exactly two ELF patches: code slot and menu selector at `0x270ffc`.
  The stock CDVD/file read path, including `0x3bac`, remains byte-for-byte stock.

Run `python -I -B netemu_p16/build.py` to rebuild, then
`python -I -B netemu_p16/validate_logger.py` for compiled PPC validation.
The installed Windows clang provides the front end but not a PowerPC backend;
the existing llvmlite emitter supplies PPC code generation. llvmlite 22 asserts
while expanding CTR-loop pseudos on this payload, so this build disables that
optimization and uses ordinary branch loops. CPU remains `970`, with Altivec and
VSX disabled. SELF decryption roundtrip and section HMAC checks are exact.

## Runtime changes

W3 could invoke its probe both from its experimental CDVD dispatcher and from
the menu, with separate completion flags. P16 removes the experimental dispatcher
and runs the diagnostic once from the menu. After the final known-complete read,
it releases the drive/DMA resources; no unmap/free/close is issued after a pending
ATAPI timeout. Reacquisition errors now stop before issuing dependent calls.

Logging initialization becomes ready only after header write, close and explicit
cache flush succeed. A failed init retains the same boot ID for retry. Logger
failures return errors rather than appearing successful. Successful record
acknowledgement advances cursor, sequence and in-memory clean state only after
write, header, close and flush succeed. A retry uses the same sector and sequence.

The probe's final state stays in allocator-owned memory. A `SUM ` record is
retried from later menu evaluations, with at most 16 attempts spaced at least
250 ms apart. These callbacks do not rerun the drive probe and never spin waiting
for an idle HDD. `END ` follows only after the summary is acknowledged. `END `
means diagnostic completion, not successful disc authentication.

**Deliberate limitation:** the original strict HDD predicate is retained. It
requires zero completion and expected tags. A stock flush that retains equal,
nonzero completed tags can therefore block all subsequent logging (mask `28`).
The new build exposes those raw tags and worker state on screen. See
`P16_HDD_GUARD_AUDIT.md` for the primary-code audit before changing this guard.

**Transaction limit:** raw UFS writes and cache flushes are not an atomic disk
transaction. If a flush fails after record/header writes, those provisional bytes
may still become visible on disk, including a provisional header clean flag.
The host must inspect the fresh boot ID, summary and END records, not interpret
the header flag alone as proof of durable completion. No unsafe recovery writes
are attempted when the guard says busy.

## Summary format and screen fallback

The existing NETEMULG/LOGR layouts stay compatible with `decode_netemu_log.py`.
`SUM ` text contains:

`P16L1 auth=... st=... fl=... mag=... op=... rd=... wr=... rrc=... wrc=... sector_rc=... send_rc=... async=... class=... a5=... sample=... logs=... skip=... fail=... busy=... tries=...`

`sample` is the first 32 bytes of the DMA LBA 16 buffer, never the authentication
reply's key area. `mag` and `op` are non-secret reply identity fields. The auth
acceptance policy is unchanged: even an unrelated opcode is captured verbatim
for analysis, not automatically rejected by this iteration.

`sector_rc`: 0 completed command, -1 send error (raw error in `send_rc`), -2 poll
timeout, -3 not attempted, -4 nonzero async status. Classification is `NOT_READ`
before an attempt, `NOT_VALID` on command failure, otherwise `UNCHANGED`, `ZEROS`,
`DATA_OK` (PVD version/type plus `CD001`), or `OTHER`. A return code of 0 with
`UNCHANGED` data is not a sector-read success.

Parameter A is `(auth_status << 32) | auth_flags`; B is the accumulated busy mask.
LOGR reserved u64 words at byte offsets `0x30`, `0x38`, `0x40` capture respectively
HDD completion tag, expected tag, and status40. Record flags contain HDD worker
state in the high 16 bits and command type in the low 16 bits.

Busy bits are: `01` disabled, `02` error, `04` wrong device, `08` nonzero completed
tag, `10` nonzero status40, `20` nonzero expected tag, `40` UFS lock. The summary
uses accumulated bits; menu row 4 displays the last observed mask.

Menu rows, each under 64 bytes even at maximum field widths:

0. Auth verdict, status and flags (`P16L1` marker).
1. Pre/post profile and READ DISC STRUCTURE status.
2. Auth reply/write byte counts and polls.
3. DMA16 classification, result and remaining A5 count.
4. Summary pending flag, attempts, current busy mask, fail reason and skips.
5. Raw completion/expected tags and `Q=worker-state/command-type` (low-byte hex).
6. Reply magic and opcode.
7. Sector sample bytes 0–15, hex.
8. Sector sample bytes 16–31, hex.

Raw tags in a successfully written summary may be zero because the strict guard
requires that state. When logging is blocked, the on-screen values are essential.

## PC validation

The final executable is run in Ghidra's PPC64 emulator with modeled stock UFS and
LV1 boundaries. Coverage includes successful and rejected auth replies, short
reply, timeout, write failure, unavailable port, matching reply identity and an
unrelated opcode; unchanged DMA data and actual PVD bytes; phase-log starvation
after record 25 followed by recovery; permanently busy HDD and init retry;
completed nonzero stock-flush tags; short record/header writes, close/flush
failures, END acknowledgement, 250 ms gating and the 16-attempt limit.

Memory-write tracking and the LLVM provenance audit check mailbox, arena, stack
and validated CDVD ranges. Key bytes are scrubbed and absent from logs. Compiled
formatters are exercised with maximum-width counters and INT_MIN values; byte
sentinels verify the 440-byte summary and all 64-byte menu rows stay bounded.
Only the existing hypercall instruction at `0x4858` occurs in changed code.

Evidence: `netemu_p16/evidence/validation.json`, private validation log and
build/roundtrip metadata under `local_only/p16/`.
