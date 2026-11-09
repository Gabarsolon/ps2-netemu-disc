# P16: authentication-path audit and runtime discriminator

## Result

The two existing bypass branches have the intended polarity in firmware 4.93.
They select accepted paths, but do not establish authentication success.
Status `0x0016` alone cannot identify the rejecting path.

The next useful measurement, after the P16 logger is validated, is a temporary
forced-error return at the PS2 authentication helper entry. A returned `0x005A`
would demonstrate that this modified helper executed in the service instance
handling the guest request. This is a diagnostic discriminator, not an
authentication bypass. No console memory was changed during this analysis.

## Primary evidence and scope

The analysis used the local firmware 4.93 `ss_server1.elf`, SHA-256
`808f1aef59d0515e76ddf9ecd0b34836664d122e3a9457887eabdddbe1529fef`.
Targeted decompilation and instruction decoding used pyghidra, with one JVM
at a time and `-Xmx3G`. Outputs are private in
`local_only/p16_auth/ss_server1/`.

The saved physical dump `local_only/lv1_mem_700000_800000.bin` was compared
against the ELF at each location described below. All six checked 16-byte
regions match. Exact bytes and hashes are in
`local_only/p16_auth/locations.json`. This confirms the earlier mapping in
that acquisition; a new live preflight is still required for any experiment.

No new claim about which code survives a partition transition follows from
these static comparisons. The latest carrier result only establishes patched
words before launch and stock words after XMB returned.

## Exact command path and reply identity

The constructor at `0x8001C418` registers opcode `0x5005`, service `0x5000`,
and installs vtable `0x800586A8`. Vtable offset `+0x48` contains descriptor
`0xC00074B8`, which resolves to executor `0x8001E724`.

That executor calls `0x80020638`, stores its returned value as a 32-bit status
at object offset `+0x18`, and returns boolean 1 to the dispatcher. It is the
only direct caller of `0x80020638` in this binary.

The base constructor `0x8000057C` and serializer `0x8003D31C` establish:

| Field | Object offset | Serialized body offset | Full VUART packet offset |
|---|---:|---:|---:|
| Opcode (`0x5005`) | `+0x08` | `+0x00` | `+0x10` |
| Service (`0x5000`) | `+0x10` | `+0x08` | `+0x18` |
| Status, 32-bit big-endian | `+0x18` | `+0x10` | `+0x20` |

The probe reads the low 16 bits of that status at full packet `+0x22`.
The opcode and service are copied unchanged. A complete reply should therefore
be checked for opcode `0x5005` and service `0x5000`, as well as framing/length,
before its status is treated as this request's result. The earlier probe did
not validate reply identity, so a stale or unrelated packet remains a possible
confounder. This audit does not establish that one was actually received.

## Branch polarity

### Firmware/product check

Function `0x8001F0E4` issues INQUIRY and compares the product field with the
accepted strings. At VA `0x8001F210`, physical `0x00713210`, stock instruction
`419E0164` is `beq cr7,0x8001F374`.

| Condition | Stock flow | Existing unconditional patch |
|---|---|---|
| First accepted product string matches | Accepted path at `0x8001F374` | Same accepted path |
| First fails; second accepted string matches | Accepted path via `0x8001F238` | Accepted path immediately |
| Both fail | Load status `0x16` at `0x8001F248`, then return | Accepted path |

The accepted target initializes the REPORT KEY retry counter and enters the
existing command/retry loop. It does not skip all drive operations or simply
return success. INQUIRY transport failure remains an earlier error path; REPORT
KEY may still fail after the branch is bypassed.

### PS2 profile check

At VA `0x80020710`, physical `0x00714710`, stock `409D001C` is the unsigned
branch accepting `(profile - 0xFF60) <= 1`.

| Returned driver profile | Stock result | Existing unconditional patch |
|---|---|---|
| `0xFF60` or `0xFF61` | Dispatch secure operation `0x0C`, length `0x38` | Same dispatch |
| Another value | Return status `0x16` | Dispatch secure operation |

The profile word is obtained from the `/dev/rbd0` query helper `0x80024E30`,
not the probe's direct MMC GET CONFIGURATION result. The function initializes
the word to `0xFFFF` and logs the query's result, but does not separately check
its return code before testing the word. A rejected word therefore need not be
a successfully fetched generic DVD profile; it may also be an unchanged default
after a failed query.

Passing this gate calls `0x8003220C`; its preparation, secure execution, and
result-read operations can still fail. The profile gate is not proof that
session keys were produced or that sector reads are available.

## Relevant sources of status `0x16`

For the directly traced `0x5005` path:

