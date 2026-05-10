# MACROBRUTE Firmware Project Structure

The firmware lives in two trees, one per processor. Both compile and flash
independently — the Pico runs UI/clock and the LPC2361 runs the synth engine.
They communicate over UART0 at 115 200 baud through a small framed protocol
(see `firmware/lpc2361/src/ui/pico_comm.{c,h}` and `firmware/pico/main.py`).

## firmware/pico/ — Raspberry Pi Pico WH (MicroPython)

```
firmware/pico/
├── main.py             # Entry point: init, run loop, message dispatch
├── config.py           # GPIO pin map (mirrors schematics/pico_pinout.md)
├── display.py          # SSD1306 0x3C main OLED driver
├── strip_display.py    # SSD1306 0x3D strip OLED driver
├── encoder.py          # KY-040 rotary encoder + button debounce
├── leds.py             # RGB status LED PWM
├── menu.py             # On-device UI state machine
├── clock.py            # Tap-tempo + external clock-in capture
├── clock_divider.py    # /2 /4 /8 derived clock outputs
├── midi.py             # 5-pin DIN MIDI (LPC bridge side)
├── usbmidi.py          # USB-MIDI class device (TinyUSB)
├── aux_outputs.py      # PWM CV / gate outputs to expander
├── effigy_bridge.py    # Inter-module ii bridge to EFFIGY/Norns
├── _effigy_constants.py
└── test_hw.py          # Per-peripheral self-test harness
```

Flash by mounting the Pico's `RPI-RP2` storage and copying the `.py` files
into the MicroPython filesystem; `main.py` runs at boot.

## firmware/lpc2361/ — LPC2361 ARM7TDMI (bare-metal C)

```
firmware/lpc2361/
├── Makefile              # arm-none-eabi build, ISP flash target
├── linker/lpc2361.ld     # 128 KB Flash / 34 KB RAM memory map
├── startup/              # Reset handler, vector table, newlib syscalls
├── include/lpc2361.h     # Register/peripheral macros
├── src/
│   ├── main.c            # Entry point, main loop
│   ├── config.h          # Build flags
│   ├── core/             # system.c (clocks), interrupts.c (IRQ vectors)
│   ├── drivers/          # uart, gpio, dac, adc, timer
│   ├── synth/            # keyboard scan, sequencer, cv_engine, clock
│   ├── midi/             # midi_parser, midi_handler, midi_output
│   ├── ui/               # pico_comm (UART framing), params
│   └── utils/            # debug.h printf, ring_buffer, math_utils,
│                         #   state_machine, types
└── tools/                # flash + monitor helpers
```

Build with `make` (requires `arm-none-eabi-gcc`); flash via ISP UART using
the included `tools/flash.sh`. JTAG is wired but unused — printf-over-UART
is the primary debug path.

> **Note on the rest of this document:** sections after this header contain
> the original design specification (file-by-file content sketches, debug-
> guide, Makefile template, etc.). They are *intent*, not the live source.
> For current code, browse the trees above directly.

---

# Core Files

## src/utils/debug.h

