/*
 * Parameter management
 * Central store for all configurable parameters
 */

#include "params.h"
#include "synth/sequencer.h"
#include "synth/clock.h"
#include "utils/debug.h"

static uint16_t param_values[PARAM_COUNT];

void params_init(void) {
    param_values[PARAM_BPM] = 120;
    param_values[PARAM_SEQ_LENGTH] = 8;
    param_values[PARAM_SEQ_DIRECTION] = SEQ_DIR_FORWARD;
    param_values[PARAM_SWING] = 0;
    param_values[PARAM_GATE_LENGTH] = 50;
    param_values[PARAM_SCALE] = 0;       // Chromatic
    param_values[PARAM_ROOT_NOTE] = 60;  // C4
    param_values[PARAM_MIDI_CHANNEL] = 0;
    param_values[PARAM_BEND_RANGE] = 2;
    param_values[PARAM_NOTE_PRIORITY] = 0;  // Last note
    param_values[PARAM_VELOCITY_RESPONSE] = 1;

    DBG_INFO("Params: defaults loaded");
}

uint16_t param_get(ParamId id) {
    if (id >= PARAM_COUNT) return 0;
    return param_values[id];
}

void param_set(ParamId id, uint16_t value) {
    if (id >= PARAM_COUNT) return;

    param_values[id] = value;

    // Apply parameter changes to subsystems
    switch (id) {
        case PARAM_BPM:
            clock_set_bpm(value);
            break;
        case PARAM_SEQ_LENGTH:
            sequencer_set_length(value);
            break;
        case PARAM_SEQ_DIRECTION:
            sequencer_set_direction((SeqDirection)value);
            break;
        case PARAM_SWING:
            sequencer_set_swing(value);
            break;
        default:
            break;
    }

    DBG_INFO("Param %d = %d", id, value);
}