1. Product mismatch in `0x8001F0E4`: loads `r29=0x16` at VA `0x8001F248`,
   physical `0x00713248`, and returns through that helper's epilogue.
2. PS2 profile rejection in `0x80020638`: loads `r31=0x16` at VA
   `0x80020720`, physical `0x00714720`.
3. A propagated downstream error from secure dispatch `0x8003220C`. This
   routine returns errors from its constituent operations; the audit does not
   rule out a downstream value of `0x16`.

Early policy checks in `0x80020638` return `0x0A`; the device/sense helper
`0x8001EE28` distinguishes several other errors. They should not be conflated
with a proven profile rejection merely because the final probe verdict is the
generic `ERR_STAT`.

The existing canary tool includes two additional profile rejection locations,
`0x00713E48` and `0x00714410`. Their surrounding primary instructions test
`0xFF70/0xFF71`, not `0xFF60/0xFF61`; they are not the direct PS2 `0x5005`
profile branch. The saved binary also has another `0xFF70/0xFF71` rejection
at VA `0x8001FB90`. The four old canaries are not a complete or equally
relevant map of this command's possible failures.

### Existing firmware canary is masked

The firmware helper's epilogue includes:

```
0x8001F394: li  r0,0x16
0x8001F39C: and r3,r29,r0
```

Consequently the old canary value `0xAA` at physical `0x00713248` would return
`0x02` (`0xAA & 0x16`), not `0xAA`. An experiment expecting `0xAA` in the
reply would be misinterpreted. The entry-return discriminator below avoids
this inner helper and its mask.

## Proposed forced-error discriminator

Preferred target: the 8-byte-aligned entry of `0x80020638`, physical
`0x00714638`, before any prologue instruction executes.

| Item | Exact bytes |
|---|---|
| Expected stock first 16 bytes | `f821ff517c0802a6fba10098fbc100a0` |
| Stock first 8 bytes / rollback value | `f821ff517c0802a6` |
| Temporary first 8 bytes | `3860005a4e800020` (`li r3,0x5A; blr`) |

The stub performs no drive authentication operation, changes no stack frame,
and leaves the link register available for the existing caller. The caller
stores the returned `0x5A` without a status mask and continues the normal reply
serialization. The stub does not make authentication succeed.

Do not apply the same two-instruction stub to executor `0x8001E724`: that
function returns a dispatcher boolean, and would need to set the status object
explicitly. The aligned helper entry avoids that additional store and the
unaligned executor address.

### Offline execution proof

`local_only/p16_auth/sentinel_abi.py` ran inside Ghidra EmulatorHelper on the
real 4.93 ELF. The helper entry was changed only in emulator memory. The test
then executed the real executor, subclass serializer, base serializer, and byte
copy helper. It verified:

- helper return `0x5A`;
- executor boolean return 1;
- status object and serialized status word both `0000005a`;
- probe-visible low 16-bit packet status `005a`;
- unchanged stack pointer, TOC, link register, and nonvolatile GPRs.

The pass record is `local_only/p16_auth/sentinel_abi.json`. This proves local
instruction/ABI and serializer behavior, not live patch persistence, code-cache
visibility, or which service instance handles the console request.

### Interpreting a later console experiment

Once the logger is reliable, perform one guarded carrier test with only this
diagnostic change. First verify the complete surrounding stock signature at
the current physical mapping; preserve the original 8-byte value; write and
read back the sentinel; run one request; then restore the known original word
after XMB returns if it has not already reverted. Do not overwrite an unknown
state. Maintain the existing emulator backup/restore procedure.

| Observation | Conclusion |
|---|---|
| Valid `0x5005/0x5000` reply, status `0x005A` | Modified helper executed for that guest request; its patch was effective at that instant |
| Valid reply still `0x0016` | Does not prove reset: wrong instance, different flow, instruction visibility, or an earlier reply remain possible |
| Wrong opcode/service, short reply, or timeout | No conclusion about this helper's runtime state |
| Sentinel present before launch and stock after XMB | Establishes a transition occurred somewhere; does not locate its timing |

This volatile-code experiment still carries hang/reboot risk if the target or
execution environment is wrong; it is not a zero-risk substitute for preflight.
It avoids patching secure-service firmware files or attempting successful key
derivation while measuring the runtime path. Log status, identity, and safe
flags only; never the key bytes at reply `+0x40..+0x6F`.

## Corrections to prior conclusions

The older P11 notes' statements that a `0x16` response proves the profile
branch, that pre-launch patches must persist, and that bypassing the profile
immediately guarantees successful key calculation are stronger than the
evidence. They should be treated as superseded by this audit and the measured
carrier results. No evidence here justifies modifying flash-resident secure
services or switching partition types.