```c
#ifndef DEBUG_H
#define DEBUG_H

#include <stdio.h>
#include "config.h"

/*
 * Debug levels:
 * 0 = Off (production build)
 * 1 = Errors only
 * 2 = Errors + Info
 * 3 = Errors + Info + Verbose (spammy)
 */

#ifndef DEBUG_LEVEL
#define DEBUG_LEVEL 2
#endif

// Error: Always important, something went wrong
#if DEBUG_LEVEL >= 1
  #define DBG_ERR(fmt, ...) printf("[ERR %s:%d] " fmt "\r\n", __FILE__, __LINE__, ##__VA_ARGS__)
#else
  #define DBG_ERR(fmt, ...)
#endif

// Info: State changes, init steps, useful events
#if DEBUG_LEVEL >= 2
  #define DBG_INFO(fmt, ...) printf("[INF] " fmt "\r\n", ##__VA_ARGS__)
#else
  #define DBG_INFO(fmt, ...)
#endif

// Verbose: Every tick, every byte, very spammy
#if DEBUG_LEVEL >= 3
  #define DBG_VERB(fmt, ...) printf("[VRB] " fmt "\r\n", ##__VA_ARGS__)
#else
  #define DBG_VERB(fmt, ...)
#endif

// Assert with message
#define DBG_ASSERT(cond, fmt, ...) \
    do { \
        if (!(cond)) { \
            DBG_ERR("ASSERT FAIL: " fmt, ##__VA_ARGS__); \
            while(1); \
        } \
    } while(0)

// Print hex dump (for MIDI debugging)
#if DEBUG_LEVEL >= 3
static inline void dbg_hexdump(const char* label, uint8_t* data, int len) {
    printf("[HEX] %s: ", label);
    for (int i = 0; i < len; i++) {
        printf("%02X ", data[i]);
    }
    printf("\r\n");
}
#else
#define dbg_hexdump(label, data, len)
#endif

#endif // DEBUG_H
```

---

## src/config.h

```c
#ifndef CONFIG_H
#define CONFIG_H

// ===================
// BUILD CONFIGURATION
// ===================

// Debug level (0=off, 1=err, 2=info, 3=verbose)
#define DEBUG_LEVEL 2

// Debug UART baud rate
#define DEBUG_BAUD 115200

// ===================
// FEATURE FLAGS
// ===================

// Enable extended sequencer (64 steps vs 8)
#define FEATURE_EXTENDED_SEQ 1

// Enable per-step probability
#define FEATURE_PROBABILITY 1

// Enable ratcheting
#define FEATURE_RATCHET 1

// Enable euclidean patterns
#define FEATURE_EUCLIDEAN 1

// Enable arpeggiator
#define FEATURE_ARPEGGIATOR 1

// Enable Pico communication
#define FEATURE_PICO_COMM 1

// Enable MIDI output (requires hardware mod)
#define FEATURE_MIDI_OUT 0

// ===================
// HARDWARE CONFIG
// ===================

// Crystal frequency (Hz)
#define XTAL_FREQ 12000000

// CPU frequency (Hz)
#define CPU_FREQ 60000000

// Sequencer
#define SEQ_MAX_STEPS 64
#define SEQ_MAX_PATTERNS 8

// MIDI
#define MIDI_BAUD 31250

// ===================
// PIN ASSIGNMENTS
// ===================

// UART0 (Debug + ISP)
#define PIN_UART0_TX 0  // P0.0
#define PIN_UART0_RX 1  // P0.1

// UART1 (MIDI IN)
#define PIN_MIDI_RX 9   // P0.9 (check actual MicroBrute routing)

// UART3 (Pico communication)
#define PIN_PICO_TX 0   // P0.0 (shared with debug in dev)
#define PIN_PICO_RX 1   // P0.1

// DAC
#define PIN_DAC_OUT 26  // P0.26 (AOUT)

#endif // CONFIG_H
```

---

## src/main.c

