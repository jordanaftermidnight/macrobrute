/*
 * Clock / tempo engine
 * Internal BPM clock with external sync support
 */

#include "clock.h"
#include "drivers/timer.h"
#include "utils/debug.h"

static uint16_t bpm = 120;
static uint32_t tick_interval_ms = 500;  // ms per quarter note
static uint32_t last_tick = 0;
static bool running = false;
static clock_tick_fn tick_cb = NULL;

// PPQN (pulses per quarter note) — standard MIDI = 24
#define PPQN 24

static uint32_t pulse_interval_ms;
static uint32_t last_pulse = 0;

static void recalc_interval(void) {
    tick_interval_ms = 60000 / bpm;                     // ms per quarter note
    pulse_interval_ms = 60000 / (bpm * PPQN);           // ms per MIDI clock pulse
}

int clock_init(void) {
    recalc_interval();
    DBG_INFO("Clock: %d BPM, tick=%dms", bpm, tick_interval_ms);
    return 0;
}

void clock_set_bpm(uint16_t new_bpm) {
    if (new_bpm < 20) new_bpm = 20;
    if (new_bpm > 300) new_bpm = 300;
    bpm = new_bpm;
    recalc_interval();
    DBG_INFO("Clock: BPM -> %d", bpm);
}

uint16_t clock_get_bpm(void) {
    return bpm;
}

void clock_start(void) {
    running = true;
    last_tick = timer_get_ms();
    last_pulse = last_tick;
    DBG_INFO("Clock: START");
}

void clock_stop(void) {
    running = false;
    DBG_INFO("Clock: STOP");
}

void clock_set_tick_callback(clock_tick_fn fn) {
    tick_cb = fn;
}

uint32_t clock_step_duration_ms(void) {
    return tick_interval_ms;
}

void clock_update(void) {
    if (!running) return;

    uint32_t now = timer_get_ms();

    // Check for sequencer tick (quarter note)
    if ((now - last_tick) >= tick_interval_ms) {
        last_tick = now;
        if (tick_cb) {
            tick_cb();
        }
    }
}
