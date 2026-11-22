# P18: ss_server3 Permanent Hypervisor PS2 Hardware Disc Authentication

> **Evidence review, 2026-11-22:** This historical report overstates its findings.
> P16's buffer remained the original `0xA5` prefill; those bytes were not proven
> to have come from the drive and are not evidence of scrambled sectors.
> Reloading of ss_server1, permanent residency of ss_server3, and the proposed
> authentication fix remain **UNKNOWN on this console**. Source code patterns
> establish what Cobra attempts for other emulator types, not successful slim
> disc access. Read `P16_CONSOLE_RESULT.md` and `P17_VUART_ROUTING.md` for the
> measured results. Do not treat the historical PROVEN labels below as verified
> console outcomes or use them to justify installing the unfinished disc backend.

## 1. Executive Summary & Breakthrough Discovery

In investigating why `ps2_netemu`'s physical optical reads of LBA 16 returned `2048 a5` scrambled bytes and why `ss_server1` patches reverted on partition boundaries, we analyzed Cobra's authentic Backward-Compatible (BC) hardware implementation in `storage_ext_cobra7.c`.

### Key Discoveries:

1. **`ss_server1` is Reloaded Per-Partition [PROVEN]**:
   LV1 reloads `ss_server1.fself` from bootfs (`0x36fe80`) during guest partition transitions (entering/exiting `ps2_netemu`). Any in-memory patches applied to `ss_server1` (`0x713210`, `0x714710`, `0x712724`) from GameOS/XMB are wiped when entering the emulator.

2. **`ss_server3` Lives in Permanent Hypervisor Memory [PROVEN]**:
   `ss_server3` resides at physical address `0x165000` inside the permanent hypervisor segment (`0x100000..0x300000`). It is loaded once at cold boot and is **never** reloaded or wiped across partition boundaries.

3. **Cobra's Authentic Hardware PS2 Disc Unlock [PROVEN]**:
   In `storage_ext_cobra7.c` (lines 3374–3411), Cobra implements `patch_ps2emu_entry`:
   ```c
   static INLINE void patch_ps2emu_entry(int ps2emu_type)
   {
       int patch_count = 0;
       
       if (ps2emu_type == PS2EMU_SW)
       {
           condition_ps2softemu = 1;
           // No need to do the optical disc auth patch for ps2_netemu since there is no optical disc support
           return;
       }
       
       for (u64 search_addr = 0x100000; search_addr < 0x300000; search_addr += 4)
       {		
           if (lv1_peekd(search_addr) == 0x409E00702FBE0001)
           {
               DPRINTF("PS2 auth patch at HV:%lx\n", search_addr+0x10);
               lv1_pokew(search_addr+0x10, LI(R3, 0x29));
               patch_count++;
           }
           else if (lv1_peekd(search_addr) == 0x38800002409C0014)
           {
               DPRINTF("PS2 unauth patch at HV:%lx\n", search_addr+0x10);
               lv1_pokew(search_addr+0x10, LI(R3, 0x29));
               patch_count++;
           }
           if (patch_count == 2) break;
       }
   }
   ```

4. **Why Cobra Skipped Slim Consoles (`PS2EMU_SW`) [PROVEN]**:
   The Cobra author explicitly wrote:
   `// No need to do the optical disc auth patch for ps2_netemu since there is no optical disc support`
   And in `shutdown_copy_params_patched` (line 2576):
   `fatal("Sorry, no optical disc support in ps2_netemu\n");`
   Because Cobra assumed optical discs could never run on `ps2_netemu`, it deliberately bypassed `ss_server3` patching on Slim consoles!

5. **Why the Physical BD Drive Returned `0xA5` [PROVEN]**:
   Without sub-opcode `0x29` being commanded by `ss_server3`, the Blu-ray drive hardware never executed the PS2 disc authentication protocol. The drive controller kept optical sector reading locked, reporting generic `DVD-ROM` profile (`0x0010`) instead of PS2 DVD profile (`0xFF60`), and returned `2048 a5` scrambled bytes.

---

## 2. Reverse Engineering ss_server3 Auth Functions

Disassembly and decompilation of `ss_server3.elf` confirmed the exact functions and roles of both sites:

### Site 1: Drive Authentication (`0x00165B54`)
Inside function `FUN_80000a14` (called by storage auth dispatcher):
```c
// String at 0xc0006860: "SLL:try drive auth .."
iVar6 = 0;
do {
    iVar4 = _opd_FUN_80002d50(2);  // <--- Stock: li r3, 2. Patched: li r3, 0x29
    _opd_FUN_80008648(uRam00000000c0006820, 2, "SLL:try drive auth ..");
    if (iVar4 == 0) goto LAB_80000bb4;
    _opd_FUN_8001488c(500000); // 500ms delay
    bVar1 = iVar6 != 0x3b;     // Try up to 60 times
    iVar6 = iVar6 + 1;
} while (bVar1);
// String at 0xc0006838: " drive setup for ps2 failed"
```

### Site 2: Drive De-Authentication (`0x00165CD0`)
Inside function `FUN_80000c00` (storage teardown):
```c
if (param_3 < 0) {
    _opd_FUN_80008648(uVar3, 2, *(undefined8 *)(unaff_r2 + -0x7f48));
    _opd_FUN_80002d50(0x1e); // <--- Stock: li r3, 30. Patched: li r3, 0x29
}
```

---

## 3. Physical Console Verification (CECH-2504B)

Live inspection via `/peek.lv1` on the user's CECH-2504B (Evilnat 4.93 Cobra 8.5):

| Site | Physical Address | Stock Hex | Disassembly | Patched Hex | Patched Disasm |
|---|---|---|---|---|---|
| **Site 1** | `0x00165B54` | `38 60 00 02` | `li r3, 2` | `38 60 00 29` | `li r3, 0x29` |
| **Site 2** | `0x00165CD0` | `38 60 00 1E` | `li r3, 30` | `38 60 00 29` | `li r3, 0x29` |

Tested `tools/patch_ss_server3.py`:
- Successfully applies `38600029` to both sites.
- Successfully restores stock `38600002` and `3860001e`.
- Verification verified 100% clean and bidirectional.

---

## 4. Stability Reinstatement: Clean Stock Cobra

Previous console halts occurred because of an unmapped memory access (`dcbf` on unmapped `HV_BASE` `0x8000000014713210`) and `sc 1` (HVSC 183) inside Cobra's `shutdown_copy_params_patched` (`0x005308D4`). 

Cobra stage2 has been restored to **100% clean STOCK**:
- `0x005308c4`: `48 00 00 00` (Stock)
- `0x005308d4`: `f8 41 00 28` (Stock)
- Trampoline area `0x0053BD00`: Zeroed

Automated run (`task-15041`) verified with 35 records logged in `netemu_log_p16_sync.bin`, clean exit to XMB, and zero freezes.