```c
/*
 * MACROBRUTE Firmware
 * Open source firmware for Arturia MicroBrute expansion
 * 
 * https://github.com/jordanaftermidnight/uberbrute-firmware
 */

#include <stdint.h>
#include "config.h"
#include "utils/debug.h"
#include "core/system.h"
#include "drivers/uart.h"
#include "drivers/gpio.h"
#include "drivers/dac.h"
#include "drivers/timer.h"
#include "synth/keyboard.h"
#include "synth/sequencer.h"
#include "synth/clock.h"
#include "midi/midi_parser.h"
#include "midi/midi_handler.h"

#if FEATURE_PICO_COMM
#include "ui/pico_comm.h"
#endif

// Firmware version
#define VERSION_MAJOR 0
#define VERSION_MINOR 1
#define VERSION_PATCH 0

// Main system state
typedef enum {
    STATE_BOOT,
    STATE_IDLE,
    STATE_PLAYING,
    STATE_RECORDING,
    STATE_EDITING,
    STATE_ERROR
} SystemState;

static SystemState g_state = STATE_BOOT;

// State names for debug
static const char* state_names[] = {
    "BOOT", "IDLE", "PLAYING", "RECORDING", "EDITING", "ERROR"
};

void set_state(SystemState new_state) {
    if (new_state != g_state) {
        DBG_INFO("State: %s -> %s", state_names[g_state], state_names[new_state]);
        g_state = new_state;
    }
}

void print_banner(void) {
    printf("\r\n");
    printf("================================\r\n");
    printf("  MACROBRUTE v%d.%d.%d\r\n", VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH);
    printf("  MicroBrute Expansion Firmware\r\n");
    printf("================================\r\n");
    printf("Compiled: %s %s\r\n", __DATE__, __TIME__);
    printf("Debug level: %d\r\n", DEBUG_LEVEL);
    printf("\r\n");
}

int init_all(void) {
    int err = 0;
    
    // Clock and core system
    DBG_INFO("Init: System clock...");
    if ((err = system_init()) != 0) {
        DBG_ERR("System init failed: %d", err);
        return err;
    }
    
    // Debug UART (must be early for printf to work)
    DBG_INFO("Init: Debug UART...");
    if ((err = uart_init(0, DEBUG_BAUD)) != 0) {
        // Can't printf this error, UART failed!
        return err;
    }
    
    // Now we can print
    print_banner();
    
    // GPIO
    DBG_INFO("Init: GPIO...");
    if ((err = gpio_init()) != 0) {
        DBG_ERR("GPIO init failed: %d", err);
        return err;
    }
    
    // Timer / system tick
    DBG_INFO("Init: Timer...");
    if ((err = timer_init()) != 0) {
        DBG_ERR("Timer init failed: %d", err);
        return err;
    }
    
    // DAC for pitch CV
    DBG_INFO("Init: DAC...");
    if ((err = dac_init()) != 0) {
        DBG_ERR("DAC init failed: %d", err);
        return err;
    }
    
    // Keyboard matrix
    DBG_INFO("Init: Keyboard...");
    if ((err = keyboard_init()) != 0) {
        DBG_ERR("Keyboard init failed: %d", err);
        return err;
    }
    
    // Sequencer
    DBG_INFO("Init: Sequencer...");
    if ((err = sequencer_init()) != 0) {
        DBG_ERR("Sequencer init failed: %d", err);
        return err;
    }
    
    // Clock / tempo
    DBG_INFO("Init: Clock...");
    if ((err = clock_init()) != 0) {
        DBG_ERR("Clock init failed: %d", err);
        return err;
    }
    
    // MIDI
    DBG_INFO("Init: MIDI...");
    if ((err = midi_parser_init()) != 0) {
        DBG_ERR("MIDI init failed: %d", err);
        return err;
    }
    
#if FEATURE_PICO_COMM
    // Pico communication
    DBG_INFO("Init: Pico comm...");
    if ((err = pico_comm_init()) != 0) {
        DBG_ERR("Pico comm init failed: %d", err);
        return err;
    }
#endif
    
    return 0;
}

int main(void) {
    // Initialize everything
    if (init_all() != 0) {
        DBG_ERR("=== INIT FAILED ===");
        set_state(STATE_ERROR);
        while(1) {
            // Blink error LED or something
        }
    }
    
    DBG_INFO("=== INIT COMPLETE ===");
    set_state(STATE_IDLE);
    
    // Main loop
    uint32_t last_tick = 0;
    uint32_t loop_count = 0;
    
    while (1) {
        loop_count++;
        
        // Periodic debug heartbeat (every ~1 second)
        if (DEBUG_LEVEL >= 3 && (loop_count % 100000) == 0) {
            DBG_VERB("Heartbeat: loops=%lu, state=%s", loop_count, state_names[g_state]);
        }
        
        // Scan keyboard matrix
        keyboard_scan();
        
        // Process incoming MIDI
        while (uart_available(1)) {  // UART1 = MIDI
            uint8_t byte = uart_read(1);
            midi_parser_feed(byte);
        }
        
        // Update sequencer
        sequencer_update();
        
        // Update clock
        clock_update();
        
#if FEATURE_PICO_COMM
        // Handle Pico communication
        pico_comm_update();
#endif
    }
    
    return 0;
}
```

