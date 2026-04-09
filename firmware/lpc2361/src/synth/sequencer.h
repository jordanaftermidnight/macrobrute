#ifndef SEQUENCER_H
#define SEQUENCER_H

#include <stdint.h>
#include "config.h"

// Step flags
#define STEP_FLAG_REST    (1 << 0)
#define STEP_FLAG_TIE     (1 << 1)
#define STEP_FLAG_ACCENT  (1 << 2)
#define STEP_FLAG_SLIDE   (1 << 3)

typedef struct {
    uint8_t note;
    uint8_t velocity;
    uint8_t gate_length;    // 0-100%
    uint8_t probability;    // 0-100%
    uint8_t ratchet;        // 1-8
    uint8_t flags;          // STEP_FLAG_*
} SeqStep;

typedef enum {
    SEQ_STOPPED,
    SEQ_PLAYING,
    SEQ_PAUSED,
    SEQ_RECORDING
} SeqState;

typedef enum {
    SEQ_DIR_FORWARD,
    SEQ_DIR_BACKWARD,
    SEQ_DIR_PINGPONG,
    SEQ_DIR_RANDOM
} SeqDirection;

typedef struct {
    SeqStep steps[SEQ_MAX_STEPS];
    uint8_t length;
    uint8_t current_step;
    uint8_t pattern;

    SeqState state;
    SeqDirection direction;

    uint8_t swing;
    uint8_t scale;
    uint8_t root_note;

    int8_t pingpong_dir;
    uint8_t ratchet_count;
} Sequencer;

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

void sequencer_tick(void);
void sequencer_print_state(void);

#endif // SEQUENCER_H
