/*
 * MIDI byte stream parser
 * Handles running status, SysEx, and realtime interleaving
 */

#include "midi_parser.h"
#include "utils/debug.h"

typedef enum {
    PARSE_IDLE,
    PARSE_STATUS,
    PARSE_DATA1,
    PARSE_DATA2,
    PARSE_SYSEX
} ParseState;

static ParseState state = PARSE_IDLE;
static MidiMsg current_msg;
static SysExMsg sysex_buf;
static uint8_t running_status = 0;

static midi_msg_cb msg_cb = NULL;
static midi_sysex_cb sysex_cb = NULL;
static midi_realtime_cb rt_cb = NULL;

static uint8_t expected_data_bytes(uint8_t status) {
    switch (status & 0xF0) {
        case MIDI_NOTE_OFF:
        case MIDI_NOTE_ON:
        case MIDI_POLY_PRESSURE:
        case MIDI_CC:
        case MIDI_PITCH_BEND:
            return 2;
        case MIDI_PROGRAM:
        case MIDI_CHAN_PRESSURE:
            return 1;
        default:
            return 0;
    }
}

int midi_parser_init(void) {
    state = PARSE_IDLE;
    running_status = 0;
    sysex_buf.length = 0;
    DBG_INFO("MIDI parser: ready");
    return 0;
}

void midi_parser_feed(uint8_t byte) {
    // Realtime messages can appear anywhere — handle immediately
    if (byte >= 0xF8) {
        DBG_VERB("MIDI: realtime 0x%02X", byte);
        if (rt_cb) rt_cb(byte);
        return;
    }

    // Status byte?
    if (byte & 0x80) {
        if (byte == MIDI_SYSEX_START) {
            state = PARSE_SYSEX;
            sysex_buf.length = 0;
            sysex_buf.data[sysex_buf.length++] = byte;
            return;
        }

        if (byte == MIDI_SYSEX_END) {
            if (state == PARSE_SYSEX) {
                sysex_buf.data[sysex_buf.length++] = byte;
                DBG_VERB("MIDI: SysEx complete (%d bytes)", sysex_buf.length);
                if (sysex_cb) sysex_cb(&sysex_buf);
            }
            state = PARSE_IDLE;
            return;
        }

        // Channel message status
        current_msg.status = byte & 0xF0;
        current_msg.channel = byte & 0x0F;
        running_status = byte;

        if (expected_data_bytes(byte) > 0) {
            state = PARSE_DATA1;
        } else {
            state = PARSE_IDLE;
        }
        return;
    }

    // Data byte
    switch (state) {
        case PARSE_SYSEX:
            if (sysex_buf.length < SYSEX_MAX_LEN) {
                sysex_buf.data[sysex_buf.length++] = byte;
            }
            break;

        case PARSE_IDLE:
            // Running status
            if (running_status) {
                current_msg.status = running_status & 0xF0;
                current_msg.channel = running_status & 0x0F;
                current_msg.data1 = byte;
                if (expected_data_bytes(running_status) == 1) {
                    DBG_VERB("MIDI: %02X %02X (running)", current_msg.status, current_msg.data1);
                    if (msg_cb) msg_cb(&current_msg);
                } else {
                    state = PARSE_DATA2;
                }
            }
            break;

        case PARSE_DATA1:
            current_msg.data1 = byte;
            if (expected_data_bytes(running_status) == 1) {
                DBG_VERB("MIDI: %02X %02X", current_msg.status, current_msg.data1);
                if (msg_cb) msg_cb(&current_msg);
                state = PARSE_IDLE;
            } else {
                state = PARSE_DATA2;
            }
            break;

        case PARSE_DATA2:
            current_msg.data2 = byte;
            DBG_VERB("MIDI: %02X %02X %02X", current_msg.status, current_msg.data1, current_msg.data2);
            if (msg_cb) msg_cb(&current_msg);
            state = PARSE_IDLE;
            break;

        default:
            break;
    }
}

void midi_set_msg_callback(midi_msg_cb cb) { msg_cb = cb; }
void midi_set_sysex_callback(midi_sysex_cb cb) { sysex_cb = cb; }
void midi_set_realtime_callback(midi_realtime_cb cb) { rt_cb = cb; }
