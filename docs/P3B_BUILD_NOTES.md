# P3B Build Notes: Reusable Durable HDD Logger & L0 Test Variant

## Status
- **Date**: 2026-11-01
- **Task**: P3B ps2_netemu reusable durable HDD logger module (`src/hddlog.c`) and L0 test variant (`ps2_netemu_p3b_L0.self`). PC validation only; do not install.
- **Base Tree**: Cloned from proven hypercall-free pager pattern in `netemu_p2c`.

---

## 1. Static Verification of Stock Preconditions & Calling Conventions

### 1.1 Stock HDD Driver State `H` (`0x241c850`) & Verified Idle Predicate
The HDD driver singleton structure resides at `0x241c850` (accessed via `TOC - 0x6f58` = `0x74a328` at runtime).
Verified against `local_only/stock.elf` and console measurements (`docs/P2C_RESULT.md`):

| Field Offset | Stock Meaning / Verification | Expected Idle Value | Measured Console Value (P2C) |
|---|---|---|---|
| `H + 0x10` | DEV_ID (uint64) | `3` (HDD device id) | `3` |
| `H + 0x38` | TAGSTAT / Completed Tag (uint64) | `0` (idle) | `0` |
| `H + 0x40` | Completion Status (uint64) | `0` (success/idle) | `0` |
| `H + 0x48` | Expected Tag (uint64) | `0` (no active command) | `0` |
| `H + 0x78` | Driver Error Flag (uint8) | `0` (no driver fault) | `0` |
| `H + 0x85` | Driver Ready / Enabled (uint8) | `1` (driver active) | `1` |

**Verified Predicate in C (`is_hdd_log_safe`)**:
```c
static inline int is_hdd_log_safe(void) {
    const u8 *H = *(const u8 * const *)0x241C850ULL; // or TOC - 0x6f58
    if (!H) return 0;
    if (H[0x85] != 1) return 0; // driver must be enabled (checked at 0x12d0cc, 0x12cda0)
    if (H[0x78] != 0) return 0; // driver error flag must be clear (checked at 0x12cca8, 0x12d124)
    if (*(const u64 *)(H + 0x10) != 3) return 0; // device id must be 3 (netemu HDD)
    if (*(const u64 *)(H + 0x48) != 0) return 0; // expected tag must be 0 (no command in-flight)
    if (*(const u64 *)(H + 0x38) != 0) return 0; // completed tag must be 0 (no unacknowledged tag)
    if (*(const u64 *)(H + 0x40) != 0) return 0; // status must be 0
    const u32 *ufs_lock = *(const u32 * const *)0x3055180ULL; // TOC - 0x42f8
    if (ufs_lock && *ufs_lock != 0) return 0; // UFS mutex must not be held
    return 1;
}
```

### 1.2 `ufs_open` (`0x1ecc5c`) Calling Convention & Mode Encoding
- **Descriptor**: `0x73f298` (Cobra entry `0x4510`).
- **Signature**: `int ufs_open(uint64_t dev_unused, const char *path)`
- **Calling Registers**:
  - `r3 = 0` (device index, always 0 in all 27 stock callers).
  - `r4 = path` (`const char *` NUL-terminated path, e.g. `"/tmp/netemu_log.bin"`).
  - **NO MODE ARGUMENT**: Verified from VMC save path at `0x11b840` (`li r3, 0`, `mr r4, path`, `bl 0x1ecc5c`) and disassembly of `0x1ecc5c` prologue. Stock UFS slots are automatically opened with read/write capability.
- **Return Value**:
  - `r3 >= 0`: file descriptor `fd` in `0..7`.
  - `r3 < 0`: error code (`-1` = all 8 slots full, `-2` = file not found, `-5` = superblock error).

### 1.3 `ufs_close` (`0x1ecb10`) Calling Convention
- **Descriptor**: `0x73f280` (Cobra entry `0x4520`).
- **Signature**: `int ufs_close(int fd)`
- **Calling Registers**:
  - `r3 = fd` (`0..7`).
