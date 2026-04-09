#ifndef PARAMS_H
#define PARAMS_H

#include <stdint.h>

// Parameter IDs (matches Pico firmware menu structure)
typedef enum {
    PARAM_BPM = 0,
    PARAM_SEQ_LENGTH,
    PARAM_SEQ_DIRECTION,
    PARAM_SWING,
    PARAM_GATE_LENGTH,
    PARAM_SCALE,
    PARAM_ROOT_NOTE,
    PARAM_MIDI_CHANNEL,
    PARAM_BEND_RANGE,
    PARAM_NOTE_PRIORITY,
    PARAM_VELOCITY_RESPONSE,
    PARAM_COUNT
} ParamId;

// Get/set parameter values
uint16_t param_get(ParamId id);
void param_set(ParamId id, uint16_t value);

// Initialize defaults
void params_init(void);

#endif // PARAMS_H
