# Offline automatic-return control experiment

**UNKNOWN: cooperative return to XMB.** This is a reviewable experiment for a
later parent-controlled carrier test, not a production exit API. No hardware
test or installation was performed. The PPC validator has **NOT RUN** because
another investigator owns the sole JVM.

Build from the exact stock ELF/SELF in `local_only`. The only hook replaces
`BC168: f821fec1` with a tail branch. Its wrapper forwards all eight `u64`
arguments through the native-TOC trampoline, relocates the original stack
update, resumes at `BC16C`, and retains the native return value. The callback
then checks state. There are no disc/file/UI hooks, drive commands, fake pad
inputs, log writes, allocation, forced shutdown, panic, or fallback calls.
The prior Buzz ISO is only a future stock HDD carrier; no game image changes.

All binary and generated outputs are in ignored `local_only/autoreturn`.
From the repository root, the offline build command is:

```powershell
python -B .\experiments\netemu_autoreturn\build.py
```

It checks both stock hashes, the zero slot/mailbox and exact hook prologue;
compiles PPC64BE 970 ELFv2 through Clang IR and llvmlite; rejects mutable
globals/BSS; audits IR and compiler/trampoline stores; patches only the code
slot and one hook without extending segments; and repacks/decrypts the local
CFW SELF with an exact roundtrip. The SELF has an intentionally invalid Sony
ECDSA signature, as in the existing CFW repacker. Repacker, decryptor and
PPC encoder are unchanged text copies from `experiments/netemu_disc`; that
experiment's `build.py` and optical source are never imported or executed.

The parent may run this **only after the sole JVM is available**:

```powershell
python -B .\experiments\netemu_autoreturn\validate_pc.py --allow-jvm
```

The validator itself has no console access. It executes the final hook,
trampolines, relocated stack update and compiled C. It models the native
refresh body after that update and the clock, and models `sync` ordering.
It checks eight arguments, native return, stack/backchain, incoming/native
TOCs, LR, GPR13–31, CR2–4, each executed store and tracked RAM store ranges.
Cases cover both timer gates, initial/active/mid-callback invalid guards,
foreign/partial/stale mailboxes, HDD busy/retry, backward/wrapped clock,
publication-before-request and one-shot behavior. Floating/vector state is
unused by the payload; no whole-emulator scheduling is modeled.

The mailbox occupies exactly `930F20..930F80`:

| Offset | Meaning |
|---|---|
| 00 | Magic `4155544F52544E31` (published last) |
| 08 | First guarded nonzero clock sample |
| 10 | Last accepted clock sample |
| 18 | Subsequent callback count, saturates at 100 |
| 20 | Phase: 1 armed, 2 requested, 3 disarmed |
| 28..5F | Seven reserved zero words |

Initialization requires all 96 bytes zero, reason zero, the fixed UI backend
slot `306FC68 == 30700D0`, fixed backend vtable `30700D0 == 949CB8`, and the
unmodified p16 HDD idle predicate. No loaded pointer is dereferenced. Unknown
mailbox contents are left alone. The delay starts when these conditions hold,
not at emulator boot; they do not prove the carrier has reached gameplay.

At least 20 seconds (79.8 MHz clock) and 100 **subsequent** callbacks must
pass. UI/reason invalidation or backwards time disarms the active session;
normal HDD busy traffic defers the request until an idle sample. The final
guards are checked again; phase 2 is stored before a full `sync` fence and
the one-byte reason-2 store at `934161`, with another reason-zero check
immediately before that store. Clearing the reason later does not rearm.

**PROVEN in this offline build:** compile, exact input hashes, 1,056-byte
payload, exact ELF patch scope, no segment changes, IR/assembly store audit,
SELF section HMAC checks and exact decrypt roundtrip. See the private
`local_only/autoreturn_build_review.md` and machine-readable build/audit files.

**INFERRED from prior stock analysis:** the periodic `BAD80 → BAF10 → BC168`
path has no lock held; native TOC/clock and relocation match the Buzz pattern;
reason 2 is observed by stock workers and reaches ordered cleanup/GameOS.

**UNKNOWN / NOT TESTED here:** actual PPC execution of this build, callback
execution without a controller, serialization under real scheduling, races
between guard reads and native teardown, UI setup omission, worker response,
complete HDD writeback, and return to GameOS/XMB. The HDD predicate is only a
momentary sample, not a lock. No bounded return or recovery from a stuck
worker is promised. The callback never calls `111A7C`, `27C3B0`, `1123B8`,
`12D420`, or sysmgr helpers. Stock cleanup must remain stock-controlled.

The parent must inspect a passing PPC result before deciding whether to use
the existing proven installer for one carrier test. This directory supplies
no installer, launcher or hardware test runner.
