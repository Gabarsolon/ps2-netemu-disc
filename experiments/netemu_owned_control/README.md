Owned-memory startup control — offline candidate only
====================================================

No optical command, DMA setup, device open/map, cache operation, thread,
installer, game launcher or hardware access is present in this experiment.
`sync` words are publication fences. No raw MSR write or global lock is added.

Build: `python -B experiments/netemu_owned_control/build.py`

Exclusive offline JVM validation:
`python -B -u experiments/netemu_owned_control/validate_pc.py --allow-jvm`

All generated artifacts go into ignored `local_only/owned_control/`.
The parent must separately precreate a 65536-byte
`/tmp/netemu_owned_snapshot.bin` before any future console test. This child
does not create that console file, install a SELF or run a hardware test.

`owned.h` names the mailbox and owned lease fields. The 96-byte mailbox is
versioned by high word OWN1, with a checksum of its immutable fields in the low
word. This checksum detects partial/changed publication; it is not an
authentication primitive and cannot grant ownership. Fresh ownership comes
only from the single real B9848 call under admitted startup conditions.
`control` holds status in its high word and phase in its low word. Remaining
qwords: A/opaque allocator return, P, E, boot TB, timer start, last TB, callback count, diagnostics,
saved MSR, inside MSR. N is fixed at 8192 for status OWNED. Diagnostics pack
attempt count at bit56, two initial nonzero-handshake-flag indicators at
bits48..49, pre-admission B at bit32 (saturated to4096 on rejection), and low
SPR088 at bit0. On a context decline without trap5, MSR slots are context
readings; otherwise they are the actual saved token/inside reading.

The wrapper at18CB4 passes its actual incoming continuation as a ninth
argument. B9D54 always runs first, once, with all eight native arguments. Only
continuation18CB8, negative signed low SPR088, PR0, acknowledged flags and an
empty mailbox admit the outer trap5. The complete fixed 4096-record validator
runs inside EE0 before the one native request. First-fit prediction additionally
rejects an altered/stale contained return. The actual native allocator,
selector, helper and IRQ wrappers execute in the PC harness. B9D54's body is
modeled; its post-return fixtures originate in actual lazy initialization and
the two native23D0/18 requests. Serialization remains an inference from the
supplied cold-start protocol, not a modeled scheduler or an SMP mutex.

Only initialize() writes dynamic persistent memory: state[A,A+1000),
command[align128(A+1000),+40), data[command+80,+800), all inside the retained
8192 bytes. All lease fields and the full state reservation are initialized.
No borrowed tail or old heap data is exported. The allocation is never freed,
resized or retried. Pool descriptor +18 supplies P; +28 supplies E; +20 is
never used as P. Command/data EA and LPAR bounds/alignment are checked
independently. No5000 prefix, guessed HTAB size or syscall95 is used.

Refresh remains native-first. It runs only bounded checks and the existing
20-second/100-callback timer; no allocation or UFS work occurs there. A clean
decline still permits the normal return and declined snapshot. On rejected or
changed native returns, the A slot contains the exact opaque allocator return
for diagnostics; status forbids treating it as owned or dereferencing it.
Foreign/partial publication leaves stock alone. Validated lease addresses are
kept locally for dependent pattern reads; mailbox reloads cannot substitute
an unchecked pointer. The terminal/consumed phases prevent retries.

Shutdown remains original-first at11243C ->11B9BC. It then makes one
open/stat/write/close transaction against the precreated private file, fd0..7,
exact size65536, 48-byte stat, 512 bytes at offset0. There is no extra flush.
Original112444 ->12D420 is untouched. Native UFS waits remain unbounded;
neither a general watchdog, cold-cache liveness nor durable delivery is proven.

OWNSEC1 consists of64 big-endian qwords. Q0 marker `OWNSEC1\0`, Q1 version/size,
Q2 terminal control, Q3 TB, Q4 native UI object, Q5 reason2, Q6 preserved native
shutdown result, Q7 exact allocator return; Q8..19 consumed mailbox; Q20..41 initialized lease
fields from owned.h (zero on decline); Q42 pattern verdict; Q43..46 first/last
command/data samples; Q47..54 current UI/HDD facts; Q55 fd; Q56..61 stat;
Q62..63 zero. Checksums are unsigned64 additive sums of our fixed patterns.
They are not disc bytes or a physical-sector read.

Decoder:
`python -B experiments/netemu_owned_control/decode_snapshot.py local_only/owned_control/pc_success_snapshot.bin --output local_only/owned_control/decoded_pc_snapshot.json`

Read the private `build_review.json`, `pc_results.json`, `input_review.json`,
store audits and `report.md` for exact hashes, model boundaries and status.
