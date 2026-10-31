OUTPUT_FORMAT(elf64-powerpc)
ENTRY(s4_menu)
SECTIONS {
  . = 0x4A00;
  .text : { *(.text) *(.text.*) }
  .rodata : { *(.rodata*) }
  . = ALIGN(8);
  .toc : { *(.toc*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
labels_page_a = 0x74e930;
labels_page_b = 0x750b70;
labels_page_c = 0x758ff0;
labels_page_d = 0x759270;
repo_read = 0x48c0;
native_clock = 0x4900;
alloc_buffer = 0x4910;
lv1_hcall = 0x4800;
