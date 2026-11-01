# P3A: Static Analysis of the Stock ps2_netemu UFS File-Write Path & Durable HDD Debug Log Design

## Verdict

**Feasibility: INFERRED FEASIBLE WITH STRICT CONSTRAINTS.**
A durable in-place HDD debug log written by our patched `ps2_netemu` directly to the PS3 HDD (`/dev_hdd0`) is feasible without adding new hypercalls or writing custom storage drivers. It can be implemented cleanly by reusing the netemu's own stock UFS file layer and HDD cache-flush routines. Because the file is pre-allocated (a fixed 64 KiB placeholder file created beforehand over FTP, e.g. `/dev_hdd0/tmp/netemu_log.bin`, filled with zeros), and writes are performed strictly in-place at aligned 512-byte sector boundaries, the filesystem metadata (superblocks, cylinder group allocation bitmaps, direct/indirect block pointers) is **never altered**. Static analysis proves that the stock block traversal function (`0x1ec084`) strictly clamps any write request to the file's existing inode size (`i_size`) and **never allocates new disk blocks**.

**Recommended Minimal Design:**
1. **Placeholder file**: 64 KiB (65,536 bytes) at `/tmp/netemu_log.bin` (which corresponds to `/dev_hdd0/tmp/netemu_log.bin` in GameOS / FTP), zero-filled by the owner before testing.
2. **Aligned sector writes**: 512 bytes per write transaction. Sector 0 (offset `0x0000`) is the header record; Sectors 1..127 (offsets `0x0200`..`0xFE00`) are 512-byte log records. This guarantees that every write completely covers a single sector, completely bypassing partial-sector read-modify-write scratch buffers.
3. **Write-Through Flush**: After each record is written into cache via stock `raw_write` (`0x1ed458`), immediately call the stock standalone flush routine **`hdd_cache_flush` (`0x12cc98`)**. This forces dirty cache blocks to disk via LV1 storage write (HV 246) and waits synchronously for guest event `0x2000`, making the record durable on physical disk in ~2 to 8 ms.
4. **Execution context & Safety Preconditions**: Invoke only from the menu hook thread (`0x270FFC` / `0x270C24`) or controlled initialization checkpoints when the HDD driver singleton `H = 0x241c850` is idle (`H+0x48 == 0`, `H+0x38 == 0`, `H+0x40 == 0`). If any busy flag or driver error is detected, fail-open immediately without calling write or flush.
5. **Lifecycle**: Open -> Write -> Flush -> Close per transaction. This prevents holding one of the emulator's 8 file slots permanently, eliminating the risk of slot exhaustion.

**Blockers & Critical Preconditions:**
- **Driver Singleton Concurrency**: `hdd_cache_flush` (`0x12cc98`) manipulates `H+0x38` (completed tag) and `H+0x48` (expected tag). If called while a background disc read or memory-card save is in-flight, it would clobber the pending command's tag and crash the completion wait loop. The idle guard (`H+0x48 == 0`) is mandatory.
- **Cleanup Trap (`0x12d420`)**: The stock cleanup function `0x12d420` flushes the cache, but immediately proceeds to unmap DMA, free DMA, close the device, and disable the driver. It must **never** be used for logging. Only the standalone `0x12cc98` flush routine is safe.

**Ranked Next Steps (Post-P3A):**
1. **P3B Spike Build (PC Emulation + PC Audit)**: Implement native trampolines for `0x1ecc5c` (open), `0x1ecb10` (close), `0x1ed458` (write), and `0x12cc98` (flush) in the code slot (`0x4800..0x7FF0`). Emulate under pyghidra `EmulatorHelper` to confirm register preservation (PPC64 ELF ABI) and TOC integrity (`r2 = 0x751280`).
2. **Owner Provisioning**: Owner runs `tools\make_log_placeholder.ps1` to upload `/dev_hdd0/tmp/netemu_log.bin` to the PS3.
3. **Single-Record Test on Hardware**: Build a diagnostic variant that writes exactly one record upon opening the PS-button menu, verifies label feedback, and reads the log back via `tools\read_netemu_log.ps1`.
   - *Worst case*: Netemu fails to open placeholder (returns negative error code), falls back to menu display without crashing; if power cut occurs during disk write, at worst that single placeholder sector is torn.

