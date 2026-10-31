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
labels_page_00 = 0x74e930;
labels_page_01 = 0x74fd30;
labels_page_02 = 0x751e10;
labels_page_03 = 0x753ef0;
labels_page_04 = 0x755fd0;
labels_page_05 = 0x7580b0;
labels_page_06 = 0x75a190;
labels_page_07 = 0x75c270;
labels_page_08 = 0x75e3f0;
labels_page_09 = 0x760570;
labels_page_10 = 0x762650;
labels_page_11 = 0x764730;
labels_page_12 = 0x766810;
labels_page_13 = 0x7688f0;
labels_page_14 = 0x76a9d0;
labels_page_15 = 0x76cab0;
labels_page_16 = 0x76eb90;
labels_page_17 = 0x770c70;
labels_page_18 = 0x772d50;
labels_page_19 = 0x774e30;
labels_page_20 = 0x776f10;
labels_page_21 = 0x778ff0;
labels_page_22 = 0x77b0d0;
labels_page_23 = 0x77d1b0;
repo_read = 0x4800;
native_alloc = 0x4840;
native_clock = 0x48c0;
