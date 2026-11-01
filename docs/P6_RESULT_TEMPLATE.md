# P6 Result: Optical DMA Mapping Test (Variant R1)

## Console Execution Instructions for Operator

1. **Install Variant R1**:
   - Copy `local_only/p6/ps2_netemu_p6_R1.self` to `/dev_hdd0/game/PS2NETEMU/USRDIR/ps2_netemu.self` on the PS3 (via FTP or local script).
   - Ensure `/dev_hdd0/tmp/netemu_log.bin` is present or initialized (64 KiB placeholder).

2. **Run Test on Console**:
   - Start any standard PS2 disc or ISO game.
   - Wait 10 seconds for initial netemu boot and optical device enumeration.
   - Press the **PS Button** once to display the in-game menu (this evaluates the hook at `0x270FFC`).
   - Observe **Row 0** on the screen:
     - `P6-R1 DONE: CAND #1 MAP OK` (Victory: CDVD real physical LPAR accepted by LV1)
     - Or `P6-R1 DONE: CAND #4 MAP OK` (Victory: Stock HDD LPAR accepted by LV1)
     - Or `P6-R1 FAIL: ALL CANDIDATES REJECTED (-17)`
   - Exit the game back to XMB (clean shutdown flushes `/dev_hdd0/tmp/netemu_log.bin`).

3. **Log Retrieval**:
   - Pull `/dev_hdd0/tmp/netemu_log.bin` over FTP to `local_only/netemu_log_R1.bin`.
   - The test harness will decode and verify all WAL records.

---

## Candidate Reference Table (Variant R1)

| Candidate ID | Target Source Address | Bus Region Exponent | Region Size | Map Length | Map Flags | Description / Rationale |
|---|---|---|---|---|---|---|
| **#1** | CDVD Real LPAR (`0x2458438`, `0x500002c00000`) | 20 (1 MiB pages) | 0x100000 | 0x100000 | `0xe000000000000800` | **Rank 1**: Sony optical emulator standard with physical LPAR. |
| **#2** | CDVD Real LPAR (`0x2458438`, `0x500002c00000`) | 16 (64 KiB pages) | 0x100000 | 0x80000 | `0xe000000000000800` | **Rank 2**: 64 KiB page size, 512 KiB length. |
| **#3** | CDVD Real LPAR (`0x2458438`, `0x500002c00000`) | 12 (4 KiB pages) | 0x80000 | 0x80000 | `0xe000000000000800` | **Rank 3**: 4 KiB page size, 512 KiB length. |
| **#4** | HDD Driver LPAR (`H+0x20`, `0x500002d00000`) | 16 (64 KiB pages) | 0x80000 | 0x80000 | `0xe000000000000800` | **Rank 4**: Cross-device mapping of verified HDD driver LPAR. |
| **#5** | HDD Driver LPAR (`H+0x20`, `0x500002d00000`) | 12 (4 KiB pages) | 0x80000 | 0x80000 | `0xe000000000000800` | **Rank 5**: HDD driver LPAR with 4 KiB pages. |
| **#6** | HDD Driver EA (`H+0x28`, `0x84800000`) | 16 (64 KiB pages) | 0x80000 | 0x80000 | `0xe000000000000800` | **Control**: Negative control testing CPU Effective Address. |
| **#7** | CDVD CPU EA (`0x2458428`, `0x84000000`) | 20 (1 MiB pages) | 0x100000 | 0x100000 | `0xe000000000000800` | **Control**: Negative control replicating P5 Q1 error. |

---

## Expected Results Summary

- **Top Expectation**: Candidate #1 will return `rc = 0`.
- **Immediate Safe Unmap**: The probe immediately issues `lv1_unmap_device_dma_region(4, 2, 0xC0000000, len, 0, 0)`, frees the region (`175`), closes device 2 (`171`), and terminates with zero DMA commands executed.