---

## src/synth/sequencer.h

```c
#ifndef SEQUENCER_H
#define SEQUENCER_H

#include <stdint.h>
#include "config.h"

// Step flags
#define STEP_FLAG_REST    (1 << 0)
#define STEP_FLAG_TIE     (1 << 1)
#define STEP_FLAG_ACCENT  (1 << 2)
#define STEP_FLAG_SLIDE   (1 << 3)

// Single sequencer step
typedef struct {
    uint8_t note;           // MIDI note (0-127)
    uint8_t velocity;       // Velocity (0-127)
    uint8_t gate_length;    // Gate length (0-100%)
    uint8_t probability;    // Probability (0-100%)
    uint8_t ratchet;        // Ratchet count (1-8)
    uint8_t flags;          // STEP_FLAG_*
} SeqStep;

// Sequencer state
typedef enum {
    SEQ_STOPPED,
    SEQ_PLAYING,
    SEQ_PAUSED,
    SEQ_RECORDING
} SeqState;

// Sequencer direction
typedef enum {
    SEQ_DIR_FORWARD,
    SEQ_DIR_BACKWARD,
    SEQ_DIR_PINGPONG,
    SEQ_DIR_RANDOM
} SeqDirection;

// Main sequencer struct
typedef struct {
    SeqStep steps[SEQ_MAX_STEPS];
    uint8_t length;             // Active length (1-64)
    uint8_t current_step;       // Current position
    uint8_t pattern;            // Current pattern (0-7)
    
    SeqState state;
    SeqDirection direction;
    
    uint8_t swing;              // Swing amount (0-75%)
    uint8_t scale;              // Scale quantize (0=off)
    uint8_t root_note;          // Root note for scale
    
    // Internal state
    int8_t pingpong_dir;        // 1 or -1 for pingpong
    uint8_t ratchet_count;      // Current ratchet position
} Sequencer;

// API
int sequencer_init(void);
void sequencer_update(void);

void sequencer_start(void);
void sequencer_stop(void);
void sequencer_pause(void);

void sequencer_set_step(uint8_t step, SeqStep* data);
SeqStep* sequencer_get_step(uint8_t step);

void sequencer_set_length(uint8_t len);
void sequencer_set_direction(SeqDirection dir);
void sequencer_set_swing(uint8_t swing);

// Called by clock
void sequencer_tick(void);

// Debug
void sequencer_print_state(void);

#endif // SEQUENCER_H
```

---

## src/synth/sequencer.c