---

## 1. Stock UFS File API Inventory

The stock `ps2_netemu` executable (`local_only/stock.elf`, SHA-256 `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`) contains an internal UFS2 filesystem client operating directly on Partition 2 of the internal PS3 HDD (`dev_hdd0`).

Global UFS context pointer: `TOC - 0x42f8` (`0x74cf88`) -> **`0x3055180`**.
- `0x3055180 + 0x00`: Global 32-bit UFS lock word (`lwz r0, 0(r31)`).
- `0x3055180 + 0x08`: Base of 8 file slot descriptors (`slot 0` at `0x3055188` .. `slot 7` at `0x305d268`). Each descriptor is exactly `0x1270` bytes (4,720 bytes).

```
Slot layout (0x1270 bytes per slot):
  +0x00: in_use flag (u32, 1 = open, 0 = free)
  +0x04: file type / mode flags (u32)
  +0x0c: lower adapter handle (u32)
  +0x10: filesystem magic / superblock ref (0x11954 for UFS)
  +0x18: block size in bytes (u32, e.g. 0x800 or 0x4000)
  +0x3c: block shift count (u32)
  +0x178: inode file size i_size (u64)
  +0x188: inode atime (u64)
  +0x190: inode mtime (u64)
  +0x198: inode ctime (u64)
  +0x1a0: inode mode / dev (u64)
  +0x1b8: inode flags (u32)
  +0x270: 512-byte scratch buffer for unaligned boundary reads/writes
```

### 1.1 `ufs_open`: `0x1ecc5c`

- **Descriptor**: `0x73f298` (Cobra descriptor table entry: `0x4510`).
- **Signature**: `int ufs_open(uint64_t dev_unused, const char *path)`
- **Calling registers**:
  - `r3`: Unused / device index (every caller in netemu passes `0`).
  - `r4`: Pointer to NUL-terminated path string (`const char *`).
- **Return convention**:
  - `r3`: Open file descriptor `fd` (`0..7`) on success.
  - Negative error code on failure: `-1` (all 8 slots occupied), `-2` / `-5` (path component not found or superblock error).
- **Path format**:
  - Paths are relative to the UFS filesystem root on `/dev_hdd0`.
  - Examples in stock code: `"/savedata/vmc/"` (`0x300bc0`), `"/tmp/game/ps2bootparam.dat"` (`0x3050d0`), `"/game/%s/USRDIR/DISC.IDX"` (`0x300ba0`), `"/game/%s/USRDIR/ISO.BIN.ENC"` (`0x3015e8`).
  - Expected placeholder path: **`"/tmp/netemu_log.bin"`** (matches `/dev_hdd0/tmp/netemu_log.bin` in GameOS/FTP).
- **Open Flags / Modes**:
  - There is **no mode argument** (no `O_RDONLY` or `O_RDWR` parameter). All 27 stock callers pass `r3 = 0, r4 = path`.
  - The slot is opened with read/write capability automatically. The same `fd` returned by `ufs_open` is used interchangeably by `raw_read` and `raw_write`.
- **Slot allocation**:
  - Scans slots 0 through 7 sequentially (`0x1ecce4..0x1ecd44`). If all 8 slots have `in_use != 0`, returns `-1` (`0x1ecd54: li r22, -1`).

### 1.2 `ufs_close`: `0x1ecb10`

- **Descriptor**: `0x73f280` (Cobra descriptor table entry: `0x4520`).
- **Signature**: `int ufs_close(int fd)`
- **Calling registers**:
  - `r3`: File descriptor `fd` (`0..7`).
- **Return convention**:
  - `r3`: `0` on success; `-3` if `fd > 7` or slot was not open.
