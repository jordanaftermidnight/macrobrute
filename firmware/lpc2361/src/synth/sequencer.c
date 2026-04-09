#include "sequencer.h"
#include "cv_engine.h"
#include "utils/debug.h"
#include "utils/math_utils.h"

static Sequencer g_seq;

int sequencer_init(void) {
    DBG_INFO("Sequencer: init %d steps", SEQ_MAX_STEPS);

    for (int i = 0; i < SEQ_MAX_STEPS; i++) {
        g_seq.steps[i].note = 60;
        g_seq.steps[i].velocity = 100;
        g_seq.steps[i].gate_length = 50;
        g_seq.steps[i].probability = 100;
        g_seq.steps[i].ratchet = 1;
        g_seq.steps[i].flags = 0;
    }

    g_seq.length = 8;
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
    if (g_seq.state != SEQ_PLAYING) return;

    SeqStep* step = &g_seq.steps[g_seq.current_step];

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

    if (step->flags & STEP_FLAG_REST) {
        DBG_VERB("Seq: step %d rest", g_seq.current_step);
        cv_gate_off();
        advance_step();
        return;
    }

    uint8_t note = step->note;
    if (g_seq.scale > 0) {
        note = quantize_to_scale(note, g_seq.scale, g_seq.root_note);
    }

    DBG_VERB("Seq: step %d note %d vel %d",
             g_seq.current_step, note, step->velocity);

    cv_set_note(note);
    cv_gate_on();
    cv_schedule_gate_off(step->gate_length);

#if FEATURE_RATCHET
    if (step->ratchet > 1) {
        g_seq.ratchet_count++;
        if (g_seq.ratchet_count >= step->ratchet) {
            g_seq.ratchet_count = 0;
            advance_step();
        }
        return;
    }
#endif

    advance_step();
}

void sequencer_update(void) {
    // Non-time-critical sequencer tasks
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
