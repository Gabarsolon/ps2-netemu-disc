# P0G: softemu physical-disc path and the netemu partition

**Verdict — INFERRED:** softemu supplies a useful design for a small netemu optical backend, but a binary transplant is neither sufficient nor shown to fit. Its physical-driver span is **PROVEN (PC)** to be 6,120 bytes; the controller-plus-driver span is 23,980 bytes, exceeding the 14,320-byte slot. A selective rewrite is **INFERRED** to need approximately 10–14 KiB of code plus separately allocated RAM, with final fit **UNKNOWN**. The immediate blocker remains a permitted optical lifecycle in the netemu partition: **PROVEN (owner)** P1b's open-enabled lifecycle powers the console off; **UNKNOWN** which instruction fails. Authentication is a separate requirement: **INFERRED, instruction checked**, softemu requests service `0x5000`, operation `0x5005`, over virtual UART 10, then reads sectors through LV1 248 ATAPI. Netemu needs both usable optical-device ownership/state and access to that authentication service; copying READ commands cannot supply either. A launch-profile/resource-policy difference between `0x8202` and `0x8204` is the leading **INFERRED** explanation, not a demonstrated LV1 ACL or a proven fix.

**PROVEN / INFERRED / CLAIMED / UNKNOWN convention:** PROVEN identifies performed byte/decoding checks or explicitly attributed owner observations; INFERRED identifies static meaning/control-flow reconstruction; CLAIMED identifies an unverified external assertion; UNKNOWN identifies unresolved behavior. A labelled paragraph or table carries its label to its contents. Static analysis does not establish successful hardware execution.

**PROVEN (work performed):** static/local work only; no PS3, phone, LAN device, installer, game, or console application was contacted or run. No git mutation was performed. Projects, raw inventories, Ghidra listings, decompilations, validation results and the whole-chain explanatory pseudo-C are under `local_only/analysis/p0g/`. Sony-derived output remains in `local_only/`. The separate P1c worktree was not edited.

**CLAIMED:** the video summarized in [P0F](P0F_SOFTEMU_AND_COBRAUSB.md) demonstrates a patched later softemu playing original discs on a downgraded slim. That is not a hardware validation of this 3.55 ELF, the owner's 4.93 partition, or a netemu port; those outcomes remain **UNKNOWN** here.

**PROVEN (PC input identity):** these are the official 3.55 inputs, not P0D's community builds. Softemu's source SELF MD5 is `f95cc406bf1b4ec44481bae1195ca94c`.

| Input | SHA-256 | Native TOC |
|---|---|---|
| softemu 3.55 | `e92f70fcdd1e94a45a5612224579ae94f24fb0644ba78336a5559a6f23416487` | `0x5c8c00` |
| gxemu 3.55 | `aaf007417c27b0a416bcea315da62721586cf1084544449c1394b39bf8478242` | `0x6765f8` |
| emu 3.55 | `dacd4985acd478221be687c5fe213fc5c3343c66c3747773f67ab099710f5eae` | `0x4e99f8` |
| stock netemu 4.93 | `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3` | `0x751280` |
| VSH 3.55 | `4d146f572f4a55450305b94d7f122221cebe53da4e7b5e7d110531db1df88884` | `0x6f7370`, 32-bit descriptor pairs |

## 1. Hypercall inventory and kernel convention

**PROVEN (PC):** the independent raw-word survey and Ghidra survey agree on all three 3.55 opcode inventories. **INFERRED:** every direct candidate has a locally recovered constant r11; this is not an exhaustive proof against computed/indirect invocation. Full number-by-number comparison and softemu wrapper/caller/site groups are in [P0G_HYPERCALLS.md](P0G_HYPERCALLS.md). Caller counts there are static direct-call lower bounds; unresolved containing functions are explicitly retained.

| Metric — PROVEN (PC), except forwarding interpretation INFERRED | softemu | gxemu | emu | netemu |
|---|---:|---:|---:|---:|
| Raw `sc` opcode words | 516 | 564 | 375 | 557 |
| Direct `sc 1` words | 326 | 317 | 259 | 20 |
| `sc 0` words | 190 | 247 | 116 | 537 |
| Recovered constant high-bit LV1 forwarding sites | 0 | 0 | 0 | 163 |

**INFERRED, local constants checked:** selected storage/platform site counts below summarize the full comparison. Counts span the binary, not just optical. Netemu's 20 direct words include the dynamic bridge and an opcode template; the template is excluded from the full comparison's executable constant counts.

