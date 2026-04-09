/*
 * MIDI message handlers
 * Routes parsed MIDI to synth engine
 */

#include "midi_handler.h"
#include "synth/cv_engine.h"
#include "synth/sequencer.h"
#include "synth/clock.h"
#include "utils/debug.h"
#include "config.h"

void midi_handler_init(void) {
    midi_set_msg_callback(midi_on_message);
    midi_set_sysex_callback(midi_on_sysex);
    midi_set_realtime_callback(midi_on_realtime);
    DBG_INFO("MIDI handler: ready");
}

void midi_on_message(const MidiMsg* msg) {
    switch (msg->status) {
        case MIDI_NOTE_ON:
            if (msg->data2 > 0) {
                cv_set_note(msg->data1);
                cv_gate_on();
                DBG_VERB("MIDI: Note ON %d vel %d", msg->data1, msg->data2);
            } else {
                // Note ON with vel 0 = Note OFF
                cv_gate_off();
            }
            break;

        case MIDI_NOTE_OFF:
            cv_gate_off();
            DBG_VERB("MIDI: Note OFF %d", msg->data1);
            break;

        case MIDI_CC:
            DBG_VERB("MIDI: CC %d = %d", msg->data1, msg->data2);
            // CC handling — route to params
            break;

        case MIDI_PITCH_BEND:
            {
                int16_t bend = ((int16_t)msg->data2 << 7 | msg->data1) - 8192;
                DBG_VERB("MIDI: Bend %d", bend);
                // Apply pitch bend to CV
            }
            break;

        default:
            break;
    }
}

void midi_on_sysex(const SysExMsg* msg) {
    // Check for Arturia MicroBrute SysEx
    // Manufacturer: 0x00 0x20 0x6B
    // Device: 0x05
    if (msg->length >= 6 &&
        msg->data[1] == 0x00 &&
        msg->data[2] == 0x20 &&
        msg->data[3] == 0x6B &&
        msg->data[4] == 0x05) {

        uint8_t cmd = msg->data[5];
        DBG_INFO("MIDI: Arturia SysEx cmd=0x%02X", cmd);

        // TODO: Handle parameter set/get commands
    }
}

void midi_on_realtime(uint8_t status) {
    switch (status) {
        case MIDI_CLOCK:
            // External clock pulse (24 PPQN)
            break;
        case MIDI_START:
            sequencer_start();
            clock_start();
            break;
        case MIDI_CONTINUE:
            // Resume
            break;
        case MIDI_STOP:
            sequencer_stop();
            clock_stop();
            break;
    }
}
