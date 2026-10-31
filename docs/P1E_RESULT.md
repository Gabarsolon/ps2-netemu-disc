# P1e result (console, 2026-10-31)

Build `local_only/p1e/ps2_netemu_p1e.self` (sha256 `c9cfcea2d218c62f7d6add5d...`, see P1E_BUILD_NOTES): one LV1 **91** (repository read, the call that works through the stock helper) issued through our OWN `sc 0` wrapper in the code slot (`0x4800`, `sc` at `0x4828`) from the menu hook.

- **PROVEN (owner):** the console powered off.
- **INFERRED:** issuing a hypercall through our own wrapper at a code-slot address is fatal, even for a known-good call number. So the P1b (open on the optical node), P1d-A (open with invalid bus) crashes say NOTHING about call 170 or the drive: every hypercall we issue ourselves from this code kills the partition. (Not proven: it could still also be the call 170 in addition; but 170 is no longer the first suspect.)
- Candidate causes (UNKNOWN which): (1) the `sc` instruction at an address outside stock text (some address-dependent check we did not find in the bridge); (2) a defect in our hand-written wrapper (prologue/epilogue, saved registers, the bridge clobbering something the stock helper preserves, e.g. LR/CR); (3) context (hook thread) combined with our own `sc`.
- Static reading by agy: the bridge `0xc50..0xca0` checks only the call number (<256) and a privilege byte (table at 0x238c, bank selected by USPRG0) against SRR1.PR, no SRR0 check; privilege bytes 91/170/171 all initialized to 2. That reading predicts P1e should have worked; it did not, so something in it is wrong or incomplete.
- Next: P1f clones the STOCK helper byte for byte into the code slot (relocated). If the clone also kills the console, the `sc` location matters; if it works, our hand-written wrapper was wrong and the clone is the path to calling 170/171.