| LV1 number | softemu | gxemu | emu | netemu |
|---|---:|---:|---:|---:|
| 91 repository read | 19 | 17 | 15 | 18 |
| 170 / 171 open / close | 7 / 3 | 6 / 3 | 6 / 6 | 4 / 3 |
| 172 MMIO mapping | 6 | 4 | 3 | 2 |
| 174 / 175 DMA allocate / free | 9 / 3 | 8 / 3 | 18 / 23 | 7 / 3 |
| 176 / 177 DMA map / unmap | 7 / 3 | 6 / 3 | 18 / 23 | 1 / 3 |
| 178 / 179 PCI configuration read / write | 3 / 6 | 2 / 4 | 1 / 2 | 1 / 2 |
| 197 device interrupt connection | 5 | 5 | 3 | 2 |
| 245 / 246 storage read / write | 5 / 8 | 5 / 14 | 3 / 7 | 2 / 6 |
| 248 device command | 2 | 2 | 2 | 1 |
| 249 / 254 async status variants | 3 / 0 | 3 / 0 | 1 / 2 | 3 / 0 |
| 162 / 163 virtual UART read / write | 2 / 1 | 2 / 1 | 2 / 1 | 2 / 1 |

**INFERRED:** softemu uses direct `sc 1`, r11=n, for optical and other LV1 operations. Its ordinary `sc 0` event ABI instead puts the local operation in **r3**: 2 waits, 3 signals. The optical wait mask is `0x800`; auth completion uses `0x08000000`. Neither is a forwarded LV1 call. Softemu's exception vector `0xc00` branches to `0x2000`; that saves native registers and dispatches through low-memory handler state. Handler `0x9ff0` dispatches the small event namespace. **PROVEN (bytes):** `0xc50..0xcaf` is zero in softemu, so netemu's bridge cannot be assumed at that address.

**INFERRED comparison:** netemu instead forwards r11=`0x80000000|n` through `0xc50..0xca0`, with local event calls 7/8. P0E's checked initializers permit both saved privilege states; the bridge does not filter optical IDs or flags. Direct softemu instructions, its r3 event ABI, MSR manipulation, TOC and address mappings are therefore not drop-in netemu primitives. **UNKNOWN:** live bridge state and the fatal instruction in P1b.

## 2. Optical discovery, commands, completion and shutdown

**INFERRED, full instruction ranges checked:** the ordered whole-chain pseudo-C is retained in `local_only/analysis/p0g/optical_lifecycle.pseudo.c`; it includes setup, packets, completion, metadata, auth and the missing optical shutdown. The following are address summaries only.

| Order | Softemu address / behavior — INFERRED |
|---|---|
| Allocate and select backend | Native bootstrap calls `0x86a34` at `0x4aa64`. It requests a 1 MiB partition buffer through `0x3d290`, initializes alternative backend support, and calls optical init `0x88724` at `0x86a6c`. Later `0x85170(controller,1)` installs the physical-backend descriptors. |
| Repository lookup | `0x88758..0x88798` encodes `bus/4/id`; `0x3c40c` uses LV1 91 with repository partition selector 1. Enumerator `0x3dc68(4,5,0,info,~0)` at `0x887c0` selects **bus index 4, device type 5**, starting index 0. The fifth argument is an end index. It does **not** filter port 0. Missing enumeration retries indefinitely with delay `0x2625a0`. |
| Validate info | Actual device ID is `info+8`, saved at `0x16c9bb0`; bus ID at `0x16c9bb8`. Exactly one interrupt is required. Helper `0x3e3c4` is a dump-shaped no-op/counter loop, not a grant. |
| Open | **170 at `0x88814`: `(actual_bus_id,actual_dev_id,0)`**. Port must subsequently be readable, not `-1`; the code does not compare it with zero. No event port, DMA region, MMIO mapping, PCI write or optical claim intervenes before open in this path. |
| DMA | **174 at `0x88850`: `(bus,dev,0x100000,20,0)`**. **176 at `0x88884`: `(bus,dev,buffer_lpar,dma_base,0x100000,0xe000000000000800)`**. LPAR-side buffer is held through `0x16c9a30`, CPU mapping through `0x16c9a28`, size through `0x16c9a20`, DMA base at `0x16c9ba0`. These address spaces must not be conflated. |
| Interrupt/event attachment | **18 at `0x88894`**, **197 at `0x888bc`** using `info.intr[0].id`, then **28 at `0x888d4`** using guest IRQ plug **11**. Handler registration `0x49780(11,descriptor)` at `0x888e8`; descriptor `0x5a0a40` points to `0x889dc`. Event port is at `0x16c9b98`. Setup failures reach fatal helper `0x3c024`, without demonstrated rollback. |

**INFERRED:** enumeration reads `id`, `type`, optional PCI fields, paired interrupt entries, MMIO entries, `port`, `meddling`, `blk_size`, `n_blocks`, and `n_regs`. The scanner only reads `meddling` into info; it does not write a corresponding flag or change ownership. Its `0x3dc68` path makes repository queries, not PCI configuration writes. Other platform/flash code contains 178/179; their presence in the whole inventory does not make them optical prerequisites.