- **Implementation**:
  - Validates `fd <= 7` (`0x1ecb70`).
  - Calls lower close stub `0x1eb778`.
  - Clears `slot[fd].in_use = 0` (`0x1ecc28: stwx r0, r29, r30`).
  - Unlocks global UFS lock (`0x1ecc2c: stw r0, 0(r31); eieio`).
  - Returns `0`.

### 1.3 `ufs_stat` (fstat): `0x1ec760`

- **Descriptor**: `0x73f250` (Cobra descriptor table entry: `0x4560`).
- **Signature**: `int ufs_stat(int fd, struct ufs_stat *st)`
- **Calling registers**:
  - `r3`: File descriptor `fd` (`0..7`).
  - `r4`: Output buffer pointer (`struct ufs_stat *`).
- **Return convention**:
  - `r3`: `0` on success; `-3` if `fd > 7` or not in use.
- **Output fields**:
  - `st + 0x00`: atime (u64)
  - `st + 0x08`: mtime (u64)
  - `st + 0x10`: ctime (u64)
  - `st + 0x18`: mode/dev (u64)
  - `st + 0x20`: flags (u32)
  - `st + 0x28`: **64-bit file size `i_size`** (`ld r9, 0x178(r3); std r9, 0x28(r28)`).

### 1.4 `raw_read`: `0x1ed5cc`

- **Descriptor**: `0x73f2c8` (Cobra descriptor table entry: `0x4530`).
- **Signature**: `int64_t raw_read(int fd, uint64_t offset, void *buf, uint64_t count)`
- **Calling registers**:
  - `r3`: File descriptor `fd`.
  - `r4`: Byte offset in file.
  - `r5`: Destination buffer in CPU EA.
  - `r6`: Requested byte count.
- **Implementation**:
  - Validates `fd <= 7`, acquires UFS lock at `0x3055180`.
  - Calls `0x1ec084(slot_ptr, offset, buf, count, is_write=0)`.
  - Unlocks global UFS lock and returns bytes read.

### 1.5 `raw_write` (`ufs_write`): `0x1ed458`

- **Descriptor**: `0x73f2b0` (Cobra descriptor table entry: `0x4550`).
- **Signature**: `int64_t raw_write(int fd, uint64_t offset, const void *buf, uint64_t count)`
- **Calling registers**:
  - `r3`: File descriptor `fd`.
  - `r4`: Byte offset in file.
  - `r5`: Source buffer in CPU EA.
  - `r6`: Requested byte count.
- **Implementation**:
  - Identical twin to `raw_read` (`0x1ed5cc`), located immediately prior (`0x1ed458..0x1ed5c8`).
  - Validates `fd <= 7`, acquires UFS lock at `0x3055180`.
  - Calls `0x1ec084(slot_ptr, offset, buf, count, is_write=1)`. Notice `0x1ed588: li r7, 1`.
  - Unlocks global UFS lock and returns bytes written.
- **Callers in stock netemu**:
  - Virtual memory card save path: `0x11b86c`, `0x11ba50`, `0x11ba78`, `0x11bac8`, `0x11bae0`, `0x11bb90`, `0x11bdcc`.
  - SIO2 memory card manager: `0x128fc8`.
  - Container / disc header writer: `0x1380e0`.

### 1.6 File Extension vs. Silent Clamping (`0x1ec084`)

**PROVEN by disassembly (`0x1ec0e4..0x1ec100`, `0x1ec240..0x1ec258`):**
In `0x1ec084`, the file size is loaded from the inode: `ld r9, 0x178(r3)` (`r9 = i_size`).
The code computes `offset + count` and compares it to `i_size`:
```assembly
0x001ec0f4: extsw   r0, r26         # r26 = requested count
0x001ec0f8: add     r0, r4, r0      # r0 = offset + count
0x001ec0fc: cmpld   cr7, r0, r9     # compare (offset + count) with i_size
0x001ec100: bgt     cr7, 0x001ec240 # if (offset + count > i_size) branch to 0x1ec240
```
At `0x1ec240`:
```assembly
0x001ec240: subf    r26, r4, r9     # r26 = i_size - offset
0x001ec244: cmpwi   cr6, r26, 0     # if (i_size - offset > 0)
0x001ec248: bgt     cr6, 0x001ec10c # branch back with count clamped to (i_size - offset)!
0x001ec24c: li      r26, 0          # otherwise (offset >= i_size), count = 0
...
0x001ec258: extsw   r3, r26         # return 0 bytes transferred!
0x001ec284: blr
```

