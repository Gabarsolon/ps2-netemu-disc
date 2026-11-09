# P16 L1 console results (2026-11-09)

## Result

**PROVEN:** the new logger saved a complete fresh diagnostic summary and END
record on both console runs. It recovered a transient UFS-lock conflict without
weakening the disk guard. Authentication still returned `0x0016`, key flags
were zero, and the DMA sector-16 buffer remained all `0xA5`.

Installed diagnostic SELF SHA-256:
`f90f166c5bfc7cc4039b5aa6e298bd0a5fc2e218f8fddee38148ad951519f987`.
Installation used the existing backup/write/read-back/unmount procedure. The
previous W3 SELF was backed up on the PC and console disk. The P16 game-read
path remains stock; the probe runs only from the PS menu.

## Baseline with the existing two RAM patches

Before launch, both existing ss_server1 signature blocks and target words were
checked. Patches at `0x713210` and `0x714710` were applied and read back.
The carrier was the existing Buzz! Schools Quiz ISO, with physical TDU in the
drive. The physical-disc-only Cobra hook was not used.

Artifacts: `local_only/p16_run_20261109_010614/`.

- Fresh log SHA-256:
  `0c1d7a42a9462f23bb4ba89bb28861f308e2f0c86184b740deaa5340c16f771b`.
- Boot ID `0x43e69756`; 35 current records; SUM at sequence 34, END at 35;
  header clean flag 1.
- Reply identity: magic `0x0000face`, opcode `0x5005`; 112 bytes written and
  received, both VUART return codes 0. Auth status `0x0016`, flags 0.
- DMA READ(10), LBA 16: send return 0, async status 0, but all 2,048 bytes
  retained the sentinel. Classification `UNCHANGED`; sample is 32 `a5` bytes.
- Summary persisted on retry 2, after four skipped phase records. Accumulated
  busy mask `0x40` identifies the UFS lock. Saved summary/END telemetry shows
  HDD worker state 2, command 0, completed/expected tags both 0, status40 0.

This run demonstrates the logger recovery on hardware. It does not demonstrate
that the two pre-launch auth patches were effective inside the service handling
the guest request. The static nonzero-completed-tag issue was not observed in
these saved records and did not justify changing the guard during this test.

## Forced-error helper discriminator

A separate run changed only the previously audited helper entry at physical
`0x714638` from stock `f821ff517c0802a6` to
`3860005a4e800020` (`li r3,0x5a; blr`). Complete surrounding bytes were checked
and the temporary word was read back before launch. No additional firmware or
emulator installation was performed. This stub returns an error and skips the
helper's authentication operations if it executes.

Artifacts: `local_only/p16_run_20261109_105836/`.

- Fresh log SHA-256:
  `c4dc2eed3d6c44de86b50dd696d28f2a7cde3171a9ca0c34905f104b0172f8ce`.
- Boot ID `1070321659`; 35 current records, SUM and END, clean flag 1.
- Valid `0x5005` reply still reported status `0x0016`, not `0x005a`. Flags 0;
  112-byte request/reply, return codes 0. Sector buffer remained unchanged.
- The summary again recovered UFS-lock mask `0x40` on attempt 2.
- After the normal quit sequence and XMB return, the helper was already stock.
  The guarded revert therefore performed no write. Both prior branch targets
  also read stock. No auth marker or bypass remains active in the checked RAM.

**UNKNOWN:** whether the negative marker result is due to service-instance or
mapping differences, reload timing, instruction-cache visibility, or another
execution path. Read-back proves data bytes before launch, not instruction
execution in the later guest context. Do not infer an exact reset point from
the post-XMB stock state.

## Additional read-only comparison

At XMB, FTP retrieved 54 bytes from physical TDU `/dev_bdvd/SYSTEM.CNF`, including
a BOOT2 entry. The private copy is in `local_only/p16_lv2_readproof/`. This is
positive evidence of physical-disc file access in GameOS, not proof of sector
access from the netemu partition.

## GameOS positive control

Primary 4.93 code tracing established that syscall 864 does not expose opcode
`0x5005` directly. A separate opcode-`0x5004` helper at physical `0x7147e8`
provides a GameOS control on the same 4 KiB code page as the PS2 helper.
Its original first 16 bytes were checked, the entry was temporarily replaced
with `li r3,0x5a; blr`, and the sentinel was read back.

Only while that entry marker was verified active, webMAN invoked scalar
`syscall864(0x5004,0x46)`. The forced early return skips the helper's normal
drive operations and error-remapping logic. The exact response was:

`syscall2(864) => 0xffffffff8001055a`

This matches the offline proof: status `0x5a` survives the secure-service
executor and serializer, and the kernel wrapper ORs it with `0x80010500`.
The original bytes were restored immediately in a finally block and read back
as stock. No unpatched baseline call to this state-changing mode was sent.

Artifacts: `local_only/p16_host_marker_20261109_111120/`. The fixed-target
tool is `tools/ss1_auth_sentinel.py --target gameos`; six offline tests cover
both targets' signatures, exact rollback, unknown bytes and dropped writes.
The HTTP syscall syntax is documented by the
[webMAN maintainer](https://github.com/aldostools/webMAN-MOD/wiki/Web-Commands).

**PROVEN:** the GameOS service image at the expected physical mapping executed
an injected marker. This is stronger than a data read-back alone.
**UNKNOWN:** the relationship to the emulator's service instance, reload point,
and instruction visibility at its different helper entry. This control does
not turn the earlier guest marker's absence into proof of any one cause.

## Remaining investigation

Keep the successful logger build. With the GameOS positive control established,
identify precisely which service instance/mapping handles the netemu VUART
request and whether a same-helper comparison is feasible. Continue from primary ABI and
launch-path evidence; neither another blind bypass nor a flash-resident service
change is justified by these two results.
See [P16_SERVICE_CONTEXT.md](P16_SERVICE_CONTEXT.md) for the caller-scoped
endpoint lookup and the limits of the GameOS syscall interface.
