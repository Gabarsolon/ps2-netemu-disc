# P0 CDVD analysis notes

Scope: exact prepared ELF SHA-256 `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`; Ghidra listings/decompilations remain in `local_only/analysis/`. These are supplementary findings for `P0_STATIC_ANALYSIS.md`. Static interpretation is **INFERRED**, not console behavior proof.

**INFERRED:** the Cobra-backed native CDVD path already represents both CD and DVD images, but its read hook hides backend errors. This must be accounted for before implementing a physical-disc backend. Whether the emulator LV1 partition can access the real optical device remains **UNKNOWN**.

## Hooks and image metadata

- **INFERRED:** `0x3960` is a TOC-changing trampoline to `0x40bc`; direct native calls are `0x135f70` in image setup `0x135f48` and `0x136ff4` in open/switch `0x136ecc`. `0x39b0` similarly dispatches to `0x3ff8`; direct native stat call is `0x135fac`. Other references are data/function descriptors.
- **INFERRED:** image setup stores the stat size in context `+0x58` (`0x135fc4..0x135fcc`). In its alternate/configured mode it uses `0x137454` and a size read at offset `0x88`, retaining the smaller bound when the read yields eight bytes. Cobra's size hook must therefore supply a consistent full image size.
- **INFERRED:** `0x137454` converts physical container length to logical length with a 16 KiB initial header and 16 KiB overhead per `0x804000`-byte group of 512 16 KiB data blocks. `0x1374a8` resets cached group/block offsets. This is image-container layout handling, not optical sector geometry.
- **INFERRED:** setup requests a `0x4000`-byte LIMG/header read using context `+0x38` offset, `+0x40` destination, `+0x48` count; `sc 0` number 8 sends an event and number 7 waits (`0x135ff4..0x136018`). It then checks result context `+0x50` and the `LIMG` magic.
- **INFERRED:** the LIMG synthesizer is `0x3bdc`: first call zeroes the requested buffer, writes magic `LIMG`, sector count at header `+8`, sector size at `+12`, and media type at `+4`. DVD is type 1 with size divided by 2048; CD is type 2; the raw-CD flag changes sector size to 2352 and count to size / 2352 (`0x3c5c..0x3cb4`). Data flags are at launch structure `+0x804` (CD) and `+0x805` (raw/tracks).
- **INFERRED:** native setup maps LIMG type 1 to native/emulated media value `0x14` and type 2 to `0x12` (`0x13610c`, `0x1360e8`). CD gets per-read data skip `0x18`; DVD skip is zero. Native logical user-sector size is `0x800` in both cases. The raw container stride remains separate.
- **INFERRED:** media presence/open state is modeled separately from the media type. Singleton context `0x2458448` has open bit 0 in its flags word; close helper `0x135ee8` closes the fd, clears that bit, and zeroes context media field `+0x18`. Open helper `0x136ecc` sets the bit only after a successful image open. Media-query helper `0x136414` checks the bit and returns zero when absent, otherwise the media type byte at singleton `0x2458463` (context `+0x1b`, low byte of the big-endian media word). This supports an emulated present/absent distinction. It does not establish a physical tray protocol; exact tray-state transitions remain **UNKNOWN**.
- **INFERRED:** DVD setup reads one image sector at byte offset `stride * 16`, then takes the four-byte field at PVD-relative `+0x54` (the big-endian ISO9660 volume-space-size copy), clamps it to the total LIMG sector count, and stores it at context `+0x20` (`0x136144..0x1361cc`). This distinguishes the first ISO volume extent from total image size, relevant to DVD-9. Exact downstream layer/TOC use needs further tracing.

## Sector request and TOC path

