# The optical-read wall and the strategy fork, 2026-11-22

Written after owned_control was **console-proven** (`status: owned`, live owned
buffer EA `0x80022440` / LPAR `0x3b22440`, data region LPAR `0x3b23500`). That
buffer is a valid DMA target. The problem is not the buffer — it is reaching the
drive at all from the netemu partition.

## The wall (PROVEN)

- **PROVEN on console (P1b + ablation):** `lv1_open_device(4,2,0)` issued from the
  netemu partition on Evilnat 4.93 **immediately powers off the console** (Syscon
  power cut, not a soft freeze). With the open call ablated, the build runs
  normally. See `docs/P0I_LV1_493_ANALYSIS.md` §5/§7 and `docs/P0H_LV1_ANALYSIS.md` §6.
- **PROVEN (4.93 LV1 static):** the LV1 storage open code is itself non-fatal
  (returns `0`/`-4`/`-6`). The power-off comes from the environment: `sysmgr_ss`
  runs `PS2_NE_LPAR` with the **BD-drive PCI bridge left unpowered/unclocked**
  (vtable method `+0xc0` stubbed, `0x8001dad8`), and the netemu guest kernel
  wires interrupts **only for HDD (IRQ 0x12) and VUART 2** — no optical IRQ
  handler. Any hardware bus access / IRQ assertion after opening the optical
  node → Southbridge bus error / checkstop or guest panic `lv1_panic(0x11f)` →
  main power off.
- **PROVEN:** the netemu has **no native ATAPI/optical path** at all. Its CDVD
  dispatcher `0x1359d4` reads sectors only as **file reads via its UFS reader**
  `0x1ed5cc` (ISO on HDD) or the Cobra container path. See `docs/P0_CDVD_NOTES.md`.

**Conclusion:** the netemu is structurally forbidden from touching the optical
drive. Making it do so requires powering the BD bridge + wiring the optical IRQ
+ granting the netemu LPAR optical repository auth — i.e. editing **core firmware
(`sysmgr_ss` / LV1)**, which the project's hard safety rule forbids
(`No other /dev_flash files may ever be written`), and each probe risks the
instant power-off. The netemu-only path (Route B, owned memory → netemu DMA from
drive) **cannot complete** without crossing that firmware boundary.

## What is still allowed and might work

**GameOS/Cobra CAN read the disc.** The inserted TDU disc is visible as files at
`/dev_bdvd/SLES_544.66`, `/dev_bdvd/SYSTEM.CNF` over FTP — read by LV2/Cobra,
which *is* permitted to touch the drive. The netemu reads its "disc" as a file
through UFS. So the safety-compatible architecture is:

> **Cobra presents the physical `/dev_bdvd` disc to the netemu as its ISO source**
> (a sector map / mount), so optical reads stay in GameOS/Cobra and the netemu
> uses its normal file path. **No netemu optical access, no firmware change.**

Open question: whether Cobra's rawseciso/netiso-style mapping can target the live
`/dev_bdvd` device (not an HDD ISO file) and keep serving it after LV2 teardown
at PS2 launch. The earlier direct `/play.ps3` physical-disc run (ss_server3 + LV2
Cobra optical panic bypass) launched but left sector buffers unchanged — that is
the symptom of optical sectors not being delivered across the launch boundary,
and is the thing to solve in this route, instead of making netemu open the drive.

## The fork (needs the owner's decision)

1. **Cobra-feeds-netemu (RECOMMENDED, safety-compatible).** Investigate/make
   Cobra map `/dev_bdvd` as the netemu ISO source. No `/dev_flash` writes beyond
   the netemu, no deliberate optical access from netemu, lower power-off risk.
   Likely still needs Cobra/LV2 live RAM work (owner-OK per the LV1/LV2 rule),
   but not core-firmware flashing.
2. **Firmware route (NOT recommended, violates a stated hard rule).** Patch
   `sysmgr_ss`/LV1 to power the BD bridge, wire the optical IRQ, and grant the
   netemu LPAR optical auth. This is core `/dev_flash` modification the AGENTS
   safety rules forbid, with repeated instant-power-off risk during development.

Until the owner picks, no optical-open build is sent to the console (it is a
PROVEN power-off).
