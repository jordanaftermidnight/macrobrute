/*
 * LPC2361 Linker Script
 * 128KB Flash, 34KB SRAM
 *
 * CRP word must be at 0x000001FC — handled in startup.s
 */

MEMORY
{
    /* Flash: 128KB (0x20000 bytes) */
    /* Vector table + CRP occupy first 0x200 bytes */
    flash (rx)  : ORIGIN = 0x00000000, LENGTH = 128K

    /* SRAM: 34KB (0x8800 bytes) */
    /* USB DMA uses top 8KB (0x7FE00000-0x7FE01FFF) — not relevant here */
    sram (rwx)  : ORIGIN = 0x40000000, LENGTH = 34K
}

/* Stack at top of SRAM */
_stack_top = ORIGIN(sram) + LENGTH(sram);

SECTIONS
{
    /* Vector table and startup code */
    .isr_vector :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))
        . = ALIGN(4);
    } > flash

    /* CRP word MUST be at 0x1FC */
    .crp 0x000001FC :
    {
        KEEP(*(.crp))
    } > flash

    /* Code */
    .text :
    {
        . = ALIGN(4);
        *(.text)
        *(.text*)
        *(.rodata)
        *(.rodata*)
        *(.glue_7)
        *(.glue_7t)
        . = ALIGN(4);
        _etext = .;
    } > flash

    /* Initialized data — stored in flash, copied to SRAM at startup */
    .data : AT (_etext)
    {
        . = ALIGN(4);
        _data = .;
        *(.data)
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } > sram

    /* BSS — zeroed at startup */
    .bss :
    {
        . = ALIGN(4);
        _bss = .;
        *(.bss)
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > sram

    /* Heap — grows up from end of BSS */
    .heap :
    {
        . = ALIGN(4);
        _end = .;
        PROVIDE(end = .);
        . = . + 0x1000;  /* 4KB minimum heap */
        _heap_end = .;
    } > sram

    /* Stack — grows down from top of SRAM */
    .stack :
    {
        . = ALIGN(8);
        . = . + 0x800;  /* 2KB stack */
        _stack = .;
    } > sram
}