- **INFERRED:** `0x1364f4(context, guest_buffer_offset, lba, sectors, read_mode)` derives output stride, leading skip and user bytes from `0x13227c`, `0x132204`, `0x1321a0`. It checks guest buffer offset + total byte count against `*0x2458430`, then adds the base `*0x2458428`. Invalid requests reach fatal helper `0x111a7c`. There is no new allocation here and no general physical-DMA alignment guarantee.
- **INFERRED:** when requested and stored sector layouts match, `0x136840..0x13686c` submits one bulk read at byte offset `lba * stored_stride`, of `sectors * output_stride` bytes. Otherwise `0x136680..0x1366cc` submits one user-data read per sector, at `lba * stored_stride + stored_skip`, into the appropriate offset of each output sector, followed by sector-header synthesis `0x135a9c`. Each request sends then waits before proceeding: there is one context request slot, not multiple queued CDVD reads in this function.
- **INFERRED:** dispatcher `0x1359d4` calls either descriptor `0x72f8d8` (entry `0x1377c4`, container/Cobra path) or `0x73f2c8` (entry `0x1ed5cc`, direct UFS path), according to context byte `+0x32`. It writes the return to context `+0x50` and clears the pending fields. Each read is synchronous on the dispatcher; the calling CDVD side waits for a separate completion event.
- **INFERRED, register/branch checked:** the native I/O worker loop is `0x12c110` (function descriptor `0x724418`). At `0x12c198..0x12c1b0` it waits through `sc 0`, `r11=7`, for a mask including request event `0x4000000000`; after testing that event it branches to `0x12c4ec`, obtains the singleton CDVD context at `0x135968`, invokes `0x1359d4` at `0x12c4f4`, and sends completion event `0x8000000000` through `sc 0`, `r11=8`, at `0x12c508`. This worker also services other file/storage tasks. A slow optical read would block this I/O worker and the waiting CDVD caller. Maximum tolerable delay and whether other native work continues smoothly are **UNKNOWN** without scheduling/delay tests.
- **INFERRED:** TOC generator `0x135ccc` handles native media `0x14`/`0xfe` separately from CD values. DVD produces `0x810` bytes of synthetic TOC information. If context first-volume sectors `+0x20` is nonzero and smaller than total sectors `+0x1c`, it sets the dual-layer indicator at output `+0x0e` and emits first-volume-end + `0x30000` - 1 at output `+0x15..+0x17` (`0x135e54..0x135e98`). CD produces `0x400` bytes copied from cached ten-byte track entries beginning at native scratch `0x2458440+0x178`; it does not query a physical drive in this routine.

## Error and short-read issue

- **INFERRED, high confidence (direct instructions):** `0x3cfc` calls the raw reader through a function descriptor, but `0x3d04` immediately overwrites its return with the requested byte count. Negative errors and short reads from that backend are therefore hidden by this Cobra hook. The earlier project briefing's blanket statement that short reads are errors must be qualified for this exact path.
- **INFERRED:** native encrypted/container readers `0x1377d4` and `0x137cd0` explicitly check `0x4000`-byte reads, map short reads to `-5`, and set error indicators. Those checks cannot recover a backend failure after the Cobra wrapper has reported full success.
- **INFERRED:** setup rejects a short LIMG/header result, missing magic or image smaller than 16 KiB with `-9`; a negative read is propagated after closing. A mismatched DVD sector-read length reaches fatal helper `0x111a7c` at `0x136214`. With Cobra's forced success these native tests do not prove safe failure handling for a physical drive.
- **UNKNOWN:** full guest-visible error propagation, retry policy, physical timeout tolerance and tray transitions; no console or delayed-read test was run in P0.

## Strings and public cross-check

- **INFERRED:** native `SB_CDVD` string is at `0x301638`, referenced through dispatch record `0x74ba48`. Its pointers `0x134a50` and `0x134bb8` lead to relative-offset dispatch tables, not function entries; another pointer is function descriptor `0x72f128` (entry `0x1328dc`). Many `cdvd_driver`, timeout and DVD-dual strings at `0x953bc0..0xb009a8` are in embedded PS2 guest modules and have no native code references in the current analysis. They cannot establish native ATAPI support.
- **CLAIMED (public source, inspected):** [Cobra 7.3 netemu main.c](https://raw.githubusercontent.com/Joonie86/COBRA-7.3/master/484/REX/ps2emu_stage2/netemu/main.c) uses the same LIMG synthesis, CD offset correction and forced-length return after the UFS read. This corroborates interpretation of the exact stock instructions; public source alone is not proof of this console's behavior.

Remaining static targets: dispatch-table callers associated with `SB_CDVD` for exact tray command semantics, and uses of worker descriptor `0x724418` for thread creation/priority. P1 should remain open-only and label-only; no CDVD redirection is justified by these findings yet.

## Direct raw-read references

**INFERRED:** Ghidra's direct call references to `0x1ed5cc` are listed below. This is a static direct-call inventory, not an assertion that all references are CDVD operations; the Cobra descriptor `0x4530` and direct-UFS descriptor `0x73f2c8` also enable indirect calls.

| Containing function | Call instruction addresses |
| --- | --- |
| `0x1377d4` container reader | `0x1378a0`, `0x137984` |
| `0x137cd0` container reader | `0x137df8` |
| `0x11c894` | `0x11cb54` |
| `0x12c110` I/O worker | `0x12c740` |
| `0x12a528` | `0x12a9bc` |
| `0x2902d8` | `0x290314` |
| `0x11af94` | `0x11b058`, `0x11b168`, `0x11b18c` |
| `0x27cc04` | `0x27cf50`, `0x27cf94`, `0x27d01c` |
| `0x27d04c` | `0x27d0e0` |
| Not assigned a function by current analysis | `0x26b780`, `0x26b7c4`, `0x26b874` |
