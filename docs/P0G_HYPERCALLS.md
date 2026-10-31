# P0G hypercall inventory

**PROVEN (PC):** raw opcode counts; **INFERRED:** locally reconstructed constant numbers, wrapper grouping and names. These are static candidates, not execution counts or permission grants. Indirect callers and dynamic numbers remain **UNKNOWN**. Official 3.55 inputs are distinct from P0D community inputs. The stock-netemu inventory is reused from P0 and excludes opcode template 0x13730.

| LV1 / name | softemu 3.55 | gxemu 3.55 | emu 3.55 | stock netemu |
|---|---:|---:|---:|---:|
| 0 `allocate_memory` | 4 | 3 | 1 | 1 |
| 1 `write_htab_entry` | 5 | 1 | 2 | 3 |
| 2 `construct_virtual_address_space` | 1 | 1 | 1 | 1 |
| 7 `select_virtual_address_space` | 1 | 1 | 1 | 1 |
| 9 `pause` | 5 | 4 | 9 | 4 |
| 12 `connect_irq_plug_ext` | 0 | 1 | 0 | 0 |
| 13 `release_memory` | 3 | 2 | 0 | 0 |
| 15 `put_iopte` | 2 | 2 | 2 | 2 |
| 18 `construct_event_receive_port` | 8 | 7 | 4 | 2 |
| 24 `send_event_locally` | 2 | 1 | 1 | 0 |
| 26 `UNKNOWN name` | 2 | 2 | 1 | 1 |
| 27 `end_of_interrupt` | 15 | 15 | 4 | 10 |
| 28 `connect_irq_plug` | 16 | 15 | 10 | 7 |
| 54 `destruct_logical_spe` | 1 | 0 | 1 | 0 |
| 57 `construct_logical_spe` | 1 | 1 | 1 | 1 |
| 61 `set_spe_interrupt_mask` | 4 | 4 | 3 | 1 |
| 65 `disable_logical_spe` | 2 | 0 | 0 | 0 |
| 66 `clear_spe_interrupt_status` | 6 | 6 | 3 | 3 |
| 67 `get_spe_interrupt_status` | 3 | 3 | 3 | 3 |
| 69 `get_logical_ppe_id` | 1 | 1 | 0 | 1 |
| 73 `set_interrupt_mask` | 3 | 3 | 1 | 1 |
| 74 `get_logical_partition_id` | 1 | 1 | 0 | 1 |
| 78 `get_spe_irq_outlet` | 4 | 4 | 3 | 1 |
| 91 `read_repository_node` | 19 | 17 | 15 | 18 |
| 95 `read_htab_entries` | 6 | 6 | 3 | 2 |
| 96 `set_dabr` | 16 | 16 | 0 | 0 |
| 97 `UNKNOWN name` | 1 | 1 | 0 | 1 |
| 98 `UNKNOWN name` | 1 | 1 | 0 | 1 |
| 105 `UNKNOWN name` | 2 | 2 | 1 | 0 |
| 106 `UNKNOWN name` | 0 | 0 | 1 | 0 |
| 107 `UNKNOWN name` | 1 | 4 | 1 | 0 |
| 108 `UNKNOWN name` | 1 | 1 | 0 | 0 |
| 109 `UNKNOWN name` | 4 | 6 | 1 | 0 |
| 110 `UNKNOWN name` | 3 | 3 | 0 | 0 |
| 111 `UNKNOWN name` | 10 | 10 | 0 | 0 |
| 112 `UNKNOWN name` | 1 | 1 | 0 | 0 |
| 116 `allocate_io_segment` | 1 | 1 | 2 | 1 |
| 117 `release_io_segment` | 0 | 1 | 4 | 0 |
| 118 `UNKNOWN name` | 2 | 2 | 1 | 2 |
| 119 `UNKNOWN name` | 0 | 2 | 2 | 0 |
| 120 `construct_io_irq_outlet` | 2 | 2 | 2 | 2 |
| 124 `UNKNOWN name` | 3 | 2 | 0 | 4 |
| 125 `UNKNOWN name` | 4 | 4 | 0 | 3 |
| 126 `UNKNOWN name` | 3 | 3 | 0 | 1 |
| 136 `UNKNOWN name` | 3 | 3 | 0 | 1 |
| 140 `construct_lpm` | 1 | 1 | 0 | 1 |
| 141 `destruct_lpm` | 1 | 1 | 0 | 1 |
| 142 `start_lpm` | 1 | 1 | 0 | 1 |
| 143 `stop_lpm` | 1 | 1 | 0 | 1 |
| 144 `copy_lpm_trace_buffer` | 1 | 1 | 0 | 1 |
| 145 `add_lpm_event_bookmark` | 1 | 1 | 0 | 1 |
| 146 `delete_lpm_event_bookmark` | 1 | 1 | 0 | 1 |
| 147 `set_lpm_interrupt_mask` | 1 | 1 | 0 | 1 |
| 148 `get_lpm_interrupt_status` | 1 | 1 | 0 | 1 |
| 149 `set_lpm_general_control` | 1 | 1 | 0 | 1 |
| 150 `set_lpm_interval` | 1 | 1 | 0 | 1 |
| 151 `set_lpm_trigger_control` | 1 | 1 | 0 | 1 |
| 152 `set_lpm_counter_control` | 1 | 1 | 0 | 1 |
| 153 `set_lpm_group_control` | 1 | 1 | 0 | 1 |
| 154 `set_lpm_debug_bus_control` | 1 | 1 | 0 | 1 |
| 155 `set_lpm_counter` | 1 | 1 | 0 | 1 |
| 156 `set_lpm_signal` | 1 | 1 | 0 | 1 |
| 157 `set_lpm_spr_trigger` | 1 | 1 | 0 | 1 |
| 162 `read_virtual_uart` | 2 | 2 | 2 | 2 |
| 163 `write_virtual_uart` | 1 | 1 | 1 | 1 |
| 164 `set_virtual_uart_param` | 2 | 2 | 2 | 2 |
| 165 `get_virtual_uart_param` | 1 | 1 | 4 | 1 |
| 166 `configure_virtual_uart_irq` | 1 | 1 | 1 | 1 |
| 170 `open_device` | 7 | 6 | 6 | 4 |
| 171 `close_device` | 3 | 3 | 6 | 3 |
| 172 `map_device_mmio_region` | 6 | 4 | 3 | 2 |
| 173 `unmap_device_mmio_region` | 0 | 0 | 3 | 0 |
| 174 `allocate_device_dma_region` | 9 | 8 | 18 | 7 |
| 175 `free_device_dma_region` | 3 | 3 | 23 | 3 |
| 176 `map_device_dma_region` | 7 | 6 | 18 | 1 |
| 177 `unmap_device_dma_region` | 3 | 3 | 23 | 3 |
| 178 `read_pci_config` | 3 | 2 | 1 | 1 |
| 179 `write_pci_config` | 6 | 4 | 2 | 2 |
| 185 `net_add_multicast_address` | 2 | 2 | 2 | 0 |
| 186 `net_remove_multicast_address` | 2 | 2 | 2 | 0 |
| 187 `net_start_tx_dma` | 3 | 3 | 1 | 0 |
| 188 `net_stop_tx_dma` | 2 | 2 | 2 | 0 |
| 189 `net_start_rx_dma` | 4 | 4 | 3 | 0 |
| 190 `net_stop_rx_dma` | 2 | 2 | 2 | 0 |
| 191 `net_set_interrupt_status_indicator` | 1 | 1 | 1 | 0 |
| 193 `net_set_interrupt_mask` | 5 | 5 | 4 | 0 |
| 194 `net_control` | 7 | 7 | 6 | 0 |
| 195 `UNKNOWN name` | 1 | 1 | 1 | 0 |
| 196 `UNKNOWN name` | 1 | 1 | 1 | 0 |
| 197 `connect_interrupt_event_receive_port` | 5 | 5 | 3 | 2 |
| 199 `get_spe_all_interrupt_statuses` | 3 | 3 | 0 | 0 |
| 202 `deconfigure_virtual_uart_irq` | 0 | 0 | 1 | 0 |
| 207 `enable_logical_spe` | 2 | 1 | 1 | 2 |
| 210 `gpu_open` | 1 | 1 | 1 | 1 |
| 211 `gpu_close` | 0 | 1 | 1 | 0 |
| 212 `gpu_device_map` | 1 | 1 | 1 | 5 |
| 213 `gpu_device_unmap` | 0 | 1 | 1 | 0 |
| 214 `gpu_memory_allocate` | 1 | 1 | 2 | 1 |
| 216 `gpu_memory_free` | 0 | 1 | 1 | 0 |
| 217 `gpu_context_allocate` | 1 | 1 | 2 | 1 |
| 218 `gpu_context_free` | 0 | 1 | 1 | 0 |
| 221 `gpu_context_iomap` | 2 | 1 | 1 | 1 |
| 222 `UNKNOWN name` | 0 | 0 | 2 | 0 |
| 225 `gpu_context_attribute` | 8 | 6 | 1 | 5 |
| 227 `gpu_context_intr` | 1 | 1 | 0 | 1 |
| 228 `gpu_attribute` | 8 | 8 | 3 | 4 |
| 245 `storage_read` | 5 | 5 | 3 | 2 |
| 246 `storage_write` | 8 | 14 | 7 | 6 |
| 248 `storage_send_device_command` | 2 | 2 | 2 | 1 |
| 249 `storage_get_async_status` | 3 | 3 | 1 | 3 |
| 254 `storage_check_async_status` | 0 | 0 | 2 | 0 |
| 255 `panic` | 0 | 0 | 0 | 15 |

