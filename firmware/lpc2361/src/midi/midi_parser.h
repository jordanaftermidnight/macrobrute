#ifndef MIDI_PARSER_H
#define MIDI_PARSER_H

#include <stdint.h>

// MIDI message types
#define MIDI_NOTE_OFF       0x80
#define MIDI_NOTE_ON        0x90
#define MIDI_POLY_PRESSURE  0xA0
#define MIDI_CC             0xB0
#define MIDI_PROGRAM        0xC0
#define MIDI_CHAN_PRESSURE   0xD0
#define MIDI_PITCH_BEND     0xE0
#define MIDI_SYSEX_START    0xF0
#define MIDI_SYSEX_END      0xF7
#define MIDI_CLOCK          0xF8
#define MIDI_START           0xFA
#define MIDI_CONTINUE       0xFB
#define MIDI_STOP           0xFC

// Parsed MIDI message
typedef struct {
    uint8_t status;
    uint8_t channel;
    uint8_t data1;
    uint8_t data2;
} MidiMsg;

// SysEx buffer
#define SYSEX_MAX_LEN 128

typedef struct {
    uint8_t data[SYSEX_MAX_LEN];
    uint16_t length;
} SysExMsg;

// Callbacks
typedef void (*midi_msg_cb)(const MidiMsg* msg);
typedef void (*midi_sysex_cb)(const SysExMsg* msg);
typedef void (*midi_realtime_cb)(uint8_t status);

int midi_parser_init(void);

// Feed raw bytes from UART
void midi_parser_feed(uint8_t byte);

// Register callbacks
void midi_set_msg_callback(midi_msg_cb cb);
void midi_set_sysex_callback(midi_sysex_cb cb);
void midi_set_realtime_callback(midi_realtime_cb cb);

#endif // MIDI_PARSER_H