**INFERRED comparison, official inputs checked:** gxemu 3.55's optical initializer is **`0x8d3a0`**, open **`0x8d490`**, with the same `(4,5,0,info,~0)` selection and DMA-before-event ordering; IRQ plug 10. These are different addresses from P0E's community gxemu. Emu 3.55's optical initializer is **`0x222ec`**, open **`0x223b0`**: scanner `0x1d860(5,5,0,...)` selects storage **bus type 5** and ROM type 5; it does not supply a port filter. Stock netemu selects HDD type 0/port 2 through `0x114ea4`, open `0x12bf8c`, then event-before-DMA setup. All these optical/HDD opens use flags 0. P0E's detailed community analysis remains applicable only at its own hashes/addresses.

**INFERRED, register checked:** device wrapper **`0x88b9c`** accepts a command number; its LV1 248 at `0x88c0c` passes `(dev_id,command,0,0,buffer_lpar,buffer_size)` and retains the returned tag. Its identified optical caller at `0x89cb8` uses **command `0x10`**, obtaining a last-LBA value that `0x89c74` increments to a sector count. It is not a separate READ CAPACITY CDB. Public CobraUSB names `0x10` GET_DEVICE_SIZE and `0x11` GET_DEVICE_TYPE; **PROVEN (source/bytes)** those constants exist, but **UNKNOWN** any `0x11` use beyond the inspected call graph.

