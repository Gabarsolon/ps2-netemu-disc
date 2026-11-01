# P2D K0 result (console, 2026-11-01, PS2 disc inserted; read from the owner's video 20261101_115651.mp4)

`P2D-K0 DONE: ALL STEPS OK`; `RC: OP=0 DMA=0 CL=0 HC=130` (open, DMA region allocate/free, close all 0; 130 hypercalls in total, no timeouts); pages for the steps K0 does not run read `NOT RUN IN K0`; the ROM node is shown as `BUS 4 DEV 2 REG 0`.

SB_CDVD buffer fields as the build printed them:
- `CDVD LPAR: 0x0000500002c00000` (value read at 0x2458438)
- `CDVD EA:   0x0000000084000000 SZ=100000` (value read at 0x2458428; size 1 MiB at 0x2458430)

## DEFECT FOUND (do not install K1..K3)
The two values are SWAPPED relative to their names. The HDD driver state measured in P2C has BUF_EA = 0x0000500002d00000 (a CPU address) and LPARBUF = 0x0000000084800000 (a partition-physical address). The SB_CDVD pair has the same shape: 0x500002c00000 is the CPU/EA value and 0x84000000 is the LPAR value, but the P2D code uses `lpar = *(0x2458438)` = 0x500002c00000 and `ea = *(0x2458428)` = 0x84000000. K1..K3 would therefore pass an EA as the LPAR address to lv1_map_device_dma_region and would write the command block through a CPU pointer 0x84000000 that is probably not mapped (a fault would kill the partition). K0 does not use the pointers, so K0 is not affected.