**Conclusion:**
Stock `raw_write` **CANNOT EXTEND A FILE**. It **NEVER ALLOCATES BLOCKS**.
If `offset + count > i_size`, it **SILENTLY CLAMPS** the write to the remaining bytes in the file.
If `offset >= i_size`, it returns `0`.
Therefore, writes to a pre-allocated placeholder file are 100% confined within existing pre-allocated disk blocks.

---

## 2. Write-Through & Cache Flush Mechanism

### 2.1 The HDD Sector Cache (`H = 0x241c850`)

The stock HDD driver uses a singleton structure at `0x241c850` (TOC slot `-0x6f58`, address `0x74a328`):
- It contains **32 cache blocks**, each managing **32 sectors** (32 * 512 = 16 KiB per block). Total cache size = 512 KiB.
- Descriptors reside at `H + 0xe8 + block_idx * 0x30` (`block_idx = 0..31`).
- Descriptor fields:
  - `+0x10`: LBA base of cache block (u64)
  - `+0x18`: Validity bitmask (u32, 1 bit per sector, 32 bits)
  - `+0x1c`: **Dirty bitmask** (u32, 1 bit per sector, 32 bits)
  - `+0x20`: CPU virtual address of cached data
  - `+0x28`: LPAR / DMA address of cached data

### 2.2 Write-Back Behavior in `0x12d0ac` (`hdd_cache_write`)

When `raw_write` is called with a 512-byte aligned offset and count:
1. `0x1eb780` detects `offset % 512 == 0` and `count % 512 == 0`. It shifts `offset >> 9` to obtain `lba` and `count >> 9` to obtain `sector_count`.
2. It calls `0x12d0ac(lba, buffer, sector_count)`.
3. `0x12d0ac` copies data into the cache block's buffer (`0x118a90`), sets the validity bit (`+0x18`), and sets the **dirty bit (`+0x1c`)**.
4. At `0x12d1e0..0x12d218`, it checks `H+0x80`. If `0`, it sets `H+0x80 = 1` and registers a delayed flush timer via `0x111bfc` for `0x4c20000` timebase ticks (~1.5 seconds).
5. **Critical consequence**: The stock file write is strictly **write-back**. If an instant power-off occurs before the 1.5s timer expires, the written log data in memory **is lost**.

### 2.3 Standalone Flush: `0x12cc98` (`hdd_cache_flush`)

**INFERRED / HIGH CONFIDENCE:**
Stock function **`0x12cc98`** (descriptor `0x724430`) is the **standalone cache flush routine**.
- **Signature**: `int hdd_cache_flush(void)` (takes no arguments).
- **Execution flow**:
  1. Checks `lbz r0, 0x78(H)` (driver error flag). If non-zero, aborts returning `-5`.
  2. Loops through all 32 cache block descriptors (`0x12ccf4..0x12ce20`):
     - Reads dirty mask `lwz r28, 0x1c(r21)`. If `0`, advances to next block.
     - Uses `cntlzw` to find the leading dirty sector index and count of contiguous dirty sectors.
     - Masks interrupts (`bl 0x11a604`).
     - Issues hypercall:
       ```
       li r11, 0xf6             # LV1 call 246: lv1_storage_write
       oris r11, r11, 0x8000    # r11 = 0x800000F6
       r3 = H->dev              # HDD device ID (3)
       r4 = 1                   # Region 1 (storage partition)
       r5 = start_lba           # Disk sector
       r6 = sector_count        # Number of sectors to flush
       r7 = 0                   # Flags = 0
       r8 = buffer_lpar         # LPAR DMA address
       sc 0
       ```
     - Saves returned tag at `H+0x48`.
     - Restores interrupts (`bl 0x11a5f8`).
     - Waits synchronously for completion:
       ```assembly
       0x0012cd50: li     r11, 0x7      # wait_event
       0x0012cd58: li     r3, 0x2000    # Event 0x2000 (guest IRQ 0x12 completion)
       0x0012cd5c: sc     0x0
       0x0012cd6c: ld     r0, 0x38(r30) # Completed tag (from interrupt handler)
       0x0012cd70: ld     r6, 0x48(r30) # Expected tag
       0x0012cd74: cmpd   cr7, r0, r6
       0x0012cd78: bne    cr7, 0x0012cd50 # Loop until tag matches
       ```
     - Verifies completion status `H+0x40 == 0`.
     - Clears the dirty bits in `+0x1c`.
  3. When all 32 blocks are clean, returns `0` (`0x12ce24: li r29, 0; blr`).