**INFERRED, register checked:** ATAPI wrapper **`0x88c88`**, LV1 248 at **`0x88d54`**, passes `(dev_id,1,packet_address,0x40,data_lpar,available_bytes)`. The packet has a 32-byte command area, CDB length at `+0x20` (12), block count at `+0x24`, block size at `+0x28`, protocol at `+0x2c`, direction at `+0x30`. Read builders use protocol 3/direction 1; metadata generally uses protocol 1/direction 1. **UNKNOWN:** useful semantics of the remaining packet bytes in this implementation; do not invent populated fields. The common layout and protocol/direction names are corroborated by [Linux ps3rom](https://raw.githubusercontent.com/torvalds/linux/master/drivers/scsi/ps3rom.c).

**INFERRED completion/error behavior:** pending tag `0x3766c8` uses idle sentinel `-2`; completion status is at `0x3766d0`. Both wrappers require idle state and MSR.EE set, mask interrupts across submission/tag publication, then wait on local event `0x800`. Their `0x100` counters bound event wakeups, **not elapsed time** or submission retries. One event wait can block indefinitely. `0x88c88` also spins while another START STOP/GET EVENT command is pending. Transport failure, invalid context or counter exhaustion is fatal, not an ordinary returned read error. Completed ATAPI status is returned to higher layers.

**INFERRED:** IRQ handler `0x889dc` drains **249 at `0x88a34`**, accepts a matching tag or unsolicited tag `-1`, stores status and restores idle state, and stops on `-6`/no-entry. Unexpected tags/errors or 256 drained records are fatal. It acknowledges with **27 at `0x88aa8`**, then signals/defer-signals `0x800`. Timestamp stores are instrumentation, not a timeout. No automatic three-attempt ATAPI submission policy was identified; P0D's corresponding interpretation must not be reused.

**INFERRED, complete for the recovered calls/tail calls to `0x88c88`:** every constructed CDB opcode in this physical backend is listed below. Addresses are builder entries and/or opcode-selection sites, not a listing.

| Opcode | Builder / selection addresses | Short description |
|---|---|---|
| `0x1b` | `0x88e18` / `0x88e60`; `0x89b4c` / `0x89bbc` | START STOP, CDB byte 4 is 2 or 3; the latter is a repeated load/eject test loop with timebase delay. |
| `0x2b` | `0x88ec0` / `0x88f10` | SEEK(10); requested LBA in bytes 2..5. |
| `0x43` | `0x88fbc` / `0x8906c` | READ TOC, MSF bit set, format 2, starting track/session byte 6=1, allocation `0x8000`. |
| `0x46` | `0x89390` / `0x893e0`; `0x89c74` / `0x89d18` | GET CONFIGURATION, allocation `0xffff`; current profile from response bytes 6..7. |
| `0x4a` | `0x89530` / `0x89558`; `0x89a64` / `0x89ac8` | GET EVENT STATUS NOTIFICATION, immediate=1, class request `0x10`, allocation `0x800`; tray helper returns response byte 5 bit 0. |
| `0xad` | `0x88fbc` / `0x892c8`; `0x895a8` / `0x895d8` | READ DISC STRUCTURE; layer byte 6, format byte 7, allocation `0x1000`. |
| `0xbb` | `0x89620` / `0x89660`; `0x89c74` / `0x89df8` | SET CD SPEED, byte 1=1, read-speed bytes 2..3; detection uses `0x2b47`. |
| `0x28` | `0x896c0` / `0x897dc` | READ(10), LBA bytes 2..5, count bytes 7..8, 2048-byte blocks. |
| `0xbe` | `0x89888`, `0x8989c`, `0x898b0`, `0x898c4` in `0x896c0` | READ CD, count bytes 7..8 with byte 6 zero, payload selection byte 9 and subchannel byte 10. |
| `0xd1` | `0x898dc` in `0x896c0` | Vendor-format read of 2064-byte blocks, same LBA bytes, count bytes 8..9. Exact drive-internal vendor semantics **UNKNOWN**. |

**INFERRED negative finding, scoped to this backend/call graph:** no MODE SENSE/SELECT `0x5a/0x55/0x1a/0x15`, READ CAPACITY `0x25`, REQUEST SENSE `0x03`, or additional vendor-auth CDB constructor was found. P0E's emu MODE SENSE/SELECT timer setup is not softemu's initialization. An opcode-like immediate elsewhere in network/embedded code is not another optical command.

**PROVEN (bytes) / INFERRED classification:** optical entries **`0x88960`** and physical-backend finalizer **`0x89f0c`** are return stubs. The three constant softemu 171 sites are **`0x67d00` HDD**, **`0x8c94c` network**, **`0x13f4bc` flash**. The supplied second open **`0x8e08c` is network**, selecting bus 1/type 3 and immediately issuing LV1 191; it is not another optical open. **UNKNOWN:** indirect/partition-wide optical teardown. No optical unmap/free/close implementation can honestly be copied from these sites. A new backend needs its own cleanup design.

## 3. Disc authentication: secure service, not an ATAPI unlock packet

**PROVEN (PC):** CobraUSB's softemu names match the functions at `0x8b2bc` and `0x22130c`; the official gxemu names match `0x8ff8c` and `0x24f774`; emu matches `0x2053c` and `0x5111c`. **INFERRED:** their request/response behavior follows below. Complete decompilations and annotated reconstruction stay local.

**INFERRED:** **`0x8b2bc` constructs a `0x70`-byte request and writes it to VUART 10**, through `0x42c74`; **LV1 163 is at `0x42cb0`**. It does not call `0x88b9c`, `0x88c88`, or another optical device-command builder. Its return value 1 means request submission, not successful authentication.

| Request field — INFERRED, stores checked | Value |
|---|---|
| `+0x00`, `+0x04`, 32-bit | `0xface`, `0x5000` |
| `+0x08`, `+0x0c`, 32-bit | `0x60`, `0x60` |
| `+0x10`, `+0x18`, 64-bit | **`0x5005`**, `0x5000` |
| `+0x20`, `+0x28` | Zero 32-bit / zero 64-bit fields |
| `+0x30`, 64-bit | `0x1020000401000001` |
| `+0x38`, `+0x39` | Second/third function arguments, low bytes |
| `+0x40`, 32-bit | Fourth function argument; default from caller is **`0x4b`**; semantic meaning **UNKNOWN** |

**INFERRED:** caller **`0x22130c(a,b)`** maps first argument `0xffffffff` to zero, second argument `0xffffffff` to `0x4b`, invokes the request with byte argument 0 and callback descriptor **`0x5befc8` → `0x2215b8`**, then waits for event **`0x08000000`** at `0x221364`. Receive helper **`0x8ae28`** accumulates bytes using `0x42d14`, **LV1 162 at `0x42d34`**, and invokes the saved callback when complete. Callback `0x2215b8` stores the response pointer/length and signals/defer-signals that event. No elapsed-time auth deadline is visible.

**INFERRED:** the synchronous caller reads a 16-bit response status at `+0x22`, flags at `+0x38`, and conditional 16-byte results at `+0x40/+0x50/+0x60` for flag bits 4/2/1. It reverses selected eight-byte portions for guest use and masks the first five bytes with a nonzero timebase byte. It publishes flags/mask in guest CDVD security state. It returns **0 only for status zero and nonzero flags**, otherwise **-1**. These returned data are consistent with disc security/key material; their cryptographic interpretation and the service's drive-internal commands are **UNKNOWN** from these ELFs.

**INFERRED, setup checked:** native UART setup `0x42e34` configures VUART interrupt delivery through **166 at `0x42e50`**, binds IRQ plug **`0x15`** through 28, configures ports including 10 through 164/165, and registers handler descriptor `0x598280` → `0x42b74`. The dispatcher recognizes UART-10 pending state and calls `0x8ae28`. This is separate from optical IRQ plug 11. It occurs after optical init in the traced bootstrap, not as an optical pre-open grant.

**INFERRED ordering and failures:** physical-backend selector 1 is installed by `0x85170`. Its media-identification path `0x87be0 → 0x86714` reads PVD sector 16, root-directory sectors and `SYSTEM.CNF` through the physical read callback; parser `0x8603c` then invokes default auth at **`0x86654`**. Default auth is also invoked by security helper `0x84e50` at **`0x84ef4`**; explicit guest auth dispatch calls it at **`0x8796c`**. Consequently there is **no demonstrated universal auth-before-first-data-read gate**. **UNKNOWN:** the globally earliest auth/read ordering across concurrent guest requests and the AUTH worker. Missing `0x5005` is a plausible missing security operation, not proof that it alone explains the LV2 probe's data-read failures.

**INFERRED:** the three immediate call sites above do not test the caller's returned status to conditionally terminate boot. Failed auth leaves status/flags reflected in security state; it does not grant keys or prove ordinary reads will succeed. UART transport/invariant failures can reach fatal helper `0x3c024`; a missing response can block. **UNKNOWN:** every game's subsequent response to failed security commands, and the privileged service's exact rejection policy.

**INFERRED comparison, official binaries independently checked:** gxemu **`0x8ff8c`** builds the same `0xface/0x5000/0x5005` request, same `0x70` length and magic, using VUART writer `0x494a4(10,...)`; `0x24f774` has the same default `0x4b`, response flags/key copying, masking and success condition. Emu **`0x2053c`** sends the same service/operation/length/arguments through `0x1e288(10,...)`, with a sequence value rather than softemu's fixed header marker at the first word. Its caller **`0x5111c`** normalizes defaults, waits, and returns its callback-populated result. These functions do not establish a vendor ATAPI authentication CDB. The secure service implementation lies outside the analyzed emulators.

## 4. Guest CDVD boundary, media handling and port size

**INFERRED, descriptor stores and targets checked:** backend selector **`0x85170`**, physical branch `0x852a4..0x852f4`, supplies this useful boundary:

| Slot / descriptor | Physical implementation |
|---|---|
| `0x16c9b48` / `0x5a0ba8` | `0x89c74`: media/size |
| `0x16c9b40` / `0x5a0b78` | `0x89a64`: event/tray status |
| `0x16c9b38` / `0x5a0ad0` | `0x88fbc`: TOC/disc structure |
| **`0x16c9b30` / `0x5a0b60`** | **`0x89924(offset,lba,count,mode)`: sector reads** |
| `0x16c9b28` / `0x5a0ab8` | `0x88ec0`: seek |
| `0x16c9b20` / `0x5a0aa0` | `0x88e18`: load/eject |
| `0x16c9b18` / `0x5a09f8` | `0x88964`: clear media state |

**INFERRED:** the guest controller state machine **`0x88328`** calls **`0x86b08`**, whose normal-read branch invokes that sector callback and limits each command to **`0x80` sectors**. After a read, `0x85c58` prepares sector layout and `0x87340` transfers staging data through guest DMA channel 3; `0x86d88` models transfer timing. This is native emulator code serving the emulated PS2 controller, not PS2 code directly issuing LV1 calls.

**PROVEN (PC table decoding) / INFERRED mode meanings:** `0x896c0` uses relative dispatch table **`0x89758`**. The independently checked supported entries are:

| Mode | Bytes/sector | CDB / selection |
|---|---:|---|
| 0 | 2048 | READ(10) |
| 1 | 2328 | READ CD, byte 9=`0x10`, byte 10=0 |
| 2 | 2340 | READ CD, byte 9=`0x78`, byte 10=0 |
| `0x10` | 2352 | READ CD, byte 9=`0xf8`, byte 10=0 |
| `0x11` | 2368 | READ CD, byte 9=`0xf8`, byte 10=2 |
| `0x20` | 2064 | vendor `0xd1` |

**INFERRED:** LBA is copied directly into big-endian CDB bytes 2..5. This builder does not add a layer offset or a fixed `0x30000`; upper controller input is already a logical LBA. DVD TOC helper `0x88fbc` requests physical disc structure with `0xad`: selector 0 uses layer 0/format 0, selector `0x10` layer 1/format 0, selector 1 format 4. For format 0 it clears `0x810` output bytes and places 17 returned physical-format bytes at output `+0x0c`. CD TOC uses `0x43`, converts up to 102 eleven-byte records to ten-byte guest records with BCD MSF, and stops on a B0 record. **UNKNOWN:** all downstream DVD-9 guest transitions and every uncommon disc-layout corner case; the small builder alone is not proof of full dual-layer compatibility.

**INFERRED:** media detection `0x89c74` caches size and type; GET CONFIGURATION maps **`0xff60 → 0x12` PS2 CD**, **`0xff61 → 0x14` PS2 DVD**, `0xff50 → 0x10`, generic CD profiles to `0xfd` and DVD profiles to `0xfe`. `0x89390` performs the profile query independently. `0x88964` clears cached media state. `0x89a64` interrogates tray/event state rather than deriving presence from a file handle. **UNKNOWN:** every unsolicited eject/media-change invalidation route; cached fields must not be treated as permanently valid.

**INFERRED, worker registration checked:** bootstrap **`0x4abac..0x4abc0`** registers descriptor `0x5a0980` → **`0x88630`**, name **MECHA**, native slot 2, through `0x49334`. The worker waits on event **`0x200`** and drives `0x88328`. Reads block this worker while interrupts can complete the LV1 request. The bootstrap also registers a separate AUTH worker at `0x4ab98`. The 1 MiB buffer is a staging allocation, not proof of a predictive cache. No independent optical read-ahead/cache-fill loop was identified in the physical slice; chunking and modeled transfer timing are present. **UNKNOWN:** seek tolerance, cache hit rates elsewhere, and real scheduling behavior under a port.

**INFERRED error propagation:** `0x89924` returns byte counts on success and maps completion errors, including `0x02023a00` to `-0x31` and `0x02052100` to `-0x20`. `0x88328` sends negative results to **`0x86f1c`**, which updates emulated CDVD error/status, aborts/reset fields as appropriate, and raises the guest interrupt through `0x54bbc(2)`. This ordinary completion-error path is distinct from the fatal submission/invariant paths. There is no reason to import those fatal policies into a new backend.

**INFERRED port boundary:** preserve netemu's existing guest CDVD controller and replace its image backing. [P0 CDVD notes](P0_CDVD_NOTES.md) identify Cobra open/stat/read at **`0x3960/0x39b0/0x3cfc`**, UFS `raw_read` **`0x1ed5cc`**, and shared I/O worker **`0x12c110`**. A synthetic disc handle needs consistent LIMG/media/sector-count/TOC metadata and byte-offset-to-sector conversion. DVD reads can use mode-0 sectors; raw CD needs the chosen stored stride/skip and track metadata. Do not redirect general UFS reads for unrelated files. **INFERRED, previously instruction checked:** Cobra **`0x3d04` overwrites the backend return with requested length**; a physical backend must also preserve/propagate failures there instead of presenting stale buffer bytes as a successful read.

**PROVEN (PC address measurements):** these are original spans, not a linked payload size; function-body totals omit some switch arms/data and must not be used to promise fit.

| Scope | Span bytes | Recovered entries |
|---|---:|---:|
| Physical init/IRQ/command/ATAPI/sector/TOC/media slice `0x88724..<0x89f0c` | **6,120** | **21** |
| Auth request `0x8b2bc..<0x8b3bc` | 256 | 1 |
| Auth synchronous caller + callback `0x22130c..<0x2215fc` | 752 | 2 |
| UART receive helper `0x8ae28..<0x8af00` | 216 | 1 |
| UART read/write helper span `0x42c74..<0x42d88` | 276 | 3 including a stub |
| Controller plus physical driver `0x84160..<0x89f0c` | **23,980** | **95** |

**INFERRED engineering estimate:** the first three rows total **7,128 bytes** before UART framing/setup, repository/allocator/IRQ integration, bounds/deadlines, cleanup, metadata synthesis, unaligned byte reads, cache policy, relocation and netemu hooks. A selective implementation of approximately **10–14 KiB**, roughly **25–40 small routines/adapters**, is plausible but close to the **14,320-byte** allowance; **UNKNOWN** until implemented and linked. Full controller transplantation already exceeds the slot. Original bytes cannot just be relocated: TOCs, globals, function descriptors, interrupt context and syscall ABIs differ.

**INFERRED required netemu primitives:** independent RW state/tag/status and packet storage; a separately validated DMA/LPAR allocation and CPU mapping; LV1 91/170/18/197/28/174/176/248/249/27 and eventual 177/175/171; IRQ registration/mask management; event wait/signal plus a real timebase deadline/recovery policy; serialized callers and copying to guest/request buffers; VUART-10 send/receive/configuration, response framing and callbacks; allocator-owned cache/staging RAM. The original 1 MiB allocation lives outside code space. Netemu's existing HDD/UFS state, DMA region and IRQ must not be borrowed. **UNKNOWN:** whether netemu's live partition permits the UART service, optical operations or a safe recovery from an outstanding timed-out request.

## 5. Partition ownership and launch arguments

**INFERRED:** softemu's optical scanner/init exposes no extra optical registration/claim operation before 170. Repository partition selector 1 is a namespace selector, not proof of device assignment. Its seven whole-binary opens include USB/platform/PCI/HDD/network/flash clients; those other drivers are not optical authorization steps. In particular, 178/179 with `0x146` belong to PCI configuration handling; no optical write of a `meddling` attribute was found. These findings reinforce P0E's corrections to P0D's MMIO/PCI/flags/fd claims.

**PROVEN (PC extraction/decryption):** `tools/pup_extract.py` extracted `dev_flash/vsh/module/vsh.self` from the owner's 3.55 PUP. Its MD5 is `50ae7f94657387b0590000b7223c24a7`. The existing LV2-only decrypter rejected SELF type 4; an APP-key adapter using the local key vault successfully decrypted it to `local_only/fw355/out/vsh.elf`. VSH descriptors use 32-bit entry/TOC pairs, unlike these emulators' 64-bit pairs. Only targeted VSH listings were completed; there is no claimed full VSH call graph.

**INFERRED, instructions checked:** VSH's launch branch at **`0x1abc30`** gets a parameter pointer from `0x19d448`, sets length **`0x4f0`** at `0x1abc38`, selects **`0x8202` at `0x1abc44`**, and calls wrapper `0x192da4` at `0x1abc7c`. That wrapper issues **LV2 syscall 379 at `0x192db0`**. The branch is selected for the local mode value 5. Getter `0x19d448` reads a global pointer through TOC offset `-0x7d08`. **UNKNOWN:** semantic names of all VSH mode values and every caller populating that block. No `0x8204` selection or literal `ps2_emu.self`/`ps2_gxemu.self`/`ps2_softemu.self`/`ps2_netemu.self` was identified in this 3.55 VSH survey. It cannot establish a modern PS2 Classics launch branch or the lower-level filename-to-profile mapping.

**INFERRED softemu launch parsing:** startup `0x4aa00` invokes **`0x53130(0x636180)`**. It exchanges system-manager messages on VUART 2, requires a returned parameter length **`0x4f0`** at `0x53500`, and parses the received payload at context `+0xc98`, exactly **`0x636e18`**, matching CobraUSB's `arguments_symbol`. This block contains launch/user/controller/card/video/settings data; it does not supply the optical bus/device IDs used by `0x88724`.

| Payload offset(s) read — INFERRED | Width / use visible in parser; semantic names UNKNOWN unless stated |
|---|---|
| `0x000`, `0x008`, `0x00a`, `0x00b` | 64-bit value, 16-bit value, two bytes copied into launch context |
| `0x00c..0x02b`, `0x02c` | 32-byte field and one byte; compare Cobra's marker placement below |
| `0x02d`, `0x02e`, `0x030`, `0x031` | Byte, 16-bit value, two bytes |
| `0x032..0x052`, `0x053`, `0x054..0x094` | 33-byte field, byte, 65-byte field |
| `0x098..0x117` | Sixteen eight-byte entries copied; consistent with controller/user identifiers, exact roles UNKNOWN |
| `0x118`, `0x11a`, `0x11c`, `0x11d` | Two 16-bit values and two bytes; final byte `0x62` normalized to `0x63` |
| `0x11e`, `0x19e` | Two `0x80`-byte card-path fields; nonempty values are expanded with `/savedata/vmc/` into separate context strings |
| `0x220`, `0x224`, `0x225..0x3ad` | 32-bit field, byte, byte plus `0x188`-byte data field |
| `0x3ae`, `0x3af`, `0x3b3`, `0x3b7`, `0x3bb`, `0x3bc`, `0x3c0` | Individual settings byte fields / four-byte copies; names UNKNOWN |
| `0x3c4`, `0x3c8` | Two 32-bit fields |
| `0x4cc..0x4ce`, `0x4d0`, `0x4d8`, `0x4e0`, `0x4e4`, `0x4e8` | Three bytes, 64-bit field, byte, byte, 32-bit field, byte |

**INFERRED:** this lists the parser's read fields, not a claim that all remaining bytes are unused across the entire program. No optical bus/dev/permission field is identified. UART 2's launch-parameter exchange, UART 10's authentication service and the optical LV1 node are separate paths.

**PROVEN (public source inspection) / INFERRED meaning:** Cobra 7.3's `shutdown_copy_params_patched` distinguishes `0x8202` for emu/gxemu/softemu and `0x8204` for netemu. `build_netemu_params` constructs a `0x40`-byte system-manager block: first eight bytes copied, byte 8=3, `--COBRA--` at +9, six bytes from old +`0x118` at new +`0x2a`. It writes a separate boot-parameter file after changing the older block, including marker at +12 and byte +11=3. Its real-optical/netemu branch deliberately fails; it supplies no optical grant. **UNKNOWN:** correspondence to the owner's complete Evilnat 4.93 launch implementation. [Cobra launch/parameter implementation](https://raw.githubusercontent.com/Joonie86/COBRA-7.3/master/486/LITE/stage2/storage_ext.c).

**INFERRED ranked explanations:**

1. **Different LV1 launch resource/policy or drive handover state.** Softemu's ordinary optical open works by design without a visible guest grant, while netemu's repository can expose the same ROM node despite an unusable open lifecycle. Distinct old/new launch paths are established; their actual device grants are **UNKNOWN**. A launch-profile-controlled device list or security-service access is the best current explanation.
2. **Open succeeds, then an event/close/state transition is fatal.** P1b has no observed post-open return phase; it immediately attempts close on success. The ablation localizes the failing lifecycle, not the exact instruction. Softemu opens before event attachment too, so absence of a pre-open port is not by itself an explanation.
3. **Firmware-era or live bridge/context difference.** Softemu 3.55 and netemu 4.93 have different kernels, direct/forwarded ABIs and platform state. P0E's bridge initializer weakens a simple static privilege-denial theory, but does not prove the live trial's state. No fatal-policy diagnosis follows from opcode inventory alone.
4. **Wrong flags/IDs or missing PCI claim.** Weaker: checked selectors/ID namespace and zero flags match working patterns; the owner's ROM IDs were repository outputs 4/2. No traced optical PCI/MMIO prerequisite supports trying configuration writes or arbitrary flags.

**UNKNOWN, decisive gap:** the emulator ELF cannot reveal the LV1 launcher's complete resource assignment or secure-storage service policy. Giving netemu the drive means establishing a launch/handover state in which its actual ROM open, interrupt connection, DMA and commands are permitted, plus a usable auth service. Merely making a node visible, changing the HDD selector, replacing a filename or changing `0x8204` to `0x8202` is not demonstrated to accomplish that.

## Ranked next experiments — proposals only

1. **INFERRED highest-value static follow-up:** inspect the matching firmware's LV1/LV2 launch implementation for `0x8202`/`0x8204`, emulator filename selection, resource grants, drive reset/handover and UART-10 service authorization. Compare exact code paths, not repository visibility alone. **Worst case:** inconclusive analysis/unsupported decryption; no hardware effect.
2. **INFERRED useful read-only evidence:** finish the existing P1c ROM/HDD repository comparison with bounded reads, both return values, interrupt IDs, port, `meddling`, geometry and region tuples. Coordinate with its existing builder; this task changes none of that code. **Worst case if later run:** an implementation or memory fault powers off the console; repository reads themselves issue no drive command and cannot prove assignment.
3. **INFERRED experiment that would distinguish launch ownership:** on the same firmware/hardware, compare one validated open/returned-status/close diagnostic under two known-compatible launch profiles, with the same verified IDs, flags, ABI and separate IRQ state. Capture a durable post-open phase before adding close. A return under only the optical launch profile strongly favors launch policy/handover; an observed return followed by failure relocates the fault. Requires launcher/CFW expertise; do not blindly run an old softemu or substitute the shutdown literal. **Worst case:** immediate power-off, hang or failed PS2 launch requiring restoration/recovery; device state changes on a successful open. No such experiment was built or run here.
4. **INFERRED auth-service experiment, only after ownership is settled:** separately validate VUART-10 setup, request framing, callback buffer ownership, response status/flags and a bounded observation path for the `0x5005` request. Compare preliminary sector-16 reads with authenticated reads in an already permitted lifecycle. **Worst case:** hang/power-off, unavailable secure service, or changed drive authentication state; no intentional media write. A missing reply is not safely solved by freeing a live buffer.
5. **INFERRED backend proof after the preceding gates:** read one 2048-byte sector 16, validate the returned byte count/PVD, then test metadata and a controlled layer-boundary/CD case before implementing caching. Adapt the measured small physical slice to netemu's existing image hooks and repair error propagation at `0x3d04`. **Worst case:** stalled worker/game or console power-off on a bad mapping; a timeout must not reuse/free DMA memory while LV1 still owns the request. Full gameplay, eject safety and final payload size remain **UNKNOWN**.

**PROVEN (PC validation):** `tools/p0g_checks.py` passed input hashes, SELF MD5, independent opcode/site-count agreement, open/wrapper/auth anchors, the zero bridge area, and all six sector-mode dispatch entries. `tools/p0g_metrics.py` recorded measured spans. Python source compilation passed. The main analysis uses pyghidra/Ghidra 12.1.3, JDK 21, `-Xmx3G`, one P0G JVM at a time, with its own projects. **UNKNOWN:** all new runtime behavior; no port, console probe, installer or deployable emulator was produced.
