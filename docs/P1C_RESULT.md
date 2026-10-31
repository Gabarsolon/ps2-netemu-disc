# P1c / P1c2 result: repository fields of the optical node vs the HDD node (console, 2026-10-31)

Build `local_only/p1c2/ps2_netemu_p1c2.self` (sha256 `1f5cc5250f87f5f0c90138dbb4d31f55c9e86e64204d9ae5af39637d55e50ace`), repository reads only (LV1 91). Source: owner's phone video `20261031_192543.mp4` (31 s), frames read by the orchestrator (low-byte values only where the label says so). No disc inserted. P06 (HDD port) and P22 were not captured.

| Page | Field | Optical node (OPT) | HDD node |
|---|---|---|---|
| P00 | summary | `r=1 h=1 id=4/2 p=0` | |
| P01/P02 | type | 5 (ROM) | 0 (DISK) |
| P03/P04 | id (device index) | 2 | 3 |
| P05/P06 | port | 0 | (not captured; P1b: 2) |
| P07/P08 | blk_sz | 2048 (0x800) | 512 (0x200) |
| P09/P10 | n_blks (low byte shown) | 0xFF | 0x30 (low byte of 976773168 = 0x3A386030, consistent) |
| P11/P12 | n_regs | 1 | 4 |
| P13/P14 | `meddling` | **1 (ON)** | **0 (OFF)** |
| P15/P16 | pci_b | rc=ERR (key absent) | rc=ERR |
| P17/P18 | intr0 (low byte) | 0x02 | 0x02 |
| P19/P20 | reg0_t | rc=ERR | rc=ERR |
| P21/P22 | intr1 | rc=ERR | (not captured) |
| P23 | BUS4 ndev | 5 devices on bus index 4 | |

## Reading
- **PROVEN (console):** the table above, for the pages captured. The optical node and the HDD node differ in block size, region count and one flag: `meddling` is 1 for the optical node and 0 for the HDD. All other readable fields match in kind (same interrupt line number, same absent PCI/register-type keys).
- **UNKNOWN:** what `meddling` means to LV1 or to the netemu. The stock enumerator `0x114ea4` reads the key into its info block for every device (seen in P0 static analysis); no use of the value was found by us. It is the only repository flag that distinguishes the two nodes and is the leading lead for why the optical open behaves differently. A candidate meaning (INFERRED, unverified): the device is meant to be "meddled with" (shared/proxied) by LV1 or another partition, so a direct open from a guest is not the intended path.
- **INFERRED:** n_regs=1 (one region) vs 4 is the normal difference between an optical drive and a disk; block size 2048 vs 512 likewise.
- Nothing in these fields shows an ownership/ACL entry; assignment is not stored in the repository, consistent with P0G/P0H.

## Next
Ask the LV1 analysis (P0H) what reads and acts on `meddling` in the 3.55 LV1 (open_device and device layer) and whether the legacy PS2 profiles' optical node had the same flag. Restore the stock netemu when finished testing.