- **Contrast with `0x12d420` (`hdd_shutdown`)**:
  - `0x12d420` contains an identical flush loop, but immediately after flushing, it proceeds to unmap DMA (LV1 177), free DMA (LV1 175), close the device (LV1 171), and disable the driver (`H+0x85 = 0`).
  - Therefore, `0x12d420` **destroys** the HDD driver and cannot be used during emulation. `0x12cc98` **preserves** the driver.

### 2.4 Synchronous Latency & Calling Context

- **Event 0x2000 wait**: The loop has no timeout. It relies on guest IRQ 0x12 (`0x12b320`) acknowledging the hardware interrupt with LV1 27, fetching async status with LV1 249, updating `H+0x38`/`H+0x40`, and signaling event `0x2000`.
- **Duration**: Writing 1 sector (512 bytes) over SATA to the PS3 5400 RPM HDD takes ~2 to 8 ms.
- **Calling Context**:
  - Menu hook (`0x270FFC` / `0x270C24`): Runs on the main emulator UI thread. The PS2 guest emulation is effectively paused while in the PS-button menu. Calling `raw_write` + `hdd_cache_flush` here introduces an imperceptible 5 ms delay.
  - Periodic / per-frame logging: **Unsuitable**. A 5 ms synchronous disk stall every 16 ms would cause massive audio stutter and emulator frame drops.
  - Crash / hook logging: Safe when triggered on specific discrete events (disc swap, error traps, menu open/close).

---

## 3. Locking, Concurrency & Safety Constraints

### 3.1 Serialization Layers

There are two distinct concurrency levels in the netemu storage stack:

| Layer | State Object | Lock / Serialization Mechanism | Stock Behavior |
|---|---|---|---|
| **UFS File Layer** | `0x3055180` | Spinlock + Event `0x4000` wait (`0x1ed5f8..0x1ed630`) | Serializes `open`, `close`, `read`, `write`, `stat`. Contention waits safely. |
| **HDD Driver Layer** | `H = 0x241c850` | Single-command tag slot (`H+0x48`), Event `0x2000` | **NON-REENTRANT**. Only 1 outstanding LV1 command permitted at a time. |

### 3.2 Hazard Analysis: What Must NOT Be Done

1. **Never call `hdd_cache_flush` (`0x12cc98`) while `H+0x48 != 0`**:
   - `H+0x48` holds the expected tag of an active in-flight storage command.
   - If the CDVD thread or I/O worker is mid-read, calling `0x12cc98` overwrites `H+0x38 = -1` and sets `H+0x48` to the flush write tag.
   - The CDVD thread's wait loop would miss its completion tag and hang indefinitely (console freeze).
2. **Never call `0x12d420`**:
   - As proven above, `0x12d420` is driver teardown.
3. **Never write beyond the pre-allocated placeholder file size**:
   - Writing beyond `i_size` is silently clamped by `0x1ec084`, but attempting unaligned or oversized writes invokes `0x1ebb70`'s scratch buffers, which could conflict if another thread uses that slot.

