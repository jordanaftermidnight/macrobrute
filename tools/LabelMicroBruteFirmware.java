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
        lbl(0x4C28, "SysEx_CmdHandler", "Arturia SysEx command handler (43 commands, F0 00 20 6B 05 01)");
        lbl(0x4C52, "SysEx_Parser_2",   "MIDI Identity Request handler (F0 7E 7F 06 01 F7)");
        lbl(0x5BF0, "StateRefresh",     "State refresh (recalc after param change)");
        lbl(0x5EC8, "StateRefresh_Wrap","State refresh wrapper (30 callers)");
        lbl(0x6114, "VIC_Init_3",       "VIC setup (late init)");
        lbl(0x669C, "GPIO_Handler",     "Fast GPIO control");
        lbl(0x6750, "Timer0_Ref",       "Timer0/timing reference");
        lbl(0x6B74, "GPIO_Handler_2",   "Fast GPIO (additional)");
        lbl(0x6B78, "SPI_Handler_2",    "SPI communication (additional)");
        lbl(0x6CAC, "PinMux_Init_2",   "PINSEL setup (additional)");
        lbl(0x6D30, "InterpTable_Ctor", "Interpolation table constructor (obj + segment count)");
        lbl(0x6D54, "InterpTable_Build","Piecewise linear interpolation builder (38 callers)");
        lbl(0x6D78, "InterpTable_Lookup","Interpolating table lookup (14-bit input)");
        lbl(0x6E0E, "I2C_Recalc",      "I2C DAC recalculate after calibration change");
        lbl(0x6E4A, "I2C_WaitReady",   "I2C wait/ready check (channel + 0x96)");
        lbl(0x6F04, "I2C_DAC_Write",   "I2C write to MCP4728 (wait + transmit)");
        lbl(0x703E, "PitchCV_Calibrate","Pitch CV: 14-bit MIDI -> DAC (table + offset -400)");
        lbl(0x71A0, "DAC_ChanSelect",  "DAC channel select + write");
        lbl(0x71AE, "DAC_WriteCalib",  "DAC write with calibration");
        lbl(0x71C8, "DAC_WriteBuf",    "DAC write (buffered)");
        lbl(0x71E2, "DAC_GetChannel",  "DAC channel accessor");
        lbl(0x752C, "PinMux_Init_3",   "PINSEL setup (additional)");
        lbl(0x7BE2, "NoteOff_Handler", "Note Off handler");
        lbl(0x7C54, "NoteOn_Handler",  "Note On handler (with velocity)");
        lbl(0x7CC2, "NoteRetrigger",   "Note re-trigger after param change");
        lbl(0x7E10, "ADC_Read",         "ADC read (25 callers)");
        lbl(0x980A, "Seq_Enable",       "Sequencer enable/disable (param: 1=on, 0=off)");
        lbl(0x9C5C, "Timer1_Ref",       "Timer1 microsecond reference");
        lbl(0xA39C, "SystemControl_Ref","System control block reference");
        lbl(0xA56A, "KeyMode_Set",      "Key mode select (0=reset, 1=single, 2=hold, 3=multi)");
        lbl(0xA57E, "KeyMode_Reset",    "Key mode pre-reset");
        lbl(0xB8AE, "SeqStep_Update",   "Sequence step update after write");
        lbl(0xC222, "MCP4728_AddrInit", "MCP4728 I2C addr setup (0xC0 = 0x60<<1)");
        lbl(0xD04C, "SysEx_Finalize",  "SysEx message finalize");
        lbl(0xD052, "SysEx_GetData",   "SysEx get message data pointer");
        lbl(0xD05A, "SysEx_GetLen",    "SysEx get message length");
        lbl(0xD0D4, "Param_Commit",    "Parameter commit (post-write)");
        lbl(0xD17C, "SysEx_Build",     "SysEx message builder");
        lbl(0xD1C4, "Param_StepSize",  "Parameter accessor: step size / next seq");
        lbl(0xD1D0, "Param_Swing",     "Parameter accessor: swing");
        lbl(0xD1DA, "Param_Tempo",     "Parameter accessor: tempo/rate");
        lbl(0xD1E4, "Param_MIDIRecv",  "Parameter accessor: MIDI receive channel");
        lbl(0xD1EE, "Param_SeqEdit",   "Parameter accessor: seq/arp edit");
        lbl(0xD1F8, "Param_BendRange", "Parameter accessor: bend range");
        lbl(0xD208, "Param_SeqStep",   "Parameter accessor: sequence step select");
        lbl(0xD218, "Param_LFORetrig", "Parameter accessor: LFO key retrig");
        lbl(0xD222, "Param_MIDIChan",  "Parameter accessor: MIDI channel");
        lbl(0xD830, "SysEx_Transmit",  "SysEx message transmit");
        lbl(0xD860, "Heap_Alloc",      "Heap allocator (malloc)");
        lbl(0xD894, "I2C_DataXfer",    "I2C data transmission (low-level)");
        lbl(0xDBF0, "Delay_ms",        "Delay in milliseconds");
        lbl(0xE7D2, "SeqStep_GetData", "Sequence step get data");
        lbl(0xE80C, "SeqStep_SetData", "Sequence step set data");
        lbl(0xE85E, "Param_Read8",     "Parameter read (8-bit, Group B)");
        lbl(0xE866, "Param_WriteBend", "Parameter write: bend range (NRPN path)");
        lbl(0xE884, "Param_Write8B",   "Parameter write (8-bit, Group B)");
        lbl(0xE8AE, "Param_Read8A",    "Parameter read (8-bit, Group A)");
        lbl(0xE8D0, "Param_Write8A",   "Parameter write (8-bit, Group A)");
        println("  Labeled 72 code locations");

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
