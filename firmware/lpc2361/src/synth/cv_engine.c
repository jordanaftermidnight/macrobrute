/*
 * CV/Gate engine
 * Drives pitch CV via MCP4728 (I2C DAC) and gate via GPIO
 */

#include "cv_engine.h"
#include "drivers/dac.h"
#include "drivers/gpio.h"
#include "drivers/timer.h"
#include "utils/math_utils.h"
#include "utils/debug.h"
#include "config.h"

static uint32_t gate_off_time = 0;
static bool gate_scheduled = false;

int cv_engine_init(void) {
    // On-chip DAC for auxiliary CV
    dac_init();

    // MCP4728 for precision pitch CV
    mcp4728_init();

    // Gate pin already configured in gpio_init()

    DBG_INFO("CV engine: ready");
    return 0;
}

void cv_set_note(uint8_t note) {
    uint16_t dac_val = note_to_dac(note);
    mcp4728_write(0, dac_val);  // Channel 0 = pitch
    DBG_VERB("CV: note %d -> DAC %d", note, dac_val);
}

void cv_set_raw(uint16_t value) {
    mcp4728_write(0, value);
}

void cv_gate_on(void) {
    gpio_set(PIN_GATE_PORT, PIN_GATE_PIN);
    gate_scheduled = false;
}

void cv_gate_off(void) {
    gpio_clear(PIN_GATE_PORT, PIN_GATE_PIN);
    gate_scheduled = false;
}

void cv_schedule_gate_off(uint8_t percent) {
    // percent = gate length as % of step time
    // Actual timing depends on current tempo — simplified here
    // In practice, clock.c would provide the step duration
    uint32_t now = timer_get_ms();
    uint32_t duration = 100;  // TODO: get from clock module
    gate_off_time = now + (duration * percent / 100);
    gate_scheduled = true;
}

void cv_engine_update(void) {
    if (gate_scheduled && timer_get_ms() >= gate_off_time) {
        cv_gate_off();
    }
}
