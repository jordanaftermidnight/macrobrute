/*
 * MACROBRUTE Firmware
 * Open source firmware for Arturia MicroBrute expansion
 *
 * Target: NXP LPC2361 (ARM7TDMI-S, 128KB Flash, 34KB SRAM)
 * Crystal: 12MHz -> 60MHz via PLL
 */

#include <stdint.h>
#include "config.h"
#include "utils/debug.h"
#include "core/system.h"
#include "core/interrupts.h"
#include "drivers/uart.h"
#include "drivers/gpio.h"
#include "drivers/dac.h"
#include "drivers/timer.h"
#include "synth/keyboard.h"
#include "synth/sequencer.h"
#include "synth/cv_engine.h"
#include "synth/clock.h"
#include "midi/midi_parser.h"
#include "midi/midi_handler.h"
#include "ui/params.h"

#if FEATURE_PICO_COMM
#include "ui/pico_comm.h"
#endif

#define VERSION_MAJOR 0
#define VERSION_MINOR 1
#define VERSION_PATCH 0

typedef enum {
    STATE_BOOT,
    STATE_IDLE,
    STATE_PLAYING,
    STATE_RECORDING,
    STATE_EDITING,
    STATE_ERROR
} SystemState;

static SystemState g_state = STATE_BOOT;

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

    DBG_INFO("Init: System clock...");
    if ((err = system_init()) != 0) {
        DBG_ERR("System init failed: %d", err);
        return err;
    }

    DBG_INFO("Init: Debug UART...");
    if ((err = uart_init(0, DEBUG_BAUD)) != 0) {
        return err;
    }

    print_banner();

    DBG_INFO("Init: GPIO...");
    if ((err = gpio_init()) != 0) {
        DBG_ERR("GPIO init failed: %d", err);
        return err;
    }

    DBG_INFO("Init: Timer...");
    if ((err = timer_init()) != 0) {
        DBG_ERR("Timer init failed: %d", err);
        return err;
    }

    DBG_INFO("Init: CV engine...");
    if ((err = cv_engine_init()) != 0) {
        DBG_ERR("CV engine init failed: %d", err);
        return err;
    }

    DBG_INFO("Init: Keyboard...");
    if ((err = keyboard_init()) != 0) {
        DBG_ERR("Keyboard init failed: %d", err);
        return err;
    }

    DBG_INFO("Init: Sequencer...");
    if ((err = sequencer_init()) != 0) {
        DBG_ERR("Sequencer init failed: %d", err);
        return err;
    }

    DBG_INFO("Init: Clock...");
    if ((err = clock_init()) != 0) {
        DBG_ERR("Clock init failed: %d", err);
        return err;
    }

    // Wire clock tick to sequencer
    clock_set_tick_callback(sequencer_tick);

    DBG_INFO("Init: MIDI...");
    if ((err = midi_parser_init()) != 0) {
        DBG_ERR("MIDI init failed: %d", err);
        return err;
    }

    // Init MIDI UART (31250 baud)
    if ((err = uart_init(1, MIDI_BAUD)) != 0) {
        DBG_ERR("MIDI UART init failed: %d", err);
        return err;
    }

    midi_handler_init();

    DBG_INFO("Init: Parameters...");
    params_init();

#if FEATURE_PICO_COMM
    DBG_INFO("Init: Pico comm...");
    if ((err = pico_comm_init()) != 0) {
        DBG_ERR("Pico comm init failed: %d", err);
        return err;
    }
#endif

    return 0;
}

int main(void) {
    if (init_all() != 0) {
        DBG_ERR("=== INIT FAILED ===");
        set_state(STATE_ERROR);
        while(1);
    }

    DBG_INFO("=== INIT COMPLETE ===");
    set_state(STATE_IDLE);

    uint32_t loop_count = 0;

    while (1) {
        loop_count++;

        if (DEBUG_LEVEL >= 3 && (loop_count % 100000) == 0) {
            DBG_VERB("Heartbeat: loops=%lu, state=%s", loop_count, state_names[g_state]);
        }

        keyboard_scan();

        while (uart_available(1)) {
            uint8_t byte = (uint8_t)uart_read(1);
            midi_parser_feed(byte);
        }

        sequencer_update();
        clock_update();
        cv_engine_update();

#if FEATURE_PICO_COMM
        pico_comm_update();
#endif
    }

    return 0;
}
