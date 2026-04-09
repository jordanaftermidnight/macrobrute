#ifndef MIDI_HANDLER_H
#define MIDI_HANDLER_H

#include "midi_parser.h"

// Initialize MIDI message handlers
void midi_handler_init(void);

// Handlers (registered with parser)
void midi_on_message(const MidiMsg* msg);
void midi_on_sysex(const SysExMsg* msg);
void midi_on_realtime(uint8_t status);

#endif // MIDI_HANDLER_H
