OUTPUT_FORMAT(elf64-powerpc)
ENTRY(s4_menu)
SECTIONS {
  . = 0x4900;
  .text : { *(.text) *(.text.*) }
  .rodata : { *(.rodata*) }
  . = ALIGN(8);
  .toc : { *(.toc*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
labels_page_a = 0x74e930;
labels_page_b = 0x74f740;
labels_page_c = 0x7a3770;
labels_page_d = 0x7ae060;
repo_read = 0x4840;
lv1_open_device = 0x4820;
lv1_close_device = 0x4830;