- **Return Value**:
  - `r3 = 0` on success; `-3` if invalid or not open.
- **Slot Discipline**: Must be called on every path including errors to guarantee 0 slot leakage.

### 1.4 `raw_read` (`0x1ed5cc`) & `raw_write` (`0x1ed458`) Calling Conventions & Buffer Type
- **Signatures**:
  - `int64_t raw_read(int fd, uint64_t offset, void *buf, uint64_t count)`
  - `int64_t raw_write(int fd, uint64_t offset, const void *buf, uint64_t count)`
- **Calling Registers**:
  - `r3`: `fd` (`0..7`).
  - `r4`: `offset` (byte offset in file; must be 512-aligned).
  - `r5`: `buf` (CPU Effective Address).
  - `r6`: `count` (byte count; 512 for sector transactions).
- **Buffer Type Verification**:
  - In `0x12d0ac` (`hdd_cache_write`), at `0x12d18c`, the stock code calls `0x00118a90` (`memcpy`), copying data from `r4` (the CPU buffer passed in `r5`) directly into the cache block's virtual address (`ld r3, 0x20(r8)`).
  - **PROVEN**: `raw_write` accepts a standard CPU buffer. It does NOT require a physical DMA or LPAR buffer.
  - To minimize stack frame size and ensure strict 512-byte alignment, our implementation builds sector buffers in the validated 4 KiB Arena (`native_alloc`).

### 1.5 `hdd_cache_flush` (`0x12cc98`) Standalone Cache Flush
- **Descriptor**: `0x724430`.
- **Signature**: `int hdd_cache_flush(void)` (takes no arguments).
- **Behavior**:
  - Checks `H+0x78` (driver error); aborts with `-5` if non-zero.
  - Loops over 32 cache blocks. If dirty bits exist, issues LV1 246 (`lv1_storage_write`), sets `H+0x38 = -1`, receives tag in `H+0x48`, and waits on guest event `0x2000` via LV1 7.
  - Clears dirty bits upon completion.
  - Preserves driver state and leaves driver active.
- **Hang Risk & Mitigation**:
  - The wait loop at `0x12cdb8` has NO timeout. If the drive hangs or hardware is in a bad state, it could loop indefinitely.
  - **Mitigation**: Strictly guarded by `is_hdd_log_safe()`. Only invoked when `H` is verified 100% idle and healthy. Never called if error flag `H+0x78 != 0`.

---

## 2. Disk Format & Layout Specification

### 2.1 Pre-allocated Placeholder: `/dev_hdd0/tmp/netemu_log.bin` (65,536 bytes)
- Exactly 128 sectors of 512 bytes each.
- Sector 0 (`0x0000..0x01FF`): Log Header.
- Sectors 1..127 (`0x0200..0xFFFF`): Log Records (capacity = 127 records).
- Stock `0x1ec084` clamps all writes to file size `i_size` (65,536 bytes). Never allocates disk blocks.

### 2.2 Sector 0: Log Header (512 bytes)
```c
struct NetemuLogHeader {
    u64 magic;           /* 0x00: 0x4E4554454D554C47 ("NETEMULG") */
    u32 version;         /* 0x08: 0x00010000 (v1.0) */
    u32 header_size;     /* 0x0C: 512 */
    u32 file_size;       /* 0x10: 65536 */
    u32 sector_size;     /* 0x14: 512 */
    u32 max_records;     /* 0x18: 127 */
    u32 next_record_idx; /* 0x1C: 1..127 (write cursor) */
    u64 boot_tb;         /* 0x20: Timebase at netemu startup (Boot ID) */
    u32 clean_shutdown;  /* 0x28: 0 = uncommitted/crash, 1 = clean exit */
    u32 record_count;    /* 0x2C: total records written in current session */
    u8  reserved[464];   /* 0x30..0x1FF: zero padding to 512 bytes */
};
```

