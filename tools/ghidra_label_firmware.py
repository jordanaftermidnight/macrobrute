# Label LPC2361 MicroBrute firmware addresses.
# @category MACROBRUTE
# @menupath Tools.MACROBRUTE.Label Firmware

from ghidra.program.model.symbol import SourceType

def addr(offset):
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset)

def lbl(offset, name, comment=None):
    a = addr(offset)
    try:
        createLabel(a, name, True, SourceType.USER_DEFINED)
        if comment:
            setPlateComment(a, comment)
    except:
        try:
            createLabel(a, name, True)
            if comment:
                setPlateComment(a, comment)
        except:
            println("  WARN: Could not label 0x%08X as %s" % (offset, name))

# Vector Table (0x2000 - 0x201F)
println("=== MACROBRUTE LPC2361 Firmware Labeler ===")

vectors = [
    (0x2000, "VEC_Reset",     "LDR PC - Reset vector"),
    (0x2004, "VEC_Undef",     "LDR PC - Undefined instruction"),
    (0x2008, "VEC_SWI",       "LDR PC - Software interrupt"),
    (0x200C, "VEC_PrefAbort", "LDR PC - Prefetch abort"),
    (0x2010, "VEC_DataAbort", "LDR PC - Data abort"),
    (0x2014, "VEC_Checksum",  "NXP checksum (0x0000CD80)"),
    (0x2018, "VEC_IRQ",       "LDR PC,[PC,-#0x120] reads VICVectAddr"),
    (0x201C, "VEC_FIQ",       "LDR PC - FIQ vector"),
]
for offset, name, comment in vectors:
    lbl(offset, name, comment)
println("  Labeled 8 vectors")

# Handler address table (0x2020 - 0x203F)
handlers = [
    (0x2020, "PTR_ResetHandler",     "-> 0x2054"),
    (0x2024, "PTR_UndefHandler",     "-> 0x2040 (default handler)"),
    (0x2028, "PTR_SWIHandler",       "-> 0x23DC"),
    (0x202C, "PTR_PrefAbortHandler", "-> 0x2044 (default handler)"),
    (0x2030, "PTR_DataAbortHandler", "-> 0x2048 (default handler)"),
    (0x2034, "PTR_Reserved5",        "Unused (checksum slot pointer)"),
    (0x2038, "PTR_IRQHandler",       "-> 0x204C (VIC dispatch)"),
    (0x203C, "PTR_FIQHandler",       "-> 0x2050 (default handler)"),
]
for offset, name, comment in handlers:
    lbl(offset, name, comment)
println("  Labeled 8 handler pointers")

# Actual handler code
lbl(0x2040, "DefaultHandler_Undef", "Default: infinite loop (B .)")
lbl(0x2044, "DefaultHandler_PrefAbort")
lbl(0x2048, "DefaultHandler_DataAbort")
lbl(0x204C, "IRQHandler_VIC", "VIC vectored IRQ dispatch")
lbl(0x2050, "DefaultHandler_FIQ")
lbl(0x2054, "ResetHandler", "Entry: system init + main()")
lbl(0x2184, "EntryPoint", "Start Linear Address from Intel HEX")

# Known Code Locations (from binary analysis)
code_locs = [
    (0x2170, "SystemInit_MAM", "MAM + system control init"),
    (0x23DC, "SWI_Handler", "Software interrupt handler"),
    (0x2C44, "PinMux_Init_1", "PINSEL setup"),
    (0x2C64, "VIC_Init_1", "VIC setup"),
    (0x3250, "VIC_Init_2", "VIC handler installation"),
    (0x3EA8, "UART0_Init", "UART0 init - ISP/debug/Pico bridge"),
    (0x3EB4, "PinMux_UART", "PINSEL for UART pins"),
    (0x3F70, "Timer0_Init", "Timer0 handler setup (1ms tick)"),
    (0x3F7C, "Timer0_VIC", "Timer0 VIC channel install"),
    (0x4340, "SPI_VIC", "SPI/SSP VIC setup"),
    (0x4348, "SPI_Init", "SPI init"),
    (0x4350, "PinMux_SPI", "PINSEL for SPI pins"),
    (0x4672, "SysEx_Parser_1", "SysEx start byte check (0xF0)"),
    (0x471E, "MIDI_Dispatcher", "MIDI status byte dispatcher (CC/NoteOn/Off/PB)"),
    (0x4C52, "SysEx_Parser_2", "MIDI Identity Request handler"),
    (0x6114, "VIC_Init_3", "VIC setup (late init)"),
    (0x669C, "GPIO_Handler", "Fast GPIO control"),
    (0x6750, "Timer0_Ref", "Timer0/timing reference"),
    (0x6B74, "GPIO_Handler_2", "Fast GPIO (additional)"),
    (0x6B78, "SPI_Handler_2", "SPI communication (additional)"),
    (0x6CAC, "PinMux_Init_2", "PINSEL setup (additional)"),
    (0x6D54, "ParamAccessor", "Most-called function (38 callers) - param read/write?"),
    (0x752C, "PinMux_Init_3", "PINSEL setup (additional)"),
    (0x7E10, "ADC_Read", "ADC read (25 callers, near ADC ref)"),
    (0x9C5C, "Timer1_Ref", "Timer1 microsecond reference"),
    (0xA39C, "SystemControl_Ref", "System control block reference"),
]
for offset, name, comment in code_locs:
    lbl(offset, name, comment)
