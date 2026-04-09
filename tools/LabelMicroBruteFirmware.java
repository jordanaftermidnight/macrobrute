// Label LPC2361 MicroBrute firmware addresses
// @category MACROBRUTE
// @menupath Tools.MACROBRUTE.Label Firmware

import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;

public class LabelMicroBruteFirmware extends GhidraScript {

    private void lbl(long offset, String name, String comment) throws Exception {
        Address a = toAddr(offset);
        try {
            createLabel(a, name, true, SourceType.USER_DEFINED);
        } catch (Exception e) {
            try { createLabel(a, name, true); } catch (Exception e2) {}
        }
        if (comment != null) {
            setPlateComment(toAddr(offset), comment);
        }
    }

    private void lbl(long offset, String name) throws Exception {
        lbl(offset, name, null);
    }

    @Override
    public void run() throws Exception {
        println("=== MACROBRUTE LPC2361 Firmware Labeler ===");

        // Vector Table
        lbl(0x2000, "VEC_Reset",     "LDR PC - Reset vector");
        lbl(0x2004, "VEC_Undef",     "LDR PC - Undefined instruction");
        lbl(0x2008, "VEC_SWI",       "LDR PC - Software interrupt");
        lbl(0x200C, "VEC_PrefAbort", "LDR PC - Prefetch abort");
        lbl(0x2010, "VEC_DataAbort", "LDR PC - Data abort");
        lbl(0x2014, "VEC_Checksum",  "NXP checksum (0x0000CD80)");
        lbl(0x2018, "VEC_IRQ",       "LDR PC,[PC,-#0x120] reads VICVectAddr");
        lbl(0x201C, "VEC_FIQ",       "LDR PC - FIQ vector");
        println("  Labeled 8 vectors");

        // Handler pointers
        lbl(0x2020, "PTR_ResetHandler",     "-> 0x2054");
        lbl(0x2024, "PTR_UndefHandler",     "-> 0x2040");
        lbl(0x2028, "PTR_SWIHandler",       "-> 0x23DC");
        lbl(0x202C, "PTR_PrefAbortHandler", "-> 0x2044");
        lbl(0x2030, "PTR_DataAbortHandler", "-> 0x2048");
        lbl(0x2034, "PTR_Reserved5",        "Unused");
        lbl(0x2038, "PTR_IRQHandler",       "-> 0x204C (VIC dispatch)");
        lbl(0x203C, "PTR_FIQHandler",       "-> 0x2050");
        println("  Labeled 8 handler pointers");

        // Handler code
        lbl(0x2040, "DefaultHandler_Undef", "Default: infinite loop");
        lbl(0x2044, "DefaultHandler_PrefAbort");
        lbl(0x2048, "DefaultHandler_DataAbort");
        lbl(0x204C, "IRQHandler_VIC", "VIC vectored IRQ dispatch");
        lbl(0x2050, "DefaultHandler_FIQ");
        lbl(0x2054, "ResetHandler", "Entry: system init + main()");
        lbl(0x2184, "EntryPoint", "Start Linear Address from Intel HEX");

        // Known code locations
        lbl(0x2170, "SystemInit_MAM",    "MAM + system control init");
        lbl(0x23DC, "SWI_Handler",       "Software interrupt handler");
        lbl(0x2C44, "PinMux_Init_1",    "PINSEL setup");
        lbl(0x2C64, "VIC_Init_1",       "VIC setup");
        lbl(0x3250, "VIC_Init_2",       "VIC handler installation");
        lbl(0x3EA8, "UART0_Init",       "UART0 init - ISP/debug/Pico bridge");
        lbl(0x3EB4, "PinMux_UART",      "PINSEL for UART pins");
        lbl(0x3F70, "Timer0_Init",      "Timer0 handler setup (1ms tick)");
        lbl(0x3F7C, "Timer0_VIC",       "Timer0 VIC channel install");
        lbl(0x4340, "SPI_VIC",          "SPI/SSP VIC setup");
        lbl(0x4348, "SPI_Init",         "SPI init");
        lbl(0x4350, "PinMux_SPI",       "PINSEL for SPI pins");
        lbl(0x4672, "SysEx_Parser_1",   "SysEx start byte check (0xF0) - Arturia protocol");
        lbl(0x471E, "MIDI_Dispatcher",  "MIDI status byte dispatcher (CC/NoteOn/Off/PB)");
        lbl(0x4C52, "SysEx_Parser_2",   "MIDI Identity Request handler (F0 7E 7F 06 01 F7)");
        lbl(0x6114, "VIC_Init_3",       "VIC setup (late init)");
        lbl(0x669C, "GPIO_Handler",     "Fast GPIO control");
        lbl(0x6750, "Timer0_Ref",       "Timer0/timing reference");
        lbl(0x6B74, "GPIO_Handler_2",   "Fast GPIO (additional)");
        lbl(0x6B78, "SPI_Handler_2",    "SPI communication (additional)");
        lbl(0x6CAC, "PinMux_Init_2",   "PINSEL setup (additional)");
        lbl(0x6D54, "ParamAccessor",    "Most-called function (38 callers) - param read/write?");
        lbl(0x752C, "PinMux_Init_3",   "PINSEL setup (additional)");
        lbl(0x7E10, "ADC_Read",         "ADC read (25 callers)");
        lbl(0x9C5C, "Timer1_Ref",       "Timer1 microsecond reference");
        lbl(0xA39C, "SystemControl_Ref","System control block reference");
        println("  Labeled 26 code locations");

        // C++ runtime
        lbl(0xC7E4, "SIGPVFN",        "Pure virtual fn called - C++ abort");
        lbl(0xCA2C, "SIGRTMEM",       "Out of heap memory");
        lbl(0xCA4C, "STR_HeapCorrupt", "Heap memory corrupted");
        lbl(0xCA78, "SIGABRT",        "Abnormal termination");

        // Create peripheral memory blocks
        Memory mem = currentProgram.getMemory();
        String[][] regions = {
            {"FAST_GPIO",   "3fffc000", "100"},
            {"TIMER0",      "e0004000", "80"},
            {"TIMER1",      "e0008000", "80"},
            {"UART0",       "e000c000", "40"},
            {"UART1",       "e0010000", "40"},
            {"I2C0",        "e001c000", "20"},
            {"PIN_CONNECT", "e002c000", "80"},
            {"ADC",         "e0034000", "40"},
            {"DAC",         "e006c000", "10"},
            {"SSP0",        "e0068000", "20"},
            {"SYS_CTRL",    "e01fc000", "200"},
            {"VIC",         "fffff000", "400"},
            {"SRAM",        "40000000", "8800"},
        };

        int blocks = 0;
        for (String[] r : regions) {
            Address a = toAddr(Long.parseUnsignedLong(r[1], 16));
            int size = Integer.parseInt(r[2], 16);
            if (mem.getBlock(a) == null) {
                try {
                    mem.createUninitializedBlock(r[0], a, size, false);
                    blocks++;
                } catch (Exception e) {
                    println("  WARN: " + r[0] + ": " + e.getMessage());
                }
            }
        }
        println("  Created " + blocks + " memory blocks");

        // Label peripheral registers
        long[][] periph = {
            {0xE0004000L}, {0xE0004004L}, {0xE0004008L}, {0xE000400CL},
            {0xE0004014L}, {0xE0004018L},
            {0xE0008000L}, {0xE0008004L}, {0xE0008008L},
            {0xE000C000L}, {0xE000C004L}, {0xE000C008L}, {0xE000C00CL}, {0xE000C014L},
            {0xE0010000L}, {0xE001000CL}, {0xE0010014L},
            {0xE001C000L}, {0xE001C008L}, {0xE001C018L},
            {0xE0034000L}, {0xE0034004L},
            {0xE006C000L},
            {0xE0068000L}, {0xE0068008L}, {0xE006800CL},
            {0xE01FC000L}, {0xE01FC004L}, {0xE01FC080L}, {0xE01FC084L},
            {0xE01FC088L}, {0xE01FC08CL}, {0xE01FC0C4L}, {0xE01FC1A0L}, {0xE01FC1A8L},
            {0xE002C000L}, {0xE002C004L}, {0xE002C008L},
            {0x3FFFC000L}, {0x3FFFC014L}, {0x3FFFC018L}, {0x3FFFC01CL},
            {0x3FFFC040L}, {0x3FFFC054L},
            {0xFFFFF000L}, {0xFFFFF010L}, {0xFFFFF014L}, {0xFFFFF030L},
            {0xFFFFF100L}, {0xFFFFF110L}, {0xFFFFF118L}, {0xFFFFF11CL},
        };
        String[] pnames = {
            "T0IR", "T0TCR", "T0TC", "T0PR", "T0MCR", "T0MR0",
            "T1IR", "T1TCR", "T1TC",
            "U0RBR", "U0IER", "U0IIR", "U0LCR", "U0LSR",
            "U1RBR", "U1LCR", "U1LSR",
            "I2C0CONSET", "I2C0DAT", "I2C0CONCLR",
            "AD0CR", "AD0GDR",
            "DACR",
            "SSP0CR0", "SSP0DR", "SSP0SR",
            "MAMCR", "MAMTIM", "PLL0CON", "PLL0CFG",
            "PLL0STAT", "PLL0FEED", "PCONP", "SCS", "PCLKSEL0",
            "PINSEL0", "PINSEL1", "PINSEL2",
            "FIO0DIR", "FIO0PIN", "FIO0SET", "FIO0CLR",
            "FIO2DIR", "FIO2PIN",
            "VICIRQStatus", "VICIntEnable", "VICIntEnClr", "VICVectAddr",
            "VICVectAddr0", "VICVectAddr4", "VICVectAddr6", "VICVectAddr7",
        };

        int plbl = 0;
        for (int i = 0; i < periph.length && i < pnames.length; i++) {
            try {
                lbl(periph[i][0], pnames[i]);
                plbl++;
            } catch (Exception e) {}
        }
        println("  Labeled " + plbl + " peripheral registers");

        println("");
        println("=== Labeling Complete ===");
        println("Go to: 0x2054 (ResetHandler), 0x3EA8 (UART0_Init), 0x4672 (SysEx)");
    }
}