```c
#include "sequencer.h"
#include "cv_engine.h"
#include "utils/debug.h"
#include "utils/math_utils.h"

static Sequencer g_seq;

int sequencer_init(void) {
    DBG_INFO("Sequencer: init %d steps", SEQ_MAX_STEPS);
    
    // Clear all steps
    for (int i = 0; i < SEQ_MAX_STEPS; i++) {
        g_seq.steps[i].note = 60;       // Middle C
        g_seq.steps[i].velocity = 100;
        g_seq.steps[i].gate_length = 50;
        g_seq.steps[i].probability = 100;
        g_seq.steps[i].ratchet = 1;
        g_seq.steps[i].flags = 0;
    }
    
    g_seq.length = 8;           // Default 8 steps
    g_seq.current_step = 0;
    g_seq.pattern = 0;
    g_seq.state = SEQ_STOPPED;
    g_seq.direction = SEQ_DIR_FORWARD;
    g_seq.swing = 0;
    g_seq.scale = 0;
    g_seq.root_note = 60;
    g_seq.pingpong_dir = 1;
    g_seq.ratchet_count = 0;
    
    DBG_INFO("Sequencer: ready");
    return 0;
}

void sequencer_start(void) {
    DBG_INFO("Sequencer: START");
    g_seq.current_step = 0;
    g_seq.state = SEQ_PLAYING;
    g_seq.pingpong_dir = 1;
}

void sequencer_stop(void) {
    DBG_INFO("Sequencer: STOP");
    g_seq.state = SEQ_STOPPED;
    g_seq.current_step = 0;
    cv_gate_off();
}

void sequencer_pause(void) {
    if (g_seq.state == SEQ_PLAYING) {
        DBG_INFO("Sequencer: PAUSE");
        g_seq.state = SEQ_PAUSED;
        cv_gate_off();
    } else if (g_seq.state == SEQ_PAUSED) {
        DBG_INFO("Sequencer: RESUME");
        g_seq.state = SEQ_PLAYING;
    }
}

static void advance_step(void) {
    switch (g_seq.direction) {
        case SEQ_DIR_FORWARD:
            g_seq.current_step = (g_seq.current_step + 1) % g_seq.length;
            break;
            
        case SEQ_DIR_BACKWARD:
            if (g_seq.current_step == 0) {
                g_seq.current_step = g_seq.length - 1;
            } else {
                g_seq.current_step--;
            }
            break;
            
        case SEQ_DIR_PINGPONG:
            g_seq.current_step += g_seq.pingpong_dir;
            if (g_seq.current_step >= g_seq.length - 1) {
                g_seq.pingpong_dir = -1;
            } else if (g_seq.current_step == 0) {
                g_seq.pingpong_dir = 1;
            }
            break;
            
        case SEQ_DIR_RANDOM:
            g_seq.current_step = random_range(0, g_seq.length);
            break;
    }
    
    DBG_VERB("Seq: step -> %d", g_seq.current_step);
}

void sequencer_tick(void) {
    if (g_seq.state != SEQ_PLAYING) {
        return;
    }
    
    SeqStep* step = &g_seq.steps[g_seq.current_step];
    
    // Check probability
#if FEATURE_PROBABILITY
    if (step->probability < 100) {
        uint8_t roll = random_percent();
        if (roll > step->probability) {
            DBG_VERB("Seq: step %d skipped (prob %d, roll %d)", 
                     g_seq.current_step, step->probability, roll);
            advance_step();
            return;
        }
    }
#endif
    
    // Check rest flag
    if (step->flags & STEP_FLAG_REST) {
        DBG_VERB("Seq: step %d rest", g_seq.current_step);
        cv_gate_off();
        advance_step();
        return;
    }
    
    // Play the note
    uint8_t note = step->note;
    
    // Apply scale quantize if enabled
    if (g_seq.scale > 0) {
        note = quantize_to_scale(note, g_seq.scale, g_seq.root_note);
    }
    
    DBG_VERB("Seq: step %d note %d vel %d", 
             g_seq.current_step, note, step->velocity);
    
    // Set CV and gate
    cv_set_note(note);
    cv_gate_on();
    
    // Schedule gate off based on gate_length
    // (handled by cv_engine with timer)
    cv_schedule_gate_off(step->gate_length);
    
#if FEATURE_RATCHET
    // Handle ratcheting
    if (step->ratchet > 1) {
        g_seq.ratchet_count++;
        if (g_seq.ratchet_count >= step->ratchet) {
            g_seq.ratchet_count = 0;
            advance_step();
        }
        // Don't advance, repeat this step
        return;
    }
#endif
    
    advance_step();
}

void sequencer_update(void) {
    // Called from main loop
    // Any non-time-critical sequencer tasks
}

void sequencer_set_length(uint8_t len) {
    if (len > 0 && len <= SEQ_MAX_STEPS) {
        DBG_INFO("Seq: length = %d", len);
        g_seq.length = len;
        if (g_seq.current_step >= len) {
            g_seq.current_step = 0;
        }
    }
}

void sequencer_set_direction(SeqDirection dir) {
    DBG_INFO("Seq: direction = %d", dir);
    g_seq.direction = dir;
    g_seq.pingpong_dir = 1;
}

void sequencer_set_swing(uint8_t swing) {
    if (swing <= 75) {
        DBG_INFO("Seq: swing = %d%%", swing);
        g_seq.swing = swing;
    }
}

void sequencer_set_step(uint8_t step, SeqStep* data) {
    if (step < SEQ_MAX_STEPS) {
        g_seq.steps[step] = *data;
        DBG_VERB("Seq: set step %d = note %d", step, data->note);
    }
}

SeqStep* sequencer_get_step(uint8_t step) {
    if (step < SEQ_MAX_STEPS) {
        return &g_seq.steps[step];
    }
    return NULL;
}

void sequencer_print_state(void) {
    const char* state_str[] = {"STOPPED", "PLAYING", "PAUSED", "RECORDING"};
    const char* dir_str[] = {"FWD", "BWD", "PING", "RAND"};
    
    printf("\r\n=== Sequencer State ===\r\n");
    printf("State: %s\r\n", state_str[g_seq.state]);
    printf("Step: %d / %d\r\n", g_seq.current_step, g_seq.length);
    printf("Direction: %s\r\n", dir_str[g_seq.direction]);
    printf("Swing: %d%%\r\n", g_seq.swing);
    printf("\r\nSteps:\r\n");
    for (int i = 0; i < g_seq.length; i++) {
        SeqStep* s = &g_seq.steps[i];
        printf("  [%02d] N:%3d V:%3d G:%3d%% P:%3d%% R:%d %s%s%s%s\r\n",
               i, s->note, s->velocity, s->gate_length, s->probability, s->ratchet,
               (s->flags & STEP_FLAG_REST) ? "REST " : "",
               (s->flags & STEP_FLAG_TIE) ? "TIE " : "",
               (s->flags & STEP_FLAG_ACCENT) ? "ACC " : "",
               (s->flags & STEP_FLAG_SLIDE) ? "SLD " : "");
    }
    printf("=======================\r\n");
}
```

