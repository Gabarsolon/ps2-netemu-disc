# P0D: how the PHAT PS3 PS2 emulators read a PS2 disc, and portability into ps2_netemu

**Status: this doc is static-analysis only (PC side, pyghidra on community ELF sources). No console or emulator code was touched. Claims are marked PROVEN / INFERRED / CLAIMED / UNKNOWN.**

Sources analyzed:

| file | sha256 first8 | origin | caveat |
|---|---|---|---|
| `local_only/variants/ps2_emu.elf` | `3af1ba14` | community archive, TOC 0x4eb8c0 | **CLAIMED (blabla.txt):** community-modified build (config cmds 0x4E/0x4F, modded BIOS). Disc-read code assumed untouched — UNKNOWN |
| `local_only/variants/ps2_gxemu.elf` | `365769d7` | community archive, TOC 0x678548 | **CLAIMED:** community-modified build (temperature display). Same caveat |
| `local_only/stock.elf` (netemu) | — | proven stock reference | baseline for comparison |

Tooling: `tools/p0d_ghidra.py` (decompile/listing per address, `local_only/analysis/p0d/<variant>/`), `tools/p0d_inventory.py` (LV1 site inventory, `inventory_summary.json` / `inventory_tables.md`), `local_only/p0d_tmp_check.py` (throwaway TOC/opd/xref probes, keep or delete).

## Verdict

**INFERRED (overall):** the PS3's *phat* PS2 emulators (`ps2_emu`, `ps2_gxemu`) drive the physical drive **directly from the Cell OS level** with plain LV1 storage calls — they enumerate the drive in the HV repository, open it with LV1 170/171, DMA-map it (174/176/172), issue SCSI-style block read commands through **LV1 248 `send_device_command`**, and on top of that run their own read cache and even an **ISO9660/SYSTEM.CNF boot parser** (debug string "Cannot find SYSTEM.CNF"). They do not need (and do not show) any guest-side or HP-syscon mechacon trickery for reads.

For our goal this is the best possible news *in principle*: the entire "read PS2 media straight off the drive" path is expressed with a small, fixed set of LV1 calls (91/170/171/172/174/176/177 + 245/246/248/249) that **stock ps2_netemu already links and partially uses** — netemu already has the flash-device variant of the same routines (`fn_001e9ba0`) and direct forwarding for 245/248/249. What is still UNKNOWN (and console-test territory) is the slim's PS2-media sector readability itself, which P0B/P0C address separately.

## 1. Hypercall inventory vs stock netemu (PROVEN)

From `inventory_summary.json` / `inventory_tables.md`:

| metric | netemu (stock.elf) | ps2_emu | ps2_gxemu |
|---|---|---|---|
| total `sc` words | 557 | 374 | ~317 |
| direct `sc 1` (lev1) sites | 20 | 259 | (17× LV1 91 alone, see below) |
| forwarded guest-sc sites (`r11 = 0x80000000\|n`) | 163 | **0** | **0** |

- Both PHAT emulators call LV1 **directly** (`sc 0x1` with a constant r11) with no forwarding bridge. netemu's 163 forwarded sites are the guest→HV bridge (PS2 guest code calls 0x80000000|detected-number, netemu's handler remaps to a real LV1 call). **PROVEN.**
- LV1 numbers used by ps2_emu (site counts, PROVEN): 91, 168-177 family, plus the GELIC family 185-194 (e.g. `fn_00027f1c` touches 186/188/190/193 on a GELIC device struct) — GELIC numbers absent from stock netemu (netemu has no network need).
- ps2_gxemu direct site counts (PROVEN): console 26×2, RV 91×17, 170×6, 171×3, 172×4, 174×8, 176×6, 177×3, 245×5, 246×14, 248×2, 249×3, 178×2, 179×4. M mins from Linux `lv1` ABI public table: 91 = `lv1_read_repository_node(lpar_id, n1..n4; v1,v2)`, 170 = open, 171 = close, 172 = map mmio, 174 = alloc DMA region(?), 176 = map DMA, 177 = map DMA(?), 245 = `storage_async_read`, 246 = `storage_async_write`, 248 = `storage_async_send_device_command`, 249 = `storage_async_get_async_status` (numbers per Linux `ps3_repository.c` / `ps3.h`, fetched copy at `C:\Users\remus\AppData\Local\Temp\opencode\ps3_repository.c` + `.h` — **suggested: re-save into `local_only/research/` since Temp is volatile**; the Linux LV1 245/248/249 signatures match how the emulators call them. **PROVEN for ABI shape of 245/248/249, INFERRED for everything else.**)
- **Undocumented pair 178/179** (not in the Linux table): used by BOTH phat emulators AND by stock netemu (netemu sites 0x1e9ed8 / 0x1e9f20 / 0x1e9f50 inside the flash scanner fn_001e9ba0). Pattern (PROVEN across all three):
  - 178 called with `(u32`id`, u32 pci_bus, u32 pci_dev, u32 pci_func, 0, 4)` — looks like a "validate/claim device instance" probe; exact semantics **UNKNOWN**.
  - 179 then called with a small buffer; the code **stores 0x146 at buffer+4 and 0 at buffer+0xc** — same magic 0x146 in both netemu and ps2_emu. **UNKNOWN** (0x146 might be a "storage command class" or an "IRQ register" magic).
