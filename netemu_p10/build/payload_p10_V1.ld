
    OUTPUT_FORMAT("elf64-powerpc")
    OUTPUT_ARCH(powerpc:common64)
    SECTIONS {
        . = 0x4B00;
        .text : {
            *(.text .text.*)
        }
        .rodata : {
            *(.rodata .rodata.*)
        }
        .data : {
            *(.data .data.*)
        }
        .opd : {
            *(.opd)
        }
        .toc : {
            *(.toc .toc.*)
        }
        .bss : {
            *(.bss .bss.*)
        }
    }
    repo_read = 0x48c0;
    native_clock = 0x4900;
    native_alloc = 0x4920;
    stock_ufs_open = 0x4960;
    stock_ufs_close = 0x49a0;
    stock_raw_read = 0x49e0;
    stock_raw_write = 0x4a20;
    stock_hdd_cache_flush = 0x4a60;
    get_r2 = 0x4aa0;
    lv1_hcall = 0x4800;
    