---

## src/startup/syscalls.c

```c
/*
 * Newlib syscall stubs
 * Redirects printf to UART for debug output
 */

#include <sys/stat.h>
#include <errno.h>
#include "drivers/uart.h"

// _write - called by printf
int _write(int fd, char *buf, int len) {
    for (int i = 0; i < len; i++) {
        uart_putc(0, buf[i]);  // UART0 = debug
    }
    return len;
}

// _read - not implemented
int _read(int fd, char *buf, int len) {
    return -1;
}

// Required stubs
int _close(int fd) { return -1; }
int _lseek(int fd, int offset, int whence) { return -1; }
int _fstat(int fd, struct stat *st) { st->st_mode = S_IFCHR; return 0; }
int _isatty(int fd) { return 1; }

// Memory allocation
extern char _end;
static char *heap_end = NULL;

void *_sbrk(int incr) {
    char *prev_heap_end;
    
    if (heap_end == NULL) {
        heap_end = &_end;
    }
    prev_heap_end = heap_end;
    heap_end += incr;
    
    return prev_heap_end;
}
```

---

## tools/flash.sh

```bash
#!/bin/bash
# Flash MACROBRUTE firmware via ISP
# Usage: ./flash.sh firmware.hex [/dev/ttyUSB0]

FIRMWARE=${1:-"build/uberbrute.hex"}
PORT=${2:-"/dev/ttyUSB0"}

echo "==================================="
echo "  MACROBRUTE ISP Flash Utility"
echo "==================================="
echo "Firmware: $FIRMWARE"
echo "Port: $PORT"
echo ""

if [ ! -f "$FIRMWARE" ]; then
    echo "ERROR: Firmware file not found: $FIRMWARE"
    exit 1
fi

if [ ! -e "$PORT" ]; then
    echo "ERROR: Serial port not found: $PORT"
    echo "Available ports:"
    ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "  (none found)"
    exit 1
fi

echo "*** Put MicroBrute in ISP mode: ***"
echo "  1. Power off MicroBrute"
echo "  2. Connect ISP jumper (P0.14 to GND)"
echo "  3. Power on MicroBrute"
echo "  4. Press Enter to continue..."
read

echo "Flashing..."
lpc21isp -control -verify "$FIRMWARE" "$PORT" 115200 12000

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "  Flash complete!"
    echo "==================================="
    echo "Remove ISP jumper and reset MicroBrute"
else
    echo ""
    echo "ERROR: Flash failed!"
    exit 1
fi
```