- psdevwiki HV_Syscall_Reference not yet cross-checked for 178/179/246 names — **TODO**.

## 2. How they open the optical drive (ps2_emu, PROVEN; gxemu assumed symmetric — UNKNOWN)

All addresses in `local_only/analysis/p0d/ps2_emu/`.

**`fn_0001d954` — the repository storage-node scanner** (≈ stock netemu's `fn_001e9ba0`, same code shape):

```
for bus in 0..:                       # ('bus',i) from LV1 91, lpar_id hardcoded 1
    ('bus',i):('type') / ('id') / ('num_dev')
    per-device: ('pci_bus') ('pci_dev') ('pci_func')
    call undocumented LV1 178(id, pci_bus, pci_dev, pci_func, 0, 4); compare result to a constant
    call undocumented LV1 179(...)     # stores 0x146 at +0x4, 0 at +0xc
return (id, num_dev) of first match
```

Matches the netemu flash variant (`d954(5, 0xe, 0)` = bus 5, device type 0xe). **PROVEN** (same structure, same 0x146 write).

**`fn_0001d400` — the "board/SB" open** (caller: `0x49b8` inside `fn_0000477c`, early init):

- `d954(1, 1, 0xffffffff820e104d, ...)` — bus 1, then checks the device id against constant **0x820e104d**; then LV1 170 open + 174/176/172 helpers (`fn_0001dd14/0x1dd90/0x1df14`) and maps mmio region 0x2e. Purpose: probably detecting an SB/RTL chip style (0x820e104d could encode an SB chip code + PS3 board rev). **UNKNOWN what this device is** (not the disc path; possibly RSX/GELIC-adjacent). Marked for P0D follow-up only if P0D §3 turns out to need it.

**`fn_00022460` — drive open for the disc chain:** `d954(5, 5, 0, ...)` → returns (id, n) → maps DMA segments into the **global drive-context struct** at `PTR_004e4568`-idx (stores to +0, +8, +0x10 …):
- ctx+0x00/0x08/0x10: DMA segment descriptors (r5/r3 of LV1 174/176)
- ctx+0x18: **device fd** (result of LV1 170 → passed to 248/245 as first arg)
- ctx+0x20: a 0x78-byte per-command "packet" holder (memset before each use)
- ctx+0x40/+0x48: mode-page values (set by the MODE SELECT fn below)
- ctx+0x50..0x70: the read-cache line (base fd/offset/sectorsize/length)
- ctx+0x28: another fd stored when the 170 succeeds twice (see fn_0001d400.c)

**Callers of `fn_00022460` and `fn_00022ac4`:** **no direct `bl`** in text.asm — they are reached through opd/function-pointer tables. Exact dynamic call sites **UNKNOWN** (but opd entries exist in the 0x4c5xxx region and text.asm lists them as DATA refs, e.g. `from 0x004c54b8` for 0x22138). All read/state-store diagnostic behavior is exercised through those pointers, so the chain is PROVEN alive even without the entry point being named yet.

## 3. The read layer (fn_00022ac4): SCSI-style block commands via LV1 248 (PROVEN)

This is the actual "how sectors get off the disc" code. ABI (from the ppd/disasm around 0x22ac4):

```
fn_00022ac4(buf, len, ...):  # read path
  if len == 0:                  → nothing to do
  brick_sz:  sector size (0x800 for CD/DVD 2048, 0x810 for CD XA 2064, ...)
  max thesis: 0x70000 / brick_sz   # 448 KiB max per command chunk
  loop over chunks:
      build a 12-byte CDB on stack:
        if brick_sz == 0x810:  CDB[0]=0xD1   # SONY vendor read for 2064 (XA) sectors — UNKNOWN exact form
        else if sector_size < 0x800:            CDB[0]=0x28   # READ(10)
        else:                                   CDB[0]=0xBE   # READ CD (raw 2352) — appears for size ≥ 0x800 too
        CDB[2..5] = LBA (u32 BE)
        CDB[6..7] = blocks (BE, up to max)
        CDB[8..9] = rx-holder/ctx? values
      fn_00022138(cdb, 0xc, ctx+0x18 + 0x10000, brick_sz, chunks, 3, 1, 3)
      fn_0000d574(guest_dst? or EE-side buffer at ctx+0x20 + LBA*brick_sz + 0x10000, ...)
```

The wrapper `fn_00022138` (PROVEN):

```
memset(ctx+0x20 (0x78 bytes), 0)
ctx+0x30 = a8, ctx+0x20 = arg2 (0xc len), ctx+0x2c = arg7, ctx+0x24 = arg6, ctx+0x28 = arg5
bl 0x00002f38                                    # disable/switch LPAR state
r11 = 0xf8  # LV1 248 send_device_command
r3 = ctx+0x8 (device fd), r4 = 1, r5 = ctx?, r6 = 0x40, r7 = arg3, r8 = arg4
sc 0x1
loop r31 times (arg9 = 3):
   check result == 0x4000 → success path (return)
   fails → wait: sc 0 with r3=1, r4=0x4000 spin; then re-check ctx+0x3c status; on 0 retry, else return error
```

At the end it mats `mtmsrd r28` to restore state (the code ran with the LPAR-state switched around LV1 248 — same pattern as stock netemu's flash / HV-tagged IO helpers), stamps a `1` wait on `dec` (the "0x4000" pattern) — the tail's `sc 0x0` is a tiny barrier. **PROVEN** that it hits **LV1 248** with the device fd first arg.

The dt惊人的 pattern (3 = 3 retries, "0x4000" = the ready mask) matches the LV1 248 event-wait you get in Linux drivers (`ps3vuart`/`ps3disk` upstream uses 0xf8 with similar re-tries). So: **the drive is commanded with SCSI-style CDBs over LV1 248, with a fixed 3-retry, 0x4000-ready mask, and results DMA-copied into the EE-side buffer at ctx+0x20 + LBA*sectorsize**. The "0x10000" offset is the LV1 "device region 0 + 64KB" pattern (matches Linux `ps3disk`'s use of region+lpar-units).

### The little command set actually issued (PROVEN list, CDB bytes from the disasm)

| fn | CDB[0] | meaning | extras |
|---|---|---|---|
| `fn_0002291c(param)` | **0x1B** | START/STOP UNIT: byte4 = 2 (eject) or 3 (load) | direct-bl caller `0x1a708` (only one) |
| `fn_00022460` @0x2267c | **0x5A** | MODE SENSE(10): page 0x1A, alloc 0x14 | byte6 = ctx+0x40-related value |
| `fn_00022460` @0x22780 + `fn_000227ac` @0x228ac | **0x55** | MODE SELECT(10): PF=0x10, param list 0x14; data page code 0x1A (len 0x0A) + two u32s from ctx+0x40/0x48 | direct-bl caller `0x20c78` (only one) |
| `fn_00022ac4` (read) | **0x28** / **0xBE** / **0xD1** | READ(10) / READ CD / 2064-byte vendor read | many sites |
| `fn_00022ac4` (read, 0x3...) | **0xD1** | raw XA read for 0x810 sectors (also site `fn_00022e04` @0x22e08, min 4 = 8 of `fn_00022138`'s direct-bl callers) | |
| `fn_00023954` @0x23a2c/0x23b04/0x23c90 | **0x28** | READ(10): `uVar18`-style LBA read of a directory record | 3 sites |

**fn_00023954 — the ISO9660 boot lookup (PROVEN, but entry point UNKNOWN):**

```
memset local_buf
CDB[0]=0x28, LBA=uVar10 (u32 BE), blocks=1, brick=0x800
for uVar16 in 0..:                        # start LBA = 0x10 (primary volume descriptor heuristic; code reads uVar10 from a descriptor result)
    send 0x28 read(1 block), copy result to ctx+0x20+0x10000
    scan the sector's ISO9660 directory records for the name "SYSTEM.CNF"
      (match via heap string PTR_s_SYSTEM_CNF_004e4618)
    if not found within 2 records/sectors: print "Cannot find SYSTEM.CNF" and bail
    else: read the record's extent LBA from bytes [6..9] (bVar2..bVar5)
    read that extent (again 0x28 / 0x800)
    call fn_00023794(sector, param_1) → parse SYSTEM.CNF (BOOT2 path bytes etc.)
```

**UNKNOWN:** entry point (no direct `bl 0x00023954` / `bl 0x00022ac4` in text.asm; both are only referenced from the opd/function-pointer tables — a P0F/patch must supply these routes).

### The "pata" / VirtualHDD layer (PROVEN strings)

- `# pata: VirtualHDD path=%s sectors=%d FF_Flg:%d`
- `# pata: ignore lba=0x%X sectors=0x%X`
- `# pata: ufs_read error!` / `# pata: ufs_write error!`
- init code `fn_00028da8` (caller: `0x2a258` inside `fn_0002a244`) maps a second ctx (the ~0x28da8 init from `fn_0002a244`'s read region) — this is the "pata" side that serves the emulated PS2 **IDE/ATA** interface for the guest, reading from a **filesystem-backed virtual HDD** and from the **disc module** if the "call the disc layer" path is chosen.

## 4. The CDVD abstraction (PROVEN strings, INFERRED architecture)

Debug strings inside ps2_emu (and the same module names in gxemu / stock netemu):

```
# cdvd: start !
# cdvd: detected=%02x leadout=%x
# cdvd: unknown intr tag=%lx err=%d
# cdvd: obsoleted...
# cdvd: ss error state=%02x
cdvd_driver / cdvd_ee_driver / cdvdman Init / " No cdvd driver \n"
"cdvd driver module version 0.1.1 (C)SCEI"
"sce_cdvd no block IO :unrecognized code %x"
"sce_cdvd block IO :unrecognized code 0x%02x"
```

**INFERRED:** the PS2's `cdvdman`-equivalent is present as an in-guest "IOP cdvd_driver" (the strings it prints come out of the emulated IOP side) and gets its sector bytes from the **Cell-side read layer (§ 3)**. No separate CDVD "mechacon" or "HP" protocol is visible in the read path; authentication appears to happen only at CD-media level, not per command. (This section is the doc's most INFERRED part — flag for the "UNKNOWN" recheck in §7.)

## 5. Portability assessment into ps2_netemu (INFERRED, to be proven by P1 tests)

**What we can copy from the phat emulators, step by step (all inside the LV1 surface netemu already has):**

1. **repository lookup** — call LV1 91 with `('bus',i):('type'/'id')` (aps2 netemu *already does this* for flash with its own `fn_001e9ba0`). For netemu the interesting call is `--type 5` (or whatever a slim's drive reports) → device id. **UNKNOWN:** on the CECH-25xx slim, whether an optical bus/device node exists and is visible to the LPAR (this is exactly what the P1 "enum + open-only" homebrew probe in P0B/P0_STATIC_ANALYSIS.md already sets out to test — the phat analysis here does not change that probe, it only confirms the probe's LV1 number set 91/170/171/172/174/176/245/248/249 is the same surface the phat emulators themselves use).
2. **open + DMA map** — LV1 170 + 174/176 + 172, region numbering copied from phat (`region 0`, `device region 0 + 0x10000` base offsets).
3. **block reads** — LV1 248 with CDBs (0x28 / 0xBE / 0xD1) + the 3-retry / 0x4000-ready pattern, DMA-copied into an EE/SPU-visible buffer.
4. **sector-size + ISO9660 layer** — copy the read-cache line and the 0x800/0x810 handling from `fn_00022ac4`.
5. **eject/load** — `fn_0002291c` 0x1B pattern.

**What netemu already has that phat does not use:** the guest→HV forwarded-sc bridge (163 sites, passing detected numbers through) — netemu is the right one to carry a "disc driver" because it already speaks to the PS2 side; only the drive-leg (`bdvd`) needs to be added.

**Risks / missing information (UNKNOWN, ordered by how much they block):**
- UNKNOWN: the CECH-25xx slim's drive must actually return PS2 sectors (`P0B` measured `8001002F`/`8001002B`; mmCM pre-unlock workaround `P0C`). This is the true blocker; phat analysis ≠ slim-free pass.
- UNKNOWN: exact LV1 semantics of undocumented 178/179 (netemu never uses 178/179 for the HDD read path itself — it uses them in the flash-scanner pairing with `d954`; the same code shape exists in phat for bus 5).
- UNKNOWN: PCI-level "port" / hidden state needed by the drive besides 248 (mechacon writes for "PS2 mode"?). Phat's § 3 shows *no* mechacon write beyond 245/246/248/249 — but phat's drive is a different hardware unit than the slim's (CECH-25xx), so it may legitimately need extra setup netemu's own driver would also cover (`P0B`).
- UNKNOWN: `region 0` numbering and the exact `map` step for the drive (phat: `174` alloc + `176` map into `region 0` is specific to each LV1 dev; netemu's flash map helpers are a known-good template).
- UNKNOWN: the actual CDB layout of 0xD1 (2064-byte) and for 0xBE chunking (CD-DA raw) — unknown but *not blocking for a first P2 sector-16 read* (2048-byte CDB 0x28 is enough to see an ISO9660 signature).

**Feasibility statement (INFERRED, not PROVEN):** if the slim's drive + LV1 expose the optical device to the emulator LPAR at all (P0B/P1), then a netemu patch that (a) opens/mapps the drive once, (b) services netemu's existing virtual-disc backing store (`pata: VirtualHDD`-style) from a new "sector-accurate drive back-end" instead of HDD-is the **cleanest architecture**: the guest sees the same cdvdman, only the sector source changes. This is the plan we already sketched in `docs/GOAL_AND_PLAN.md`; phat analysis *supports* that plan with concrete LV1 call order + CDB bytes + retry pattern.

## 6. webMAN MOD source findings (from subagent research, report in the task conversation — record only summary here)

webMAN MOD (`include/mount/ps2_disc.h`, master @ commit 4502598) provides a "physical disc for PS2 mode" path from **LV2/CFW side, not HV**:

- `mount_ps2disc()` = a **disc-swap shim** (SC_FS_UMOUNT → eject → swap → mount), it does **not** itself read sectors.
- For the "physical PS2 disc" case webMAN mounts the physical drive as `CELL_FS_IOS:BDVD_DRIVE` (device blkfs `CELL_FS_IOS:BDVD`) + ISO9660-style filesystem directly onto `/dev_ps2disc`, using syscall SC_FS_MOUNT (837) with `{has_fs, cellFsMount, cellFsUmount, cellFsUnmount, ...}`. **This does not settle whether the emulator's HV slot can open a disc device — it only shows a "CFW-side file-system mount" being enough when the *emulator* accepts a filesystem-backed disc driver.** (i.e. it does NOT prove PS2-media readability.)
- That was already measured in `P0B_PS2_MEDIA_READ.md` (DOCUMENTED: multiMAN can read `/dev_bdvd` `SYSTEM.CNF`, but the emulator path still fails → sector-accuracy problem is at the emulator-LV1 leg, not the mount).

## 7. UNKNOWNs / TODO

- psdevwiki cross-check for undocumented LV1 178/179 (and for "0x146" magic) — TODO.
- exact CDB byte-9 semantics for 0x28/0xBE reads, and for the 0xD1 vendor order (bytes 1..9).
- The fn_00022138 tail's "0x4000-ready" wait uses `mtmsrd r28` + `sc 0x0` with r3=1, r4=0x4000 — whether this is a **`dec` (decrementer) wait** or a "CSS evflag" clear is unresolved; netemu already implements wait loops of the same shape, so not blocking.
- opd entry route into fn_00022460 / fn_00022ac4 / fn_00023954 (WHO invokes the disc chain at boot: presumably the emulation "operator" after the physical POST check) — TODO; a targeted `p0d_ghidra.py --focus` scan of `fn_0002a244`-region caller `0x2a258` would probably find it.
- Community-modification drift: any risk that the version in this archive drifted from retail (e.g. an EMU-internal change to the disc layer that makes our `ps2_emu` analysis non-representative of a true *phat* build). Mitigation: same analysis on a **stock rip** of `ps2_emu` / `ps2_gxemu` from the owner's own console dump (`/dev_flash/ps2emu/ps2_emu.self` etc.) when one becomes available. Until then all `ps2_emu`/`ps2_gxemu` findings are **CLAIMED-only "unchanged from retail"**.

## 8. Reproduction / toolchain

- Ghidra/pyghidra one-at-a-time, 16c/32t box, JVM `-Xmx3G` (single job), project in `local_only/ghidra/p0d/`.
- Per-variant:

```
python tools/p0d_ghidra.py ps2_emu  --no-analyze --focus --range 0022440 0022e40  # listings + fn decomps
python tools/p0d_ghidra.py ps2_emu  --no-analyze --range 000faa00 000fbe60        # fn for fn_000fbc28 family
python tools/p0d_inventory.py ps2_emu  # / ps2_gxemu / stock: sc_inventory + numbers
```

- Manifests/String dumps: `local_only/analysis/p0d/<variant>/{manifest.json,strings.json,functions.tsv,fn_*.asm,fn_*.c,sc_inventory.json}`.
- `local_only/p0d_tmp_check.py`: quick ELF probes (opd refs / CDB extraction around call sites) — keep while P0D active.