### 2.3 Sectors 1..127: Log Record (512 bytes)
```c
struct NetemuLogRecord {
    u32 magic;           /* 0x00: 0x4C4F4752 ("LOGR") */
    u32 sequence;        /* 0x04: Monotonic sequence counter */
    u32 tag;             /* 0x08: Tag (ASCII 'BOOT', 'T1  ', 'T2  ', 'END ' or numeric) */
    u32 flags;           /* 0x0C: Status flags */
    u64 timestamp_tb;    /* 0x10: Timebase ticks from native_clock */
    u64 a;               /* 0x18: 64-bit parameter A */
    u64 b;               /* 0x20: 64-bit parameter B */
    u64 reserved[4];     /* 0x28: 32 bytes reserved telemetry */
    char text[440];      /* 0x48: NUL-terminated message string (440 bytes) */
};
```
*Verification*: 72 header bytes + 440 text bytes = exactly 512 bytes (`0x200`). Naturally aligned on 8-byte boundaries.

### 2.4 Cursor Policy: Stop-When-Full
When `next_record_idx > 127`, the log is full. The logger chooses **stop-when-full** (sets mailbox status `LOG_FULL` and ceases writes). This preserves initial boot telemetry and early probe records from being overwritten by subsequent menu openings.

---

## 3. Mailbox Layout (`0x930F20..0x930F80`, exactly 96 bytes)

```c
struct HddLogMailbox {
    u32 status;            /* 0x00: bitmask: STARTED, DONE, INIT_OK, INIT_FAILED, LOG_FAILED, LOG_FULL */
    u32 records_written;   /* 0x04: count of records successfully written & flushed */
    u32 bytes_written;     /* 0x08: total bytes written */
    s32 last_ufs_rc;       /* 0x0C: return code from last UFS call */
    s32 last_flush_rc;     /* 0x10: return code from last hdd_cache_flush */
    u32 open_count;        /* 0x14: menu open cycles detected by TB gap */
    u64 arena_ptr;         /* 0x18: pointer to 4 KiB arena from native_alloc */
    u64 boot_tb;           /* 0x20: boot timebase ticks from native_clock */
    u64 last_eval_tb;      /* 0x28: timebase of last hook evaluation */
    u32 cursor;            /* 0x30: current next_record_idx */
    u32 fail_reason;       /* 0x34: reason code if logging stopped */
    u64 hdd_state_h;       /* 0x38: pointer H (0x241c850) */
    u64 idle_tagstat;      /* 0x40: H+0x38 read during idle check */
    u64 idle_status40;     /* 0x48: H+0x40 read during idle check */
    u64 idle_status48;     /* 0x50: H+0x48 read during idle check */
    u8  driver_enabled;    /* 0x58: H+0x85 read during idle check */
    u8  driver_error;      /* 0x59: H+0x78 read during idle check */
    u8  flush_completed;   /* 0x5A: 1 if cache flush completed */
    u8  pad[5];            /* 0x5B: pad to exactly 96 bytes */
};
```
_Static assertions guarantee `sizeof(struct HddLogMailbox) == 96`.

---

## 4. Code Cave Trampoline Architecture

The code cave at `0x4800..0x7FF0` hosts the trampolines:
- `0x4800`: `native_alloc` (target `0x0b9848`, TOC `0x751280`)
- `0x4840`: `native_clock` (target `0x0b9cd0`, `b 0x0b9cd0`)
- `0x4860`: `get_r2` (`mr r3, 2; blr`)
- `0x4880`: `ufs_open` (target `0x1ecc5c`, TOC `0x751280`)
- `0x48C0`: `ufs_close` (target `0x1ecb10`, TOC `0x751280`)
- `0x4900`: `raw_read` (target `0x1ed5cc`, TOC `0x751280`)
- `0x4940`: `raw_write` (target `0x1ed458`, TOC `0x751280`)
- `0x4980`: `hdd_cache_flush` (target `0x12cc98`, TOC `0x751280`)
- `0x49C0`: `entry_menu` (target `s4_menu`, saves/restores TOC, extracts row `r3`)
- `0x4A00`: Payload C code (`hddlog.o` + `probe.o`)

NO custom hypercalls (`sc 0`) are written into our code. All storage hypercalls are executed exclusively by the stock functions (`raw_write` and `hdd_cache_flush`).