---

## tools/monitor.sh

```bash
#!/bin/bash
# Serial monitor for debug output
# Usage: ./monitor.sh [/dev/ttyUSB0] [115200]

PORT=${1:-"/dev/ttyUSB0"}
BAUD=${2:-"115200"}

echo "MACROBRUTE Debug Monitor"
echo "Port: $PORT @ $BAUD baud"
echo "Press Ctrl+A then X to exit"
echo "=========================="

minicom -D "$PORT" -b "$BAUD"
```

---

## Makefile

```makefile
# MACROBRUTE Firmware Makefile

# Project
PROJECT = uberbrute
VERSION = 0.1.0

# Toolchain
CC = arm-none-eabi-gcc
AS = arm-none-eabi-as
LD = arm-none-eabi-ld
OBJCOPY = arm-none-eabi-objcopy
SIZE = arm-none-eabi-size

# Directories
SRC_DIR = src
BUILD_DIR = build
INC_DIR = include

# Source files
SRCS = $(wildcard $(SRC_DIR)/*.c) \
       $(wildcard $(SRC_DIR)/**/*.c)
ASMS = $(wildcard startup/*.s)

OBJS = $(SRCS:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o) \
       $(ASMS:%.s=$(BUILD_DIR)/%.o)

# Flags
CPU = -mcpu=arm7tdmi
CFLAGS = $(CPU) -mthumb-interwork -g -O2 -Wall
CFLAGS += -I$(SRC_DIR) -I$(INC_DIR)
CFLAGS += -DDEBUG_LEVEL=2

LDFLAGS = $(CPU) -mthumb-interwork
LDFLAGS += -T linker/lpc2361.ld
LDFLAGS += -nostartfiles
LDFLAGS += --specs=nano.specs

# Targets
.PHONY: all clean flash monitor

all: $(BUILD_DIR)/$(PROJECT).hex $(BUILD_DIR)/$(PROJECT).bin
	@$(SIZE) $(BUILD_DIR)/$(PROJECT).elf

$(BUILD_DIR)/$(PROJECT).elf: $(OBJS)
	@mkdir -p $(dir $@)
	$(CC) $(LDFLAGS) -o $@ $^

$(BUILD_DIR)/$(PROJECT).hex: $(BUILD_DIR)/$(PROJECT).elf
	$(OBJCOPY) -O ihex $< $@

$(BUILD_DIR)/$(PROJECT).bin: $(BUILD_DIR)/$(PROJECT).elf
	$(OBJCOPY) -O binary $< $@

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD_DIR)/%.o: startup/%.s
	@mkdir -p $(dir $@)
	$(AS) $(CPU) -o $@ $<

clean:
	rm -rf $(BUILD_DIR)

flash: $(BUILD_DIR)/$(PROJECT).hex
	./tools/flash.sh $<

monitor:
	./tools/monitor.sh

# Debug build
debug: CFLAGS += -DDEBUG_LEVEL=3
debug: all

# Release build (no debug)
release: CFLAGS += -DDEBUG_LEVEL=0 -Os
release: all
```

---

## docs/debugging.md

