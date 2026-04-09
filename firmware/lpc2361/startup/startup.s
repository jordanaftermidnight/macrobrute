/*
 * LPC2361 Startup Code
 * ARM7TDMI-S Vector Table and Reset Handler
 *
 * Vector table at 0x00000000
 * CRP word at 0x000001FC
 */

    .syntax unified
    .cpu arm7tdmi
    .arm

    .section .isr_vector, "ax"
    .global _vectors

_vectors:
    ldr     pc, =reset_handler      /* 0x00: Reset */
    ldr     pc, =undef_handler      /* 0x04: Undefined instruction */
    ldr     pc, =swi_handler        /* 0x08: Software interrupt */
    ldr     pc, =pabt_handler       /* 0x0C: Prefetch abort */
    ldr     pc, =dabt_handler       /* 0x10: Data abort */
    .word   0                       /* 0x14: Reserved (checksum) */
    ldr     pc, [pc, #-0x0FF0]      /* 0x18: IRQ — load from VIC */
    ldr     pc, =fiq_handler        /* 0x1C: FIQ */

    /* CRP word — MUST be at 0x1FC */
    .section .crp, "a"
    .word   0xFFFFFFFF              /* CRP_NONE — no read protection */

    .section .text
    .global reset_handler

reset_handler:
    /* Setup stacks for each mode */

    /* IRQ mode stack */
    msr     cpsr_c, #0xD2           /* IRQ mode, IRQ+FIQ disabled */
    ldr     sp, =_stack_top
    sub     sp, sp, #0x100          /* 256 bytes IRQ stack */

    /* FIQ mode stack */
    msr     cpsr_c, #0xD1           /* FIQ mode */
    ldr     sp, =_stack_top
    sub     sp, sp, #0x100
    sub     sp, sp, #0x40           /* 64 bytes FIQ stack */

    /* Abort mode stack */
    msr     cpsr_c, #0xD7           /* Abort mode */
    ldr     sp, =_stack_top
    sub     sp, sp, #0x140
    sub     sp, sp, #0x40           /* 64 bytes abort stack */

    /* Undefined mode stack */
    msr     cpsr_c, #0xDB           /* Undefined mode */
    ldr     sp, =_stack_top
    sub     sp, sp, #0x180
    sub     sp, sp, #0x40           /* 64 bytes undef stack */

    /* Supervisor mode (SVC) stack — main execution */
    msr     cpsr_c, #0xD3           /* SVC mode, IRQ+FIQ disabled */
    ldr     sp, =_stack_top
    sub     sp, sp, #0x200          /* Rest of stack for SVC mode */

    /* Copy initialized data from flash to SRAM */
    ldr     r0, =_etext             /* Source: end of text in flash */
    ldr     r1, =_data              /* Dest: start of .data in SRAM */
    ldr     r2, =_edata             /* End: end of .data in SRAM */
copy_data:
    cmp     r1, r2
    ldrlo   r3, [r0], #4
    strlo   r3, [r1], #4
    blo     copy_data

    /* Zero BSS */
    ldr     r0, =_bss               /* Start of .bss */
    ldr     r1, =_ebss              /* End of .bss */
    mov     r2, #0
zero_bss:
    cmp     r0, r1
    strlo   r2, [r0], #4
    blo     zero_bss

    /* Enable Fast GPIO on ports 0 and 1 */
    ldr     r0, =0xE01FC1A0         /* SCS register */
    ldr     r1, [r0]
    orr     r1, r1, #1              /* GPIOM = 1 */
    str     r1, [r0]

    /* Switch to System mode, enable IRQ */
    msr     cpsr_c, #0x1F           /* System mode, IRQ+FIQ enabled */

    /* Jump to C main */
    bl      main

    /* If main returns, loop forever */
hang:
    b       hang

/* Default exception handlers (infinite loops) */
undef_handler:
    b       undef_handler

swi_handler:
    b       swi_handler

pabt_handler:
    b       pabt_handler

dabt_handler:
    b       dabt_handler

fiq_handler:
    b       fiq_handler
