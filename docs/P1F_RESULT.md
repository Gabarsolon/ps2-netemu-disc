# P1f result (console, 2026-10-31)

Build `local_only/p1f/ps2_netemu_p1f.self` (sha256 `abc8eeee...`): LV1 91 read through a byte-for-byte clone of the stock helper `0x111eb8` placed in the code slot (`sc 0` at `0x4858`).

Labels as reported by the owner: `P1F-CLONE DONE rc=SUCCESS v=5(ROM)`, `P1F-STOCK DONE rc=SUCCESS v=5(ROM)`, `P1F MATCH CLONE==STOCK (RC=0 SUCCESS V=5 ROM)`, `ROM B=04 D=02 P=0 ID=4/2 HDD B=4 D=3 P=2 PH=BOTH`. The console did not shut down.

- **PROVEN (console):** a hypercall `sc 0` executed from our code slot works, and returns the same value as the stock helper. The code-slot location is NOT the problem.
- **PROVEN:** the hand-written P1e wrapper (`stdu r1,-64(r1)`, no CR/LR save, outputs kept on the stack, `sc` at 0x4828) powered the console off while the byte-for-byte clone does not. So the defect was in our wrapper's register/stack/CR/LR handling (exact cause UNKNOWN; the stock helper saves CR and LR, uses a 0x80 frame and keeps the out pointers in r30/r31).
- **INFERRED:** the P1b (open on the optical node) and P1d-A (open with invalid bus) crashes came from the same wrapper defect, not from LV1 call 170 or the drive. `open_device` has therefore NOT been tested yet.
- Next: a generic wrapper that keeps the stock helper's exact prologue/epilogue and changes only the argument set-up and r11, validated first with 91, then 170/171 in separate builds (invalid-bus open, close without open, real open + close).