```markdown
# MACROBRUTE Debugging Guide

## Printf Debugging

This firmware uses printf-style debugging over UART. No JTAG required.

### Hardware Setup

Connect your USB-TTL adapter:

| USB-TTL | LPC2361 (MicroBrute) |
|---------|---------------------|
| TX | P0.1 (RXD0) - Pin 47 |
| RX | P0.0 (TXD0) - Pin 46 |
| GND | GND |
| 3.3V | DO NOT CONNECT |

### Serial Settings

- Baud: 115200
- Data: 8 bits
- Parity: None
- Stop: 1 bit
- Flow control: None

### Viewing Debug Output

Linux:
```bash
./tools/monitor.sh
# or
minicom -D /dev/ttyUSB0 -b 115200
```

Windows:
- Use PuTTY
- Select COM port
- Set baud to 115200

### Debug Levels

Set in `config.h`:

```c
#define DEBUG_LEVEL 2
```

| Level | Output |
|-------|--------|
| 0 | None (production) |
| 1 | Errors only |
| 2 | Errors + Info (recommended) |
| 3 | Everything (very spammy) |

### Debug Macros

```c
DBG_ERR("Something broke: %d", error_code);  // Level 1+
DBG_INFO("State changed to: %s", state);      // Level 2+
DBG_VERB("Processing byte: 0x%02X", byte);    // Level 3 only
```

### Example Output

```
================================
  MACROBRUTE v0.1.0
  MicroBrute Expansion Firmware
================================
Compiled: Mar 21 2026 15:30:00
Debug level: 2

[INF] Init: System clock...
[INF] Init: Debug UART...
[INF] Init: GPIO...
[INF] Init: Timer...
[INF] Init: DAC...
[INF] Init: Keyboard...
[INF] Init: Sequencer...
[INF] Sequencer: init 64 steps
[INF] Sequencer: ready
[INF] Init: Clock...
[INF] Init: MIDI...
[INF] === INIT COMPLETE ===
[INF] State: BOOT -> IDLE
```

### Debugging Tips

1. **Startup hangs?** Check which init message was last printed
2. **MIDI issues?** Enable level 3, watch for `[VRB] MIDI byte:`
3. **Sequencer problems?** Call `sequencer_print_state()` from main loop
4. **Timing issues?** Add heartbeat prints with loop counter

### Common Issues

**No output at all:**
- Check TX/RX wiring (they're crossed)
- Verify baud rate matches
- Make sure UART init runs before first printf

**Garbled output:**
- Wrong baud rate
- Wrong crystal frequency in config.h

**Missing messages:**
- Check DEBUG_LEVEL is high enough
- Printf buffer might be full (add small delays)
```

---

## docs/isp-flashing.md

```markdown
# ISP Flashing Guide

## Overview

The LPC2361 can be programmed via UART using In-System Programming (ISP).
This doesn't require a JTAG debugger.

## Hardware Setup

Same wiring as debug UART, plus ISP enable:

| USB-TTL | LPC2361 |
|---------|---------|
| TX | P0.1 (RXD0) |
| RX | P0.0 (TXD0) |
| GND | GND |

**ISP Enable:** P0.14 must be LOW during reset to enter ISP mode.

## Entering ISP Mode

1. Power off MicroBrute
2. Connect P0.14 to GND (jumper wire)
3. Power on MicroBrute
4. LPC2361 is now in ISP bootloader

## Flashing (Linux)

Install lpc21isp:
```bash
sudo apt install lpc21isp
```

Flash:
```bash
lpc21isp -control firmware.hex /dev/ttyUSB0 115200 12000
```

Or use the provided script:
```bash
./tools/flash.sh build/uberbrute.hex
```

## Flashing (Windows)

Use Flash Magic (free):
1. Download from flashmagictool.com
2. Select LPC2361
3. Set COM port and baud (115200)
4. Set crystal to 12000 kHz
5. Browse to .hex file
6. Click Start

## After Flashing

1. Remove ISP jumper (P0.14 to GND)
2. Reset or power cycle MicroBrute
3. New firmware runs

## Troubleshooting

**"No response from device":**
- Check wiring
- Verify ISP jumper is connected
- Try lower baud rate (38400)

**"Verify failed":**
- Flash might be protected (CRP)
- Try full erase first

**CRP (Code Read Protection):**
- If CRP is enabled, you can only do full erase
- Full erase wipes everything including CRP
- Then you can flash new firmware
```
