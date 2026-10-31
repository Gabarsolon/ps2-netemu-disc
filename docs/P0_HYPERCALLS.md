# P0 LV1 call inventory

**PROVEN (local decoding):** Ghidra decoded all 557 opcode matches. There are 20 `sc 1` words, of which one is an opcode-table entry rather than an identified executable callsite. The remaining 537 words are `sc 0`; only the constant high-bit syscall subset below is classified as forwarding to LV1. Opcode matches alone do not prove execution.

**INFERRED:** number-to-name mappings use the public Linux header; locally reconstructed r11 values and ELFv1 descriptor bounds identify candidate wrappers. Caller counts are unique direct call instruction references in Ghidra, not runtime counts. Indirect calls and unanalysed references can add callers; a zero is a lower bound. A wrapper may contain multiple call numbers. None of this proves partition permission.

Source: [Linux LV1 declarations](https://raw.githubusercontent.com/torvalds/linux/master/arch/powerpc/include/asm/lv1call.h); [wiki call reference](https://www.psdevwiki.com/ps3/HV_Syscall_Reference). Raw disassembly/context and descriptor references remain local.

## Direct `sc 1` words

| Site | Number | Containing wrapper / block | Direct callers (lower bound) | Interpretation |
|---|---|---|---:|---|
| 0x18 | 0xff | 00000014 | 6 | panic; high confidence numeric identification |
| 0x988 | 0xff | trap block 0x984 | 0 | panic; high confidence numeric identification |
| 0xca0 | dynamic / data | exception bridge 0x0c00 | 0 | Dynamic generic forwarder; r11 supplied by guest syscall |
| 0xf40 | 0xff | trap block 0xf3c | 0 | panic; high confidence numeric identification |
| 0xf50 | 0xff | trap block 0xf4c | 0 | panic; high confidence numeric identification |
| 0xf60 | 0xff | trap block 0xf5c | 0 | panic; high confidence numeric identification |
| 0x1208 | 0xff | trap block 0x1204 | 0 | panic; high confidence numeric identification |
| 0x1608 | 0xff | trap block 0x1604 | 0 | panic; high confidence numeric identification |
| 0x1708 | 0xff | trap block 0x1704 | 0 | panic; high confidence numeric identification |
| 0x1808 | 0xff | trap block 0x1804 | 0 | panic; high confidence numeric identification |
| 0x1a64 | 0xff | trap block 0x1a60 | 0 | panic; high confidence numeric identification |
| 0x1aa8 | 0xff | trap block 0x1aa4 | 0 | panic; high confidence numeric identification |
| 0x1af8 | 0xff | trap block 0x1af4 | 0 | panic; high confidence numeric identification |
| 0x1b08 | 0xff | trap block 0x1b04 | 0 | panic; high confidence numeric identification |
| 0x1b18 | 0xff | trap block 0x1b14 | 0 | panic; high confidence numeric identification |
| 0x1b28 | 0xff | trap block 0x1b24 | 0 | panic; high confidence numeric identification |
| 0x12e10 | 0xa2 | guest syscall dispatcher 0x12670 | 0 | read_virtual_uart; high confidence numeric identification |
| 0x134e4 | 0xa2 | guest syscall dispatcher 0x12670 | 0 | read_virtual_uart; high confidence numeric identification |
| 0x13644 | 0xf8 | 0x135fc | 0 | storage_send_device_command; command 0x88 = ENCDEC path |
| 0x13730 | dynamic / data | table at 0x13670.. | 0 | Opcode template table: excluded from executable-call totals |

## Constant guest calls forwarded to LV1

**INFERRED:** `li r11,N; oris r11,r11,0x8000; sc 0` reaches the bridge at `0xc50..0xcbc`; `xoris` removes the high bit before `sc 1` at `0xca0`. The bridge checks the number and a privilege table. Local constants below must not be interpreted as a permission allow-list.

| Number (hex / decimal) | Public name / confidence | Wrapper entry | Direct callers (lower bound) | Guest `sc 0` sites |
|---|---|---|---:|---|
| 0x0 / 0 | allocate_memory; high (number) | 0x1622c | 5 | 0x16314 |
| 0x1 / 1 | write_htab_entry; high (number) | 0x16790 | 28 | 0x16ce4 |
| 0x1 / 1 | write_htab_entry; high (number) | 0x17324 | 0 | 0x18e98, 0x18ed8 |
| 0x2 / 2 | construct_virtual_address_space; high (number) | 0x17324 | 0 | 0x17b50 |
| 0x7 / 7 | select_virtual_address_space; high (number) | 0x17324 | 0 | 0x17b70 |
| 0x9 / 9 | pause; high (number) | 0x118290 | 0 | 0x118324 |
| 0x9 / 9 | pause; high (number) | 0x11db84 | 0 | 0x11dde4, 0x11de3c, 0x11deec |
| 0xf / 15 | put_iopte; high (number) | 0x1c2e4 | 1 | 0x1cbac, 0x1cc2c |
| 0x12 / 18 | construct_event_receive_port; high (number) | 0x12be04 | 1 | 0x12bfa0 |
| 0x12 / 18 | construct_event_receive_port; high (number) | 0x137af8 | 1 | 0x137b7c |
| 0x1a / 26 | not named in inspected Linux header; UNKNOWN name | 0x4c6e0 | 0 | 0x4c750 |
| 0x1b / 27 | end_of_interrupt; high (number) | 0x114500 | 0 | 0x1145e0 |
| 0x1b / 27 | end_of_interrupt; high (number) | 0x1146a0 | 0 | 0x1147ac |
| 0x1b / 27 | end_of_interrupt; high (number) | 0x114868 | 0 | 0x114a64 |
| 0x1b / 27 | end_of_interrupt; high (number) | 0x1181b0 | 0 | 0x11822c |
| 0x1b / 27 | end_of_interrupt; high (number) | 0x12b320 | 0 | 0x12b33c |
| 0x1b / 27 | end_of_interrupt; high (number) | 0x137590 | 0 | 0x13763c |
| 0x1b / 27 | end_of_interrupt; high (number) | 0x4c94c | 0 | 0x4c9cc |
| 0x1b / 27 | end_of_interrupt; high (number) | 0xba474 | 0 | 0xba4e0, 0xba548 |
| 0x1b / 27 | end_of_interrupt; high (number) | 0xba564 | 0 | 0xba5c8 |
| 0x1c / 28 | connect_irq_plug; high (number) | 0x12be04 | 1 | 0x12bfec |
| 0x1c / 28 | connect_irq_plug; high (number) | 0x137af8 | 1 | 0x137bc4 |
| 0x1c / 28 | connect_irq_plug; high (number) | 0x18f90 | 3 | 0x19018 |
| 0x1c / 28 | connect_irq_plug; high (number) | 0x19c7c | 1 | 0x1a0e4, 0x1a160 |
| 0x1c / 28 | connect_irq_plug; high (number) | 0x1bfbc | 1 | 0x1c000 |
| 0x1c / 28 | connect_irq_plug; high (number) | 0x1d768 | 1 | 0x1d7ac |
| 0x39 / 57 | construct_logical_spe; high (number) | 0x1139ac | 1 | 0x113a34 |
| 0x3d / 61 | set_spe_interrupt_mask; high (number) | 0x18f90 | 3 | 0x19038 |
| 0x42 / 66 | clear_spe_interrupt_status; high (number) | 0x114500 | 0 | 0x1145c8 |
| 0x42 / 66 | clear_spe_interrupt_status; high (number) | 0x1146a0 | 0 | 0x114794 |
| 0x42 / 66 | clear_spe_interrupt_status; high (number) | 0x114868 | 0 | 0x114a4c |
| 0x43 / 67 | get_spe_interrupt_status; high (number) | 0x114500 | 0 | 0x11456c |
| 0x43 / 67 | get_spe_interrupt_status; high (number) | 0x1146a0 | 0 | 0x114724 |
| 0x43 / 67 | get_spe_interrupt_status; high (number) | 0x114868 | 0 | 0x114910 |
| 0x45 / 69 | get_logical_ppe_id; high (number) | 0x17324 | 0 | 0x1761c |
| 0x49 / 73 | set_interrupt_mask; high (number) | 0x17324 | 0 | 0x18b6c |
| 0x4a / 74 | get_logical_partition_id; high (number) | 0x17324 | 0 | 0x17600 |
| 0x4e / 78 | get_spe_irq_outlet; high (number) | 0x18f90 | 3 | 0x18ff4 |
| 0x5b / 91 | read_repository_node; high (number) | 0x111eb8 | 22 | 0x111f10 |
| 0x5b / 91 | read_repository_node; high (number) | 0x11b47c | 1 | 0x11b4c0 |
| 0x5b / 91 | read_repository_node; high (number) | 0x1e808 | 1 | 0x1e874 |
| 0x5b / 91 | read_repository_node; high (number) | 0x1e9b28 | 0 | 0x1e9b70 |
| 0x5b / 91 | read_repository_node; high (number) | 0x1e9ba0 | 1 | 0x1e9c4c, 0x1e9cf0, 0x1e9d30, 0x1e9d8c, 0x1e9dfc, 0x1e9e44, 0x1e9e8c |
| 0x5b / 91 | read_repository_node; high (number) | 0x1e9f60 | 0 | 0x1e9f90 |
| 0x5b / 91 | read_repository_node; high (number) | 0x1e9fd8 | 0 | 0x1ea040, 0x1ea08c |
| 0x5b / 91 | read_repository_node; high (number) | 0x1ea110 | 0 | 0x1ea14c |
| 0x5b / 91 | read_repository_node; high (number) | 0x1ea18c | 0 | 0x1ea1b8 |
| 0x5b / 91 | read_repository_node; high (number) | 0x1ea1e8 | 1 | 0x1ea210 |
| 0x5b / 91 | read_repository_node; high (number) | 0x1ea240 | 1 | 0x1ea268 |
| 0x5f / 95 | read_htab_entries; high (number) | 0x16790 | 28 | 0x16998, 0x16c28 |
| 0x61 / 97 | not named in inspected Linux header; UNKNOWN name | 0x17324 | 0 | 0x18f18 |
| 0x62 / 98 | not named in inspected Linux header; UNKNOWN name | 0x17324 | 0 | 0x17b28 |
| 0x74 / 116 | allocate_io_segment; high (number) | 0x1c2e4 | 1 | 0x1cb70 |
| 0x76 / 118 | not named in inspected Linux header; UNKNOWN name | 0x1c2e4 | 1 | 0x1cb34, 0x1cb4c |
| 0x78 / 120 | construct_io_irq_outlet; high (number) | 0x19c7c | 1 | 0x1a0bc, 0x1a138 |
| 0x7c / 124 | not named in inspected Linux header; UNKNOWN name | 0x119b9c | 0 | 0x119d68 |
| 0x7c / 124 | not named in inspected Linux header; UNKNOWN name | 0x11a028 | 0 | 0x11a240 |
| 0x7c / 124 | not named in inspected Linux header; UNKNOWN name | 0x1291bc | 1 | 0x129268 |
| 0x7c / 124 | not named in inspected Linux header; UNKNOWN name | 0x12a528 | 8 | 0x12a8c8 |
| 0x7d / 125 | not named in inspected Linux header; UNKNOWN name | 0x11976c | 0 | 0x119938 |
| 0x7d / 125 | not named in inspected Linux header; UNKNOWN name | 0x11a310 | 0 | 0x11a558 |
| 0x7d / 125 | not named in inspected Linux header; UNKNOWN name | 0x128ccc | 2 | 0x128ed4 |
| 0x7e / 126 | not named in inspected Linux header; UNKNOWN name | 0x119df8 | 0 | 0x119fb4 |
| 0x88 / 136 | not named in inspected Linux header; UNKNOWN name | 0x1199c8 | 0 | 0x119b5c |
| 0x8c / 140 | construct_lpm; high (number) | 0x1183cc | 0 | 0x1183f4 |
| 0x8d / 141 | destruct_lpm; high (number) | 0x11842c | 0 | 0x11843c |
| 0x8e / 142 | start_lpm; high (number) | 0x11844c | 0 | 0x11845c |
| 0x8f / 143 | stop_lpm; high (number) | 0x11846c | 0 | 0x11848c |
| 0x90 / 144 | copy_lpm_trace_buffer; high (number) | 0x1184b4 | 0 | 0x1184d4 |
| 0x91 / 145 | add_lpm_event_bookmark; high (number) | 0x1184fc | 0 | 0x11850c |
| 0x92 / 146 | delete_lpm_event_bookmark; high (number) | 0x11851c | 0 | 0x11852c |
| 0x93 / 147 | set_lpm_interrupt_mask; high (number) | 0x11853c | 0 | 0x11855c |
| 0x94 / 148 | get_lpm_interrupt_status; high (number) | 0x118584 | 0 | 0x1185a4 |
| 0x95 / 149 | set_lpm_general_control; high (number) | 0x1185cc | 0 | 0x1185f4 |
| 0x96 / 150 | set_lpm_interval; high (number) | 0x118624 | 0 | 0x118644 |
| 0x97 / 151 | set_lpm_trigger_control; high (number) | 0x11866c | 0 | 0x11868c |
| 0x98 / 152 | set_lpm_counter_control; high (number) | 0x1186b4 | 0 | 0x1186d4 |
| 0x99 / 153 | set_lpm_group_control; high (number) | 0x1186fc | 0 | 0x11871c |
| 0x9a / 154 | set_lpm_debug_bus_control; high (number) | 0x118744 | 0 | 0x118764 |
| 0x9b / 155 | set_lpm_counter; high (number) | 0x11878c | 0 | 0x1187b4 |
| 0x9c / 156 | set_lpm_signal; high (number) | 0x1187e4 | 0 | 0x1187f4 |
| 0x9d / 157 | set_lpm_spr_trigger; high (number) | 0x118804 | 0 | 0x118814 |
| 0xa3 / 163 | write_virtual_uart; high (number) | 0x11810c | 34 | 0x118154 |
| 0xa4 / 164 | set_virtual_uart_param; high (number) | 0x1d6b0 | 2 | 0x1d6dc, 0x1d72c |
| 0xa5 / 165 | get_virtual_uart_param; high (number) | 0x1d6b0 | 2 | 0x1d6f8 |
| 0xa6 / 166 | configure_virtual_uart_irq; high (number) | 0x1d768 | 1 | 0x1d790 |
| 0xaa / 170 | open_device; high (number) | 0x12be04 | 1 | 0x12bf8c |
| 0xaa / 170 | open_device; high (number) | 0x137af8 | 1 | 0x137b68 |
| 0xaa / 170 | open_device; high (number) | 0x19c7c | 1 | 0x19d48 |
| 0xaa / 170 | open_device; high (number) | 0x1e7928 | 1 | 0x1e79a4 |
| 0xab / 171 | close_device; high (number) | 0x12d420 | 1 | 0x12d610 |
| 0xab / 171 | close_device; high (number) | 0x1373e0 | 1 | 0x137440 |
| 0xab / 171 | close_device; high (number) | 0x1e7760 | 0 | 0x1e77b4 |
| 0xac / 172 | map_device_mmio_region; high (number) | 0x19c7c | 1 | 0x19e14, 0x19fe0 |
| 0xae / 174 | allocate_device_dma_region; high (number) | 0x12be04 | 1 | 0x12c03c |
| 0xae / 174 | allocate_device_dma_region; high (number) | 0x137af8 | 1 | 0x137c04 |
| 0xae / 174 | allocate_device_dma_region; high (number) | 0x19ac0 | 0 | 0x19b34 |
| 0xae / 174 | allocate_device_dma_region; high (number) | 0x19c7c | 1 | 0x19ebc, 0x19efc, 0x1a054 |
| 0xae / 174 | allocate_device_dma_region; high (number) | 0x1a200 | 1 | 0x1a27c |
| 0xaf / 175 | free_device_dma_region; high (number) | 0x12d420 | 1 | 0x12d5fc |
| 0xaf / 175 | free_device_dma_region; high (number) | 0x1373e0 | 1 | 0x13742c |
| 0xaf / 175 | free_device_dma_region; high (number) | 0x1e7760 | 0 | 0x1e77a0 |
| 0xb0 / 176 | map_device_dma_region; high (number) | 0x160fc | 5 | 0x16134 |
| 0xb1 / 177 | unmap_device_dma_region; high (number) | 0x12d420 | 1 | 0x12d5e4 |
| 0xb1 / 177 | unmap_device_dma_region; high (number) | 0x1373e0 | 1 | 0x137414 |
| 0xb1 / 177 | unmap_device_dma_region; high (number) | 0x1e7760 | 0 | 0x1e7788 |
| 0xb2 / 178 | not named in inspected Linux header; UNKNOWN name | 0x1e9ba0 | 1 | 0x1e9ed8 |
| 0xb3 / 179 | not named in inspected Linux header; UNKNOWN name | 0x1e9ba0 | 1 | 0x1e9f20, 0x1e9f50 |
| 0xc5 / 197 | connect_interrupt_event_receive_port; high (number) | 0x12be04 | 1 | 0x12bfd0 |
| 0xc5 / 197 | connect_interrupt_event_receive_port; high (number) | 0x137af8 | 1 | 0x137ba8 |
| 0xcf / 207 | enable_logical_spe; high (number) | 0x112f18 | 0 | 0x112f74 |
| 0xcf / 207 | enable_logical_spe; high (number) | 0x1139ac | 1 | 0x113a70 |
| 0xd2 / 210 | gpu_open; high (number) | 0x1c2e4 | 1 | 0x1c65c |
| 0xd4 / 212 | gpu_device_map; high (number) | 0x1c2e4 | 1 | 0x1c680, 0x1c6c0, 0x1c700, 0x1c740, 0x1c780 |
| 0xd6 / 214 | gpu_memory_allocate; high (number) | 0x1c2e4 | 1 | 0x1c8b8 |
| 0xd9 / 217 | gpu_context_allocate; high (number) | 0x1c2e4 | 1 | 0x1c8e4 |
| 0xdd / 221 | gpu_context_iomap; high (number) | 0x1609c | 2 | 0x160cc |
| 0xe1 / 225 | gpu_context_attribute; high (number) | 0x115814 | 0 | 0x11584c |
| 0xe1 / 225 | gpu_context_attribute; high (number) | 0x11587c | 0 | 0x1158b4 |
| 0xe1 / 225 | gpu_context_attribute; high (number) | 0x1158e4 | 0 | 0x11591c |
| 0xe1 / 225 | gpu_context_attribute; high (number) | 0x1a458 | 2 | 0x1a610 |
| 0xe1 / 225 | gpu_context_attribute; high (number) | 0x1bfbc | 1 | 0x1c220 |
| 0xe3 / 227 | gpu_context_intr; high (number) | 0x4c94c | 0 | 0x4c980 |
| 0xe4 / 228 | gpu_attribute; high (number) | 0x1bfbc | 1 | 0x1c168, 0x1c1a4, 0x1c1cc, 0x1c270 |
| 0xf5 / 245 | storage_read; high (number) | 0x12b5fc | 2 | 0x12b674 |
| 0xf5 / 245 | storage_read; high (number) | 0x1e77c8 | 5 | 0x1e7850 |
| 0xf6 / 246 | storage_write; high (number) | 0x12c110 | 0 | 0x12c5ac, 0x12c87c, 0x12ca9c |
| 0xf6 / 246 | storage_write; high (number) | 0x12cc98 | 0 | 0x12cd6c |
| 0xf6 / 246 | storage_write; high (number) | 0x12ce80 | 2 | 0x12cfd4 |
| 0xf6 / 246 | storage_write; high (number) | 0x12d420 | 1 | 0x12d50c |
| 0xf9 / 249 | storage_get_async_status; high (number) | 0x12b320 | 0 | 0x12b350 |
| 0xf9 / 249 | storage_get_async_status; high (number) | 0x137590 | 0 | 0x1375dc |
| 0xf9 / 249 | storage_get_async_status; high (number) | 0x1e77c8 | 5 | 0x1e787c |

## Coverage limits

**UNKNOWN:** indirect callers, execution of every recovered wrapper, and runtime device permissions. The local r11 walk deliberately leaves dynamic/unresolved cases unresolved. A name absent from this table may still be issued through a dynamic bridge.

**INFERRED:** there is no identified constant `storage_check_async_status` (254) call, or constant `net_*` / `gelic_*` call in this scan. The identified device command (248) is the dedicated ENCDEC command-0x88 path, not an ATAPI optical implementation. Generic open/close are 170/171, not separate storage-open/storage-close numbers.
