#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

/*
 * Simple state machine macros for event-driven subsystems.
 *
 * Usage:
 *   SM_DEFINE(my_sm, MY_STATE_IDLE);
 *
 *   void my_sm_update(void) {
 *       SM_BEGIN(my_sm)
 *       SM_STATE(MY_STATE_IDLE) {
 *           if (event) SM_TRANSITION(my_sm, MY_STATE_ACTIVE);
 *       }
 *       SM_STATE(MY_STATE_ACTIVE) {
 *           // do stuff
 *       }
 *       SM_END
 *   }
 */

#define SM_DEFINE(name, initial) \
    static int name##_state = (initial); \
    static int name##_prev_state = (initial)

#define SM_BEGIN(name) \
    switch (name##_state) {

#define SM_STATE(s) \
    case (s):

#define SM_TRANSITION(name, new_state) \
    do { \
        name##_prev_state = name##_state; \
        name##_state = (new_state); \
    } while(0)

#define SM_CURRENT(name) (name##_state)
#define SM_PREVIOUS(name) (name##_prev_state)

#define SM_END \
    }

#endif // STATE_MACHINE_H