**INFERRED:** all softemu LV1 candidates grouped by containing Ghidra function and constant number. Direct-call counts are raw `bl` references to that entry (lower bounds); an unknown boundary has no count. A row can contain several sites. No high-bit guest forwarding was recovered.

| Wrapper | LV1 | Direct calls | Sites |
|---|---|---:|---|
| UNKNOWN boundary | 124 | UNKNOWN | 0x4c65c, 0x4cd14 |
| UNKNOWN boundary | 125 | UNKNOWN | 0x4c38c, 0x4ca84 |
| UNKNOWN boundary | 126 | UNKNOWN | 0x4c0cc |
| UNKNOWN boundary | 136 | UNKNOWN | 0x4c890 |
| UNKNOWN boundary | 194 | UNKNOWN | 0x8d898 |
| 0x0000a854 | 26 | 0 | 0xa8d8 |
| 0x0000acec | 96 | 0 | 0xad88 |
| 0x0000b094 | 96 | 0 | 0xb1f0 |
| 0x0003c024 | 26 | 966 | 0x3c118 |
| 0x0003c024 | 27 | 966 | 0x3c180 |
| 0x0003c024 | 73 | 966 | 0x3c0e8 |
| 0x0003c40c | 91 | 24 | 0x3c45c |
| 0x0003c5bc | 96 | 8 | 0x3c604 |
| 0x0003c62c | 96 | 0 | 0x3c680 |
| 0x0003c734 | 96 | 0 | 0x3c814, 0x3c894 |
| 0x0003cb98 | 96 | 2 | 0x3cbec |
| 0x0003cc24 | 96 | 0 | 0x3cc78 |
| 0x0003cca0 | 96 | 2 | 0x3cd6c, 0x3cde4 |
| 0x0003ce00 | 96 | 1 | 0x3ced8, 0x3cf50 |
| 0x0003cf6c | 96 | 1 | 0x3d03c, 0x3d0b8 |
| 0x0003d0d4 | 96 | 4 | 0x3d1b0, 0x3d22c |
| 0x0003d380 | 174 | 1 | 0x3d3f4 |
| 0x0003d380 | 176 | 1 | 0x3d420 |
| 0x0003d664 | 28 | 1 | 0x3d828, 0x3d8a0 |
| 0x0003d664 | 120 | 1 | 0x3d800, 0x3d878 |
| 0x0003d664 | 170 | 1 | 0x3d750 |
| 0x0003d664 | 172 | 1 | 0x3d944, 0x3d9b8 |
| 0x0003d664 | 174 | 1 | 0x3da30, 0x3da68, 0x3db34 |
| 0x0003d664 | 176 | 1 | 0x3dabc |
| 0x0003db78 | 174 | 1 | 0x3dbf0 |
| 0x0003db78 | 176 | 1 | 0x3dc1c |
| 0x0003e6bc | 27 | 0 | 0x3e754 |
| 0x0003e6bc | 227 | 0 | 0x3e6ec |
| 0x0003e860 | 228 | 0 | 0x3e884 |
| 0x0003ea20 | 225 | 2 | 0x3eb8c |
| 0x0003ecb8 | 221 | 1 | 0x3ed00 |
| 0x0003ed48 | 228 | 0 | 0x3ed74 |
| 0x0003eda4 | 228 | 0 | 0x3edd8 |
| 0x0003ee10 | 228 | 0 | 0x3ee34 |
| 0x0003ee60 | 228 | 0 | 0x3ee94 |
| 0x0003eecc | 225 | 0 | 0x3ef08 |
| 0x0003f224 | 28 | 1 | 0x3f264 |
| 0x0003f224 | 225 | 1 | 0x3f494, 0x3f4e4 |
| 0x0003f224 | 228 | 1 | 0x3f3e4, 0x3f41c, 0x3f440 |
| 0x0003f528 | 15 | 1 | 0x3fdd4, 0x3fe64 |
| 0x0003f528 | 116 | 1 | 0x3fd90 |
| 0x0003f528 | 118 | 1 | 0x3fd54, 0x3fd6c |
| 0x0003f528 | 210 | 1 | 0x3f924 |
| 0x0003f528 | 212 | 1 | 0x3f94c |
| 0x0003f528 | 214 | 1 | 0x3fa90 |
| 0x0003f528 | 217 | 1 | 0x3fab8 |
| 0x0003f528 | 221 | 1 | 0x3fc30 |
| 0x00042b74 | 27 | 0 | 0x42bfc |
| 0x00042c74 | 163 | 41 | 0x42cb0 |
| 0x00042d14 | 162 | 5 | 0x42d34 |
| 0x00042d88 | 164 | 3 | 0x42db0, 0x42df8 |
| 0x00042d88 | 165 | 3 | 0x42dc8 |
| 0x00042e34 | 28 | 1 | 0x42e6c |
| 0x00042e34 | 166 | 1 | 0x42e50 |
| 0x00042ec0 | 9 | 0 | 0x42f48 |
| 0x00042ec0 | 162 | 0 | 0x42f18 |
| 0x00044cfc | 125 | 2 | 0x44de4 |
| 0x00044cfc | 136 | 2 | 0x44d7c |
| 0x00044e28 | 126 | 1 | 0x44fb4 |
| 0x000450e0 | 126 | 1 | 0x45160 |
| 0x00046148 | 140 | 1 | 0x4616c |
| 0x000461a4 | 141 | 1 | 0x461b0 |
| 0x000461c0 | 142 | 1 | 0x461cc |
| 0x000461dc | 143 | 1 | 0x461f8 |
| 0x00046220 | 144 | 2 | 0x4623c |
| 0x00046264 | 145 | 0 | 0x46270 |
| 0x00046280 | 146 | 0 | 0x4628c |
| 0x0004629c | 147 | 0 | 0x462b8 |
| 0x000462e0 | 148 | 0 | 0x462fc |
| 0x00046324 | 149 | 2 | 0x46348 |
| 0x00046378 | 150 | 4 | 0x46394 |
| 0x000463bc | 151 | 2 | 0x463d8 |
| 0x00046400 | 152 | 2 | 0x4641c |
| 0x00046444 | 153 | 2 | 0x46460 |
| 0x00046488 | 154 | 2 | 0x464a4 |
| 0x000464cc | 155 | 2 | 0x464f0 |
| 0x00046520 | 156 | 7 | 0x4652c |
| 0x0004653c | 157 | 0 | 0x46548 |
| 0x00046a7c | 27 | 0 | 0x46b84 |
| 0x00046c68 | 109 | 0 | 0x46c88 |
| 0x00047440 | 24 | 0 | 0x47590 |
| 0x0004766c | 109 | 5 | 0x476b8, 0x4771c |
| 0x00048698 | 27 | 0 | 0x48704 |
| 0x00048698 | 108 | 0 | 0x486c8 |
| 0x00048850 | 107 | 1 | 0x488a0 |
| 0x00048850 | 109 | 1 | 0x488ac |
| 0x000488bc | 18 | 1 | 0x488ec |
| 0x000488bc | 28 | 1 | 0x4893c |
| 0x000488bc | 105 | 1 | 0x48924, 0x489a8 |
| 0x00048bb8 | 95 | 0 | 0x48bfc |
| 0x00048c48 | 0 | 0 | 0x48ca8 |
| 0x00048c48 | 13 | 0 | 0x48d34, 0x48d54 |
| 0x00048f60 | 0 | 1 | 0x48fec |
| 0x00049070 | 95 | 0 | 0x490c0 |
| 0x00049168 | 95 | 0 | 0x491a0 |
| 0x000494a4 | 18 | 0 | 0x49564 |
| 0x000494a4 | 28 | 0 | 0x49588 |
| 0x000494a4 | 73 | 0 | 0x4966c |
| 0x00049814 | 0 | 1 | 0x499b4 |
| 0x00049a18 | 1 | 18 | 0x49eb0 |
| 0x00049a18 | 95 | 18 | 0x49bb4, 0x49c7c, 0x49ec8 |
| 0x00049f7c | 0 | 0 | 0x4ae40 |
| 0x00049f7c | 2 | 0 | 0x4a250 |
| 0x00049f7c | 7 | 0 | 0x4a26c |
| 0x00049f7c | 13 | 0 | 0x4ae9c |
| 0x00049f7c | 69 | 0 | 0x4a00c |
| 0x00049f7c | 73 | 0 | 0x4aaf4 |
| 0x00049f7c | 74 | 0 | 0x49ff8 |
| 0x00049f7c | 97 | 0 | 0x4a20c |
| 0x00049f7c | 98 | 0 | 0x4a220 |
| 0x00049f7c | 110 | 0 | 0x4ad64 |
| 0x00049f7c | 112 | 0 | 0x4a96c |
| 0x0004cdf0 | 27 | 0 | 0x4ce30 |
| 0x0004ce78 | 24 | 2 | 0x4cea4 |
| 0x0004d1a0 | 18 | 2 | 0x4d1f4 |
| 0x0004d1a0 | 28 | 2 | 0x4d218 |
| 0x0004d7e0 | 28 | 0 | 0x4d878 |
| 0x0004d7e0 | 61 | 0 | 0x4d894 |
| 0x0004d7e0 | 78 | 0 | 0x4d858 |
| 0x0004da9c | 199 | 11 | 0x4dc0c, 0x4dc8c |
| 0x0004dc9c | 66 | 13 | 0x4de94, 0x4dec4, 0x4def4 |
| 0x0004dc9c | 199 | 13 | 0x4de24 |
| 0x0004e150 | 57 | 1 | 0x4e1c0 |
| 0x0004e150 | 207 | 1 | 0x4e200 |
| 0x0004eeac | 1 | 1 | 0x4f154, 0x4f1a0 |
| 0x0004eeac | 65 | 1 | 0x4f1c4 |
| 0x0004f214 | 1 | 1 | 0x4f318, 0x4f358 |
| 0x0004f214 | 207 | 1 | 0x4f2e4 |
| 0x0004f494 | 28 | 1 | 0x4f518, 0x4f564, 0x4f5b0 |
| 0x0004f494 | 61 | 1 | 0x4f534, 0x4f580, 0x4f5cc |
| 0x0004f494 | 78 | 1 | 0x4f500, 0x4f54c, 0x4f598 |
| 0x000503e4 | 27 | 0 | 0x504b0 |
| 0x000503e4 | 66 | 0 | 0x5049c |
| 0x000503e4 | 67 | 0 | 0x50440 |
| 0x00050500 | 27 | 0 | 0x505ec |
| 0x00050500 | 66 | 0 | 0x505d8 |
| 0x00050500 | 67 | 0 | 0x50568 |
| 0x00050640 | 54 | 1 | 0x5069c |
| 0x00050640 | 65 | 1 | 0x50688 |
| 0x000506d8 | 27 | 0 | 0x508e0 |
| 0x000506d8 | 66 | 0 | 0x508cc |
| 0x000506d8 | 67 | 0 | 0x50780 |
| 0x000511d0 | 18 | 0 | 0x5120c |
| 0x000511d0 | 28 | 0 | 0x51250 |
| 0x000511d0 | 197 | 0 | 0x51238 |
| 0x000512ec | 27 | 0 | 0x51398 |
| 0x0005174c | 18 | 0 | 0x51a1c |
| 0x0005174c | 28 | 0 | 0x51a5c |
| 0x0005174c | 170 | 0 | 0x51954 |
| 0x0005174c | 172 | 0 | 0x51984, 0x519d0 |
| 0x0005174c | 174 | 0 | 0x51ab4 |
| 0x0005174c | 176 | 0 | 0x51ae4 |
| 0x0005174c | 178 | 0 | 0x51850 |
| 0x0005174c | 179 | 0 | 0x518f8, 0x51924 |
| 0x0005174c | 197 | 0 | 0x51a44 |
| 0x00051b00 | 170 | 0 | 0x51cd8 |
| 0x00051b00 | 172 | 0 | 0x51d08, 0x51d54 |
| 0x00051b00 | 174 | 0 | 0x51dd0 |
| 0x00051b00 | 176 | 0 | 0x51e00 |
| 0x00051b00 | 178 | 0 | 0x51bf8 |
| 0x00051b00 | 179 | 0 | 0x51c80, 0x51cac |
| 0x000528c8 | 91 | 1 | 0x528fc |
| 0x00052994 | 91 | 1 | 0x529c0 |
| 0x00053130 | 91 | 1 | 0x5345c |
| 0x000543c4 | 9 | 0 | 0x54614, 0x54654, 0x546e8 |
| 0x000556cc | 111 | 0 | 0x55718, 0x55754 |
| 0x000557a8 | 111 | 1 | 0x55848, 0x55988 |
| 0x000557a8 | 136 | 1 | 0x55804 |
| 0x00056818 | 111 | 2 | 0x56988, 0x569c4 |
| 0x0005a310 | 111 | 1 | 0x5a358, 0x5a3a0 |
| 0x0005aeb4 | 111 | 0 | 0x5b0cc, 0x5b114 |
| 0x000649cc | 125 | 5 | 0x64bb4 |
| 0x00065d40 | 124 | 4 | 0x65f9c |
| 0x00066b80 | 246 | 0 | 0x66c58, 0x66cb4 |
| 0x00066e24 | 27 | 0 | 0x66e40 |
| 0x00066e24 | 249 | 0 | 0x66e50 |
| 0x00067378 | 246 | 2 | 0x674c8, 0x67524 |
| 0x0006772c | 245 | 1 | 0x67940, 0x6799c, 0x679f4, 0x67a50 |
| 0x00067b10 | 171 | 0 | 0x67d00 |
| 0x00067b10 | 175 | 0 | 0x67cf0 |
| 0x00067b10 | 177 | 0 | 0x67cdc |
| 0x00067b10 | 246 | 0 | 0x67c0c, 0x67c68 |
| 0x00067d8c | 246 | 1 | 0x67f90, 0x67fec |
| 0x000681f4 | 18 | 1 | 0x683a0 |
| 0x000681f4 | 28 | 1 | 0x683e4 |
| 0x000681f4 | 170 | 1 | 0x68390 |
| 0x000681f4 | 174 | 1 | 0x68464 |
| 0x000681f4 | 176 | 1 | 0x68498 |
| 0x000681f4 | 197 | 1 | 0x683cc |
| 0x000839e4 | 27 | 0 | 0x83a10 |
| 0x00083a48 | 27 | 0 | 0x83acc |
| 0x00088724 | 18 | 1 | 0x88894 |
| 0x00088724 | 28 | 1 | 0x888d4 |
| 0x00088724 | 170 | 1 | 0x88814 |
| 0x00088724 | 174 | 1 | 0x88850 |
| 0x00088724 | 176 | 1 | 0x88884 |
| 0x00088724 | 197 | 1 | 0x888bc |
| 0x000889dc | 27 | 0 | 0x88aa8 |
| 0x000889dc | 249 | 0 | 0x88a34 |
| 0x00088b9c | 248 | 1 | 0x88c0c |
| 0x00088c88 | 248 | 10 | 0x88d54 |
| 0x00089f4c | 110 | 0 | 0x89fec |
| 0x0008a480 | 110 | 0 | 0x8a654 |
| 0x0008c15c | 189 | 1 | 0x8c248 |
| 0x0008c260 | 195 | 13 | 0x8c2f0 |
| 0x0008c3b0 | 194 | 1 | 0x8c41c |
| 0x0008c548 | 185 | 2 | 0x8c5f0 |
| 0x0008c548 | 186 | 2 | 0x8c70c |
| 0x0008c548 | 187 | 2 | 0x8c738 |
| 0x0008c548 | 188 | 2 | 0x8c6d0 |
| 0x0008c548 | 189 | 2 | 0x8c674 |
| 0x0008c548 | 190 | 2 | 0x8c6b8 |
| 0x0008c548 | 193 | 2 | 0x8c614, 0x8c6f4 |
| 0x0008c740 | 27 | 0 | 0x8c750 |
| 0x0008c880 | 171 | 0 | 0x8c94c |
| 0x0008c880 | 175 | 0 | 0x8c93c |
| 0x0008c880 | 177 | 0 | 0x8c928 |
| 0x0008c880 | 188 | 0 | 0x8c910 |
| 0x0008c880 | 190 | 0 | 0x8c8f8 |
| 0x0008c880 | 193 | 0 | 0x8c8dc |
| 0x0008c990 | 187 | 1 | 0x8caf8 |
| 0x0008cb9c | 185 | 0 | 0x8d4f0 |
| 0x0008cb9c | 186 | 0 | 0x8d47c |
| 0x0008cb9c | 187 | 0 | 0x8ce3c |
| 0x0008cb9c | 189 | 0 | 0x8cf60, 0x8d534 |
| 0x0008cb9c | 194 | 0 | 0x8cca8, 0x8cd00 |
| 0x0008e004 | 18 | 1 | 0x8e0ac |
| 0x0008e004 | 28 | 1 | 0x8e0e0 |
| 0x0008e004 | 170 | 1 | 0x8e08c |
| 0x0008e004 | 191 | 1 | 0x8e0a4 |
| 0x0008e004 | 193 | 1 | 0x8e4a4, 0x8e534 |
| 0x0008e004 | 194 | 1 | 0x8e37c, 0x8e3ec, 0x8e444 |
| 0x0008e004 | 196 | 1 | 0x8e508 |
| 0x0008e004 | 197 | 1 | 0x8e0d0 |
| 0x0013f3a4 | 170 | 1 | 0x13f418 |
| 0x0013f464 | 171 | 1 | 0x13f4bc |
| 0x0013f464 | 175 | 1 | 0x13f4ac |
| 0x0013f464 | 177 | 1 | 0x13f498 |
| 0x0013f4d8 | 245 | 5 | 0x13f56c |
| 0x0013f4d8 | 249 | 5 | 0x13f590 |
| 0x00141794 | 91 | 0 | 0x1417b4 |
| 0x001417e4 | 91 | 1 | 0x141878, 0x141920, 0x141948, 0x141990, 0x1419f0, 0x141a1c, 0x141a48 |
| 0x001417e4 | 178 | 1 | 0x141a78 |
| 0x001417e4 | 179 | 1 | 0x141abc, 0x141ae8 |
| 0x00141af8 | 91 | 1 | 0x141b1c |
| 0x00141b4c | 91 | 1 | 0x141b70 |
| 0x00141ba0 | 91 | 0 | 0x141bc0 |
| 0x00141bf0 | 91 | 0 | 0x141c20 |
| 0x00141c60 | 91 | 0 | 0x141cb4, 0x141cf4 |
| 0x00141d5c | 91 | 0 | 0x141d7c |
| 0x0022394c | 225 | 1 | 0x223a30 |
| 0x00236ee8 | 9 | 1 | 0x237360 |
| 0x002380f4 | 225 | 2 | 0x238220 |
| 0x0023825c | 225 | 1 | 0x2383b4, 0x238490 |