println("  Labeled %d code locations" % len(code_locs))

# C++ runtime error handlers
lbl(0xC7E4, "SIGPVFN", "Pure virtual fn called - C++ abort")
lbl(0xCA2C, "SIGRTMEM", "Out of heap memory - heap exhausted")
lbl(0xCA4C, "STR_HeapCorrupt", "Heap memory corrupted")
lbl(0xCA78, "SIGABRT", "Abnormal termination")

# Create memory blocks for peripheral regions
mem = currentProgram.getMemory()
periph_regions = [
    ("FAST_GPIO",   0x3FFFC000, 0x100),
    ("TIMER0",      0xE0004000, 0x80),
    ("TIMER1",      0xE0008000, 0x80),
    ("UART0",       0xE000C000, 0x40),
    ("UART1",       0xE0010000, 0x40),
    ("I2C0",        0xE001C000, 0x20),
    ("PIN_CONNECT", 0xE002C000, 0x80),
    ("ADC",         0xE0034000, 0x40),
    ("DAC",         0xE006C000, 0x10),
    ("SSP0",        0xE0068000, 0x20),
    ("SYS_CTRL",    0xE01FC000, 0x200),
    ("VIC",         0xFFFFF000, 0x400),
    ("SRAM",        0x40000000, 0x8800),
]

blocks_created = 0
for name, base, size in periph_regions:
    a = addr(base)
    if mem.getBlock(a) is None:
        try:
            mem.createUninitializedBlock(name, a, size, False)
            blocks_created += 1
        except:
            println("  WARN: Could not create block %s at 0x%08X" % (name, base))
println("  Created %d memory blocks" % blocks_created)

# Label peripheral registers
peripherals = [
    (0xE0004000, "T0IR"),    (0xE0004004, "T0TCR"),   (0xE0004008, "T0TC"),
    (0xE000400C, "T0PR"),    (0xE0004014, "T0MCR"),   (0xE0004018, "T0MR0"),
    (0xE0008000, "T1IR"),    (0xE0008004, "T1TCR"),   (0xE0008008, "T1TC"),
    (0xE000C000, "U0RBR"),   (0xE000C004, "U0IER"),   (0xE000C008, "U0IIR"),
    (0xE000C00C, "U0LCR"),   (0xE000C014, "U0LSR"),
    (0xE0010000, "U1RBR"),   (0xE001000C, "U1LCR"),   (0xE0010014, "U1LSR"),
    (0xE001C000, "I2C0CONSET"), (0xE001C008, "I2C0DAT"), (0xE001C018, "I2C0CONCLR"),
    (0xE0034000, "AD0CR"),   (0xE0034004, "AD0GDR"),
    (0xE006C000, "DACR"),
    (0xE0068000, "SSP0CR0"), (0xE0068008, "SSP0DR"),  (0xE006800C, "SSP0SR"),
    (0xE01FC000, "MAMCR"),   (0xE01FC004, "MAMTIM"),  (0xE01FC080, "PLL0CON"),
    (0xE01FC084, "PLL0CFG"), (0xE01FC088, "PLL0STAT"),(0xE01FC08C, "PLL0FEED"),
    (0xE01FC0C4, "PCONP"),   (0xE01FC1A0, "SCS"),     (0xE01FC1A8, "PCLKSEL0"),
    (0xE002C000, "PINSEL0"), (0xE002C004, "PINSEL1"), (0xE002C008, "PINSEL2"),
    (0x3FFFC000, "FIO0DIR"), (0x3FFFC014, "FIO0PIN"), (0x3FFFC018, "FIO0SET"),
    (0x3FFFC01C, "FIO0CLR"), (0x3FFFC040, "FIO2DIR"), (0x3FFFC054, "FIO2PIN"),
    (0xFFFFF000, "VICIRQStatus"), (0xFFFFF010, "VICIntEnable"),
    (0xFFFFF014, "VICIntEnClr"),  (0xFFFFF030, "VICVectAddr"),
    (0xFFFFF100, "VICVectAddr0"), (0xFFFFF110, "VICVectAddr4"),
    (0xFFFFF118, "VICVectAddr6"), (0xFFFFF11C, "VICVectAddr7"),
]

plabeled = 0
for offset, name in peripherals:
    try:
        lbl(offset, name)
        plabeled += 1
    except:
        pass
println("  Labeled %d peripheral registers" % plabeled)

println("")
println("=== Labeling Complete ===")
println("Next: Go to 0x2054 (ResetHandler), 0x3EA8 (UART0_Init), 0x4672 (SysEx)")