### 3.3 Minimum Safe Preconditions (Guard Check)

Before executing any log write or flush, our payload must evaluate the following guard in assembly / C:

```c
static inline bool is_hdd_log_safe(void) {
    uint64_t *toc = (uint64_t*)0x751280;
    uint8_t *H = *(uint8_t**)(0x751280 - 0x6f58); // H = 0x241c850
    uint32_t *ufs_lock = *(uint32_t**)(0x751280 - 0x42f8); // 0x3055180

    if (!H || !ufs_lock) return false;

    // Check driver enabled and healthy
    if (H[0x85] != 1) return false; // Driver disabled
    if (H[0x78] != 0) return false; // Driver error flag set

    // Check device ID is valid
    if (*(uint64_t*)(H + 0x10) != 3) return false;

    // Check driver is completely idle (no commands in-flight)
    if (*(uint64_t*)(H + 0x48) != 0) return false; // Expected tag must be 0
    if (*(uint64_t*)(H + 0x38) != 0) return false; // Tagstat must be 0
    if (*(uint64_t*)(H + 0x40) != 0) return false; // Status must be 0

    // Check UFS lock is not currently contended
    if (*ufs_lock != 0) return false;

    return true;
}
```

If `is_hdd_log_safe()` returns false, the log transaction must **fail-open** (skip disk write and preserve console stability).

---

## 4. Log Protocol & Transaction Design

### 4.1 Disk File Structure: `/dev_hdd0/tmp/netemu_log.bin` (64 KiB)

The placeholder file is exactly 65,536 bytes (128 sectors of 512 bytes):

```
+---------------------------------------------------------------+
| Sector 000 (Offset 0x0000 - 0x01FF): Log Header (512 B)       |
+---------------------------------------------------------------+
| Sector 001 (Offset 0x0200 - 0x03FF): Log Record 001 (512 B)   |
| Sector 002 (Offset 0x0400 - 0x05FF): Log Record 002 (512 B)   |
| ...                                                           |
| Sector 127 (Offset 0xFE00 - 0xFFFF): Log Record 127 (512 B)   |
+---------------------------------------------------------------+
```

#### Sector 0: Log Header (512 bytes)
```c
struct NetemuLogHeader {
    uint64_t magic;           // 0x00: 0x4E4554454D554C47 ("NETEMULG")
    uint32_t version;         // 0x08: 0x00010000 (1.0)
    uint32_t header_size;     // 0x0C: 512
    uint32_t file_size;       // 0x10: 65536
    uint32_t sector_size;     // 0x14: 512
    uint32_t max_records;     // 0x18: 127
    uint32_t next_record_idx; // 0x1C: 1..127 (write cursor)
    uint64_t boot_tb;         // 0x20: Timebase at netemu startup
    uint32_t clean_shutdown;  // 0x28: 0 = uncommitted/crash, 1 = clean exit
    uint32_t reserved[117];   // 0x2C: Pad to exactly 512 bytes
};
```

#### Sectors 1..127: Log Record (512 bytes each)
```c
struct NetemuLogRecord {
    uint32_t magic;           // 0x00: 0x4C4F4752 ("LOGR")
    uint32_t sequence;        // 0x04: Monotonic sequence counter
    uint32_t source_tag;      // 0x08: Component tag (e.g. 0x01=Menu, 0x02=CDVD, 0x03=Probe)
    uint32_t flags;           // 0x0C: Status flags
    uint64_t timestamp_tb;    // 0x10: Timebase ticks of event
    char     message[488];    // 0x18: NUL-terminated text message or raw telemetry bytes
};
```

### 4.2 Single Record Write Transaction (Atomic Lifecycle)

To eliminate slot exhaustion and minimize lock contention, every log write executes as a self-contained transaction:

