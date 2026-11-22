# Automatic return control, 2026-11-22

**PROVEN on this console:** one modified netemu run loaded the Buzz! Schools
Quiz carrier and returned to XMB without controller input or a power-plug action.
The stock netemu was then restored through the installer and read-back verified.
**UNKNOWN:** physical-disc boot, full gameplay, and recovery from a stuck worker.

This control removes the need to press controller buttons for this particular
healthy-carrier test. Bluetooth wake already works; accepted Bluetooth HID
button input is still unproven. See [the Bluetooth notes](PS3_BLUETOOTH_WAKE.md).

## Implementation and scope

Text sources live in `experiments/netemu_autoreturn/`; Sony-derived artifacts,
logs and captures stay private in `local_only/autoreturn/`.

The payload forwards the original eight arguments to native host-pad refresh
`0xBC168` and preserves its return. Its added callback performs only bounded
memory checks and a clock read. After at least 20 seconds and 100 subsequent
callbacks, known UI/backend pointers, an unchanged exit reason, and the existing
HDD idle predicate permit a single write of reason `2` to the stock byte
`0x934161`. The regular stock worker/control loop then performs cleanup.

**INFERRED:** the observed return followed that reason-byte path. No live
mailbox capture established the precise request time. This test does not prove
that bypassing the UI's preparatory actions is safe in every emulator state.
It is an experimental control, not a general exit API or a recovery watchdog.

All added persistent stores are limited to mailbox `0x930F20..0x930F80` and
that existing reason byte; other added stores use the stack. No optical
commands, new device ownership, or forced-shutdown calls are included.

## Evidence

- **PROVEN offline, modeled boundaries:** 76 compiled PPC cases checked timers,
  guards, one-shot behavior, ABI preservation and allowed RAM stores. Native
  refresh and clock were modeled in these cases.
- **PROVEN offline, actual native body:** a separate stock/patched comparison
  executed the disabled-provider native refresh body. Its return and native
  writes matched, and the added payload remained inert with UI uninitialized.
- **PROVEN offline:** compile/store audits and exact SELF decrypt round-trip.
- **PROVEN on console:** one carrier launch, network offline during PS2 mode,
  then GameOS FTP returned at about 75 seconds. Direct PS3 HDMI capture showed
  the carrier loading screen and the subsequent XMB. A title screen or gameplay
  was not observed.

Private receipts:

- `local_only/autoreturn/pc_validation_results.json`
- `local_only/autoreturn/native_boundary_validation.json`
- `local_only/autoreturn/console_20261122T153324Z/receipt.json`
- `local_only/autoreturn/console_20261122T153324Z/returned.png`
- `local_only/autoreturn/stock_restoration_20261122.json`

Test SELF SHA256:
`6490a41118d687eef52f65f43236f6764a6d601dca189d8019fb87956737be03`.

Restored stock SELF SHA256:
`bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`.

## Next discriminator

**UNKNOWN:** which alias/mapping or transfer behavior leaves sector buffers
unchanged. Exact firmware parsing accepts the existing 64-byte ATAPI command;
adding Linux's optional trailing field is not supported as a fix. A prior
post-map bus-address log field was misleading: the allocated bus base is the
output of call 174, not call 176. Correcting that telemetry does not establish
the cause of missing data.

Before adding optical work to an automatic callback, establish staging-buffer
ownership and the context needed for safe logging/completion. Do not move the
whole blocking menu probe into the refresh loop or ship the unfinished disc
backend solely because its offline stat/read-return fixes pass.

**PROVEN offline, exact mapping review:** the effective address `0x84000000`
selects VSID 7, producing the mapper's virtual address `0x74000000`. These
are two representations of one translation, not evidence of two CPU aliases.
LV1 replaces requested WIMG bits according to the translated real address;
the allocator's requested coherent bits do not alone prove final attributes.

Stock already uses forwarded read-only call 95 to retrieve four HPTE V words
and packed low R halves. The expected primary/secondary V words are `0x7405`
and `0x7407`; the low R bits can distinguish the final cache attributes.
**UNKNOWN:** those live values on the affected run, the full translated
physical address, and the hardware's currently selected SLB entry. Call 95
does not establish the latter two. Private exact evidence and eight attribute
model cases: `local_only/cache_mapping_finish/report.md` and its receipts.

The scheduling review found native HDD completion in a separate IRQ path,
but synchronous UFS logging has unbounded waits. A candidate snapshot logger
must follow the native ordered shutdown context, preserve its cleanup order,
and document that limitation. Borrowing native CDVD staging memory still lacks
an exclusive ownership proof; a momentary HDD idle sample is insufficient.
