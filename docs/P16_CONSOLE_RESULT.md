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

## Remaining investigation

Keep the successful logger build. Establish a positive control for the temporary
marker in the known GameOS service context, or identify precisely which service
instance/mapping handles the netemu VUART request. Continue from primary ABI and
launch-path evidence; neither another blind bypass nor a flash-resident service
change is justified by these two results.