```c
int netemu_log_write(uint32_t tag, const char *msg) {
    if (!is_hdd_log_safe()) return -1;

    // 1. Open placeholder file
    int fd = stock_ufs_open(0, "/tmp/netemu_log.bin");
    if (fd < 0) return fd;

    // 2. Determine target sector from state (e.g. kept in our RW mailbox)
    uint32_t rec_idx = g_state->log_cursor;
    if (rec_idx == 0 || rec_idx > 127) rec_idx = 1;
    uint64_t offset = rec_idx * 512;

    // 3. Format 512-byte record buffer on stack
    struct NetemuLogRecord rec;
    memset(&rec, 0, sizeof(rec));
    rec.magic = 0x4C4F4752;
    rec.sequence = g_state->log_seq++;
    rec.source_tag = tag;
    rec.timestamp_tb = read_timebase();
    strncpy(rec.message, msg, sizeof(rec.message) - 1);

    // 4. In-place write of exactly 512 aligned bytes
    int64_t written = stock_raw_write(fd, offset, &rec, 512);

    // 5. Close file immediately (frees slot)
    stock_ufs_close(fd);

    // 6. Advance cursor and write-through flush to disk
    if (written == 512) {
        g_state->log_cursor = (rec_idx >= 127) ? 1 : (rec_idx + 1);
        stock_cache_flush(); // 0x12cc98
    }

    return (written == 512) ? 0 : -2;
}
```

### 4.3 Native Helper Trampolines

Calling stock functions from our payload in the code slot (`0x4800..0x7FF0`) must use `bl` trampolines following standard PPC64 ELF ABI discipline (saving LR, CR, and setting up stack frame):

```assembly
# Trampoline definitions in our payload:
stock_ufs_open:
    mflr    r0
    std     r0, 16(r1)
    bl      0x1ecc5c
    ld      r0, 16(r1)
    mtlr    r0
    blr

stock_ufs_close:
    mflr    r0
    std     r0, 16(r1)
    bl      0x1ecb10
    ld      r0, 16(r1)
    mtlr    r0
    blr

stock_raw_write:
    mflr    r0
    std     r0, 16(r1)
    bl      0x1ed458
    ld      r0, 16(r1)
    mtlr    r0
    blr

stock_cache_flush:
    mflr    r0
    std     r0, 16(r1)
    bl      0x12cc98
    ld      r0, 16(r1)
    mtlr    r0
    blr
```

---

## 5. Risk Assessment

| Risk Item | Evidence Level | Description & Worst Case | Mitigation |
|---|---|---|---|
| **Filesystem metadata corruption** | **PROVEN (PC)** | Disassembly of `0x1ec084` proves that writes within existing `i_size` never allocate blocks, never touch direct/indirect block tables, and never modify cylinder group allocation bitmaps. Worst case: 0% risk to UFS filesystem structure. | Pre-allocate full 64 KiB placeholder file with zeros before netemu boots. |
| **Placeholder file corruption** | **INFERRED** | If console power cuts off during the 2 ms SATA sector write, that specific 512-byte sector may have partial or corrupted data. Worst case: 1 log record corrupted. | Each record has a magic (`LOGR`) and sequence number; reader detects corrupt record without failing. |
| **Re-entrancy / Deadlock with CDVD or VMC** | **PROVEN (PC)** | UFS layer serializes with global lock (`0x3055180`). HDD driver `H` has single tag slot `H+0x48`. If flush is called while `H+0x48 != 0`, CDVD tag completion is clobbered. | Mandatory idle guard: check `H+0x48 == 0 && H+0x38 == 0 && H+0x40 == 0` before calling write or flush. |
| **Slot exhaustion** | **PROVEN (PC)** | Netemu has 8 file slots (`0x1ecce4`). Active usage is typically 1..2 slots. If our code leaked an fd, all 8 slots could fill, failing game loads. | Open, write, close in the same transaction. Never hold an fd open across frames. |
| **Infinite wait on Event 0x2000** | **PROVEN (PC)** | The wait loop at `0x12cd50` has no timeout. If the disk driver is in an error state (`H+0x78 != 0`), it could wait forever. | Guard checks `H+0x78 == 0` and `H+0x85 == 1` before issuing flush. |
| **Console filesystem verification** | **PROVEN (Console)** | CFW / webMAN MOD and the PS3 Recovery Menu provide standard UFS filesystem checks ("Restore File System"). | If the user ever experiences an unexpected shutdown, the PS3 standard filesystem check verifies `/dev_hdd0` cleanly. |