---

## 5. Build Artifacts, Hashes & Verification Results

### 5.1 Binary Artifacts & Cryptographic Hashes
- **Stock ELF**: `local_only/stock.elf`
  - SHA-256: `63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3`
- **Stock SELF**: `local_only/stock_ps2_netemu.self`
  - SHA-256: `bad3e45c9a81f25726e414b146ea5a112f28216ab4bdd2fd9f5c81b33d04c80a`
- **Patched ELF**: `local_only/p3b/ps2_netemu_p3b_L0.elf`
  - Size: 10,901,288 bytes
  - SHA-256: `8d723e7c3072a557b0f7881d26b71e71a1be8b55e9ad3dc0122b773888f7884f`
- **Patched SELF**: `local_only/p3b/ps2_netemu_p3b_L0.self`
  - Size: 2,526,448 bytes
  - SHA-256: `57507f5daafc67084ad94d9fb7250c5ee50a33db65027063a3c73fbdf4a0ddb1`
- **Code Cave Allocation**:
  - Trampolines: `0x4800..0x4A00` (512 bytes)
  - Payload text/rodata: `0x4A00..0x58A0` (3,744 bytes)
  - Total code cave footprint: 4,256 bytes / 14,320 bytes (29.7%)

### 5.2 Strict `p1a_audit.py` Results
```
stock sha256 63f12b7e00959c758f8aedfd23d1b8bc78e8ae7d922048e4765aaaef1dbbc6d3
p1a   sha256 8d723e7c3072a557b0f7881d26b71e71a1be8b55e9ad3dc0122b773888f7884f
sc instructions in changed/added executable ranges: []
stores in changed/added executable ranges: 124
```
**ZERO** `sc` instructions in our payload. All stores strictly to stack (`r1`), arena buffers (`r3`, `r4`, `r5`, `r6`, `r8`), and mailbox (`r23`, `r27`, `r28`, `r29`, `r30`).

### 5.3 PyGhidra `validate_pc.py` Test Suite Outcome
1. **Happy Path (L0 4-record durable write & flush)**:
   - 4 records written: `BOOT`, `T1`, `T2`, `END`.
   - Next cursor updated to `#5`.
   - Sector 0 header verified: `NETEMULG`, 65536 bytes, 127 capacity.
   - All 4 records parsed and validated via `decode_netemu_log.py`.
   - Slot accounting: exactly 0 leaked slots (4 opens, 4 closes).
   - Menu open idempotency: repeated menu opens do not re-issue writes.
2. **Busy HDD Guard**:
   - Tested 5 conditions: `H+0x38 != 0`, `H+0x48 != 0`, `H+0x85 == 0`, `H+0x78 != 0`, `ufs_lock != 0`.
   - In all 5 cases: exactly 0 UFS calls issued, zero writes, zero flushes.
3. **Missing File Injection**:
   - `ufs_open -> -2`: zero writes, zero flushes, label displays `P3B-L0 FAIL: NO FILE (/tmp/netemu_log.bin missing)`, 0 leaked slots.
4. **Write Error Injection**:
   - `raw_write -> -5`: fd closed immediately, flush skipped, 0 leaked slots.
5. **Memory Store Range Audit**:
   - All stores verified inside stack, 96-byte mailbox `[0x930F20, 0x930F80)`, or 4 KiB arena.
   - ZERO stores into stock global variables `[0x930F80, 0x931000)`.
6. **Bounds Fuzzing**:
   - Fuzzed row index across 13 extreme values (`0, 1, 2, 7, 8, 9, 10, 15, 36, 100, 255, 1000, 0xFFFFFFFF`); all returned valid clamped labels.
7. **SELF Round-Trip**:
   - Decrypted ELF matches patched ELF byte-for-byte.
8. **PowerShell AST Parse Check**:
   - `make_log_placeholder.ps1`: 0 errors
   - `read_netemu_log.ps1`: 0 errors
   - `install_netemu.ps1`: 0 errors
   - `restore_netemu.ps1`: 0 errors