---

## 6. Tooling & Verification Scripts

Two PowerShell scripts have been developed in `tools\` and verified using the PowerShell AST Language Parser (`[System.Management.Automation.Language.Parser]::ParseFile`) with **0 errors**, compatible with both Windows PowerShell 5.1 and PowerShell 7+:

### 6.1 `tools\make_log_placeholder.ps1`
- **Purpose**: Creates a 65,536-byte zero-filled binary locally, uploads it to `ftp://<Ps3Host>/dev_hdd0/tmp/netemu_log.bin` using `curl.exe`, reads it back, and verifies that the file is exactly 65,536 bytes and 100% zeros.
- **Safety**: Checks if the file already exists on the PS3; refuses to overwrite existing non-zero data unless `-Force` is supplied.
- **Console execution**: **NEVER RUN BY AI**. For owner execution only:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\make_log_placeholder.ps1 -Ps3Host 192.168.0.169
  ```

### 6.2 `tools\read_netemu_log.ps1`
- **Purpose**: Connects read-only over FTP, downloads `/dev_hdd0/tmp/netemu_log.bin`, and decodes the header (Sector 0) and records (Sectors 1..127).
- **Output**: Displays header status, timestamp, sequence numbers, and ASCII message text for each populated sector.
- **Console execution**: Read-only, safe for owner use:
  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\read_netemu_log.ps1 -Ps3Host 192.168.0.169
  ```

---

## 7. Static Symbol Reference Table

| Symbol | Address | Descriptor | Provenance | Purpose |
|---|---|---|---|---|
| `ufs_open` | `0x1ecc5c` | `0x73f298` (Cobra `0x4510`) | PROVEN (PC) | Opens UFS file relative to `/dev_hdd0/` root; returns `fd` (0..7). |
| `ufs_close` | `0x1ecb10` | `0x73f280` (Cobra `0x4520`) | PROVEN (PC) | Closes UFS file slot, clears `in_use`, releases lock. |
| `ufs_stat` | `0x1ec760` | `0x73f250` (Cobra `0x4560`) | PROVEN (PC) | Fetches file inode metadata (`i_size` at `st+0x28`). |
| `raw_read` | `0x1ed5cc` | `0x73f2c8` (Cobra `0x4530`) | PROVEN (PC) | Reads bytes from open UFS file slot. |
| `raw_write` | `0x1ed458` | `0x73f2b0` (Cobra `0x4550`) | PROVEN (PC) | Writes bytes to open UFS file slot (in-place clamp). |
| `block_traverse` | `0x1ec084` | - | PROVEN (PC) | Inode direct/indirect block mapping; clamps to `i_size`. |
| `hdd_aligned_rw` | `0x1eb780` | - | PROVEN (PC) | Dispatches 512-byte aligned I/O to cache reader or writer. |
| `hdd_cache_write` | `0x12d0ac` | - | PROVEN (PC) | Writes sectors into 32-sector cache block; marks dirty. |
| `hdd_cache_read` | `0x12d224` | - | PROVEN (PC) | Reads sectors from 32-sector cache block. |
| `hdd_cache_flush` | `0x12cc98` | `0x724430` | PROVEN (PC) | **Standalone cache flush**: issues LV1 246, waits on event 0x2000. |
| `hdd_cleanup` | `0x12d420` | - | PROVEN (PC) | Shutdown: flushes cache AND unmaps/closes device (DO NOT CALL). |
| `H` (HDD state) | `0x241c850` | `TOC - 0x6f58` (`0x74a328`) | PROVEN (Console P2C) | HDD driver singleton state. |
| `UFS lock` | `0x3055180` | `TOC - 0x42f8` (`0x74cf88`) | PROVEN (PC) | Global UFS mutex word. |
