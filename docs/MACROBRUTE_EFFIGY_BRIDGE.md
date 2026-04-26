# MACROBRUTE ↔ EFFIGY Bridge Protocol

**Status:** v1 draft (2026-04-26). Authoritative shared contract.
**Scope:** Defines the I²C peer-pairing protocol between the MACROBRUTE expander
(Raspberry Pi Pico WH, MicroPython) and the EFFIGY DSP module (Daisy Seed,
libDaisy C++). Both projects implement to this document.

---

## 1. Design principle

EFFIGY is a complete **standalone 24HP Eurorack audio + CV processing module**.
This protocol does not reduce that autonomy. When unpaired, EFFIGY runs entirely
from its own panel. When paired, MACROBRUTE adds a coordinated control surface
and reads exposed state — nothing more.

**Audio and fast CV never cross this bus.** All audio and audio-rate CV flow via
Eurorack 3.5mm jacks and patch cables. The I²C pair bus carries control,
slow CV (~100 Hz update rate), events, telemetry, and coordination only.

---

## 2. Hardware

### 2.1 Rear header

5-pin JST-XH on each module's rear, accessed with the case open (not panel-visible):

| Pin | Signal | MACROBRUTE side | EFFIGY side |
|-----|--------|-----------------|-------------|
| 1 | SDA | Pico GP2 (I²C1) | Daisy free I²C peripheral SDA (I2C1 is OLED on EFFIGY — use I2C2/3) |
| 2 | SCL | Pico GP3 (I²C1) | Daisy free I²C peripheral SCL |
| 3 | INT | Pico GP11 (input, pull-up) | Daisy GPIO (open-drain output, active-low) |
| 4 | +3.3V | Pico 3V3 (header pull-ups only) | not connected on EFFIGY side |
| 5 | GND | star ground | shared reference |

Cable: shielded twisted pair recommended, < 30 cm length.
Pull-ups: 4.7 kΩ on SDA and SCL to +3.3V, located on the MACROBRUTE side only.

### 2.2 Electrical

| Parameter | Value |
|-----------|-------|
| Bus speed | 100 kHz |
| Logic level | 3.3 V |
| INT polarity | active-low, open-drain |
| EFFIGY I²C role | target |
| EFFIGY I²C address | **0x42** |
| MACROBRUTE I²C role | controller |
| Heartbeat interval | 100 ms |
| Pair-loss timeout | 1 second of missing heartbeat polls |

---

## 3. Protocol semantics

### 3.1 Register file model

EFFIGY exposes a flat 256-byte register file. MACROBRUTE accesses it via
standard I²C "register pointer" semantics:

- **Write:** `START · ADDR(W) · REG · DATA[0..N] · STOP`
- **Read:**  `START · ADDR(W) · REG · RESTART · ADDR(R) · DATA[0..N] · STOP`

Endianness for multi-byte values: **little-endian**.
Strings: ASCII, NUL-padded to declared length.

### 3.2 INT-driven event delivery

EFFIGY drives INT low when `EVENT_COUNT` (0x60) > 0. MACROBRUTE responds:

1. Detect falling edge on GP11
2. Read `EVENT_COUNT`
3. Loop: read `EVENT_POP` (0x61) one event at a time until count = 0
4. Write `EVENT_CLEAR` (0x62) — EFFIGY releases INT

INT line is the only mechanism for asynchronous EFFIGY → MACROBRUTE messages.
Polling is reserved for parameter mirroring and telemetry refresh.

---

## 4. Register map (authoritative)

### 4.1 Device / pair management — 0x00–0x0F

| Addr | Name | R/W | Bytes | Description |
|------|------|-----|-------|-------------|
| 0x00 | DEVICE_ID        | r/o | 8 | `"EFFIGY1\0"` |
| 0x01 | FW_VERSION_MAJOR | r/o | 1 | |
| 0x02 | FW_VERSION_MINOR | r/o | 1 | |
| 0x03 | CAPABILITIES     | r/o | 4 | bitfield: bit0=has_granular, bit1=has_reverb, bit2=has_quantizer, bit3=has_euclidean, bit4=has_cv_out, bit5=has_preset_recall |
| 0x0F | HEARTBEAT        | r/o | 1 | monotonic counter, +1 every 100 ms |

### 4.2 Parameter control (controller writes) — 0x10–0x3F

| Addr | Name | R/W | Bytes | Description |
|------|------|-----|-------|-------------|
| 0x10 | MASS              | r/w | 2 | u16 0–65535 |
| 0x11 | ENTROPY           | r/w | 2 | u16 |
| 0x12 | POSITION          | r/w | 2 | u16 |
| 0x13 | TEXTURE           | r/w | 2 | u16 |
| 0x14 | MIX               | r/w | 2 | u16 dry/wet |
| 0x15 | FOLD              | r/w | 2 | u16 |
| 0x16 | FILTER            | r/w | 2 | u16 cutoff |
| 0x17 | REVERB            | r/w | 2 | u16 wet send |
| 0x18 | CRUSH             | r/w | 2 | u16 |
| 0x19 | DESTRUCTION_MACRO | r/w | 2 | u16 overall wet |
| 0x1A | ENGINE_INDEX      | r/w | 1 | 0…N synthesis engine selector |
| 0x1B | HARMONIZER_INT    | r/w | 1 | interval index |
| 0x1C | MICRO_LFO_RATE    | r/w | 2 | u16 |
| 0x1D | ENV_SHAPE         | r/w | 1 | 0–3 curve preset |
| 0x30 | TRIG_VOICE_1      | w/o | 1 | write 0x01 to retrigger envelope |
| 0x31 | FREEZE            | r/w | 1 | 0=off, 1=on |
| 0x32 | PANEL_OVERRIDE    | r/w | 1 | 0=accept remote writes, 1=panel-only |

### 4.3 State telemetry (controller reads) — 0x40–0x5F

| Addr | Name | R/W | Bytes | Description |
|------|------|-----|-------|-------------|
| 0x40 | LEVEL_L            | r/o | 1  | 0–255 peak meter |
| 0x41 | LEVEL_R            | r/o | 1  | 0–255 |
| 0x42 | CLIP_FLAGS         | r/o | 1  | bit0=L, bit1=R |
| 0x43 | ENGINE_NAME        | r/o | 12 | ASCII current engine |
| 0x44 | PRESET_SLOT        | r/o | 1  | 0–7 active slot |
| 0x45 | CPU_LOAD           | r/o | 1  | 0–100 % |
| 0x46 | GRAIN_BUFFER_FILL  | r/o | 1  | 0–100 % |
| 0x47 | FREEZE_STATE       | r/o | 1  | 0=off, 1=on, 2=transitioning |
| 0x48 | ENV_STAGE          | r/o | 1  | 0=idle, 1=A, 2=S, 3=R |
| 0x49 | CV_OUT_1_VALUE     | r/o | 2  | s16 virtual readback |
| 0x4A | CV_OUT_2_VALUE     | r/o | 2  | s16 |

### 4.4 Event queue — 0x60–0x7F

| Addr | Name | R/W | Bytes | Description |
|------|------|-----|-------|-------------|
| 0x60 | EVENT_COUNT | r/o | 1 | pending events |
| 0x61 | EVENT_POP   | r/o | 4 | dequeue one: `{type, a, b, c}` |
| 0x62 | EVENT_CLEAR | w/o | 1 | write any value to deassert INT after drain |

**Event types:**

| Type | Name | a | b | c |
|------|------|---|---|---|
| 0x01 | ENCODER | signed delta | — | — |
| 0x02 | BUTTON | btn_id (0=FRZ, 1=PAGE, 2=encoder push) | 1=down, 0=up | — |
| 0x03 | PRESET | new slot 0–7 | — | — |
| 0x04 | ENGINE | new engine index | — | — |
| 0x05 | CLIP | flags (bit0=L, bit1=R) | — | — |
| 0x06 | PANEL | param register address | new value LSB | new value MSB |

PANEL events propagate user-driven parameter changes (knob turns on EFFIGY's
own panel) to MACROBRUTE so its mirror stays current.

### 4.5 Routing / coordination — 0x80–0x9F

| Addr | Name | R/W | Bytes | Description |
|------|------|-----|-------|-------------|
| 0x80 | PAIR_ACTIVE      | r/w | 1 | 1=paired, 0=solo |
| 0x81 | CLOCK_MASTER     | r/w | 1 | 0=MACROBRUTE owns clock, 1=EFFIGY owns clock |
| 0x82 | MENU_OWNER       | r/w | 1 | 0=MACROBRUTE shows main menu, 1=EFFIGY shows main menu |
| 0x83 | FOCUS_OWNER      | r/w | 1 | 0=MACROBRUTE encoder drives, 1=EFFIGY encoder drives |
| 0x90 | CLOCK_TICK       | w/o | 1 | any write = clock edge from controller |
| 0x91 | CLOCK_BPM        | r/w | 2 | u16, BPM × 10 (e.g. 1280 = 128.0 BPM) |
| 0x92 | TRANSPORT_STATE  | r/w | 1 | 0=stop, 1=play, 2=pause |
| 0x93 | PRESET_RECALL    | w/o | 1 | 0–7 triggers preset load |

### 4.6 Cross-modulation bridge — 0xA0–0xBF

| Addr | Name | R/W | Bytes | Description |
|------|------|-----|-------|-------------|
| 0xA0 | SRC_COUNT        | r/o | 1 | named mod source count |
| 0xA1–0xAF | SRC_NAME[i] | r/o | 8 | ASCII names (CV_OUT_1, MASS, ENV_STAGE, …) |

### 4.7 Diagnostics — 0xF0–0xFF

| Addr | Name | R/W | Bytes | Description |
|------|------|-----|-------|-------------|
| 0xF0 | ERROR_STATUS  | r/o | 1 | last bridge error code (0=OK) |
| 0xFF | RESET_BRIDGE  | w/o | 1 | resets pair state, clears events |

**Error codes:** 0=OK, 1=invalid_register, 2=write_to_readonly,
3=value_out_of_range, 4=panel_locked, 5=protocol_error.

---

## 5. Pair negotiation sequence

1. Both modules boot and initialise in solo mode (`PAIR_ACTIVE=0`).
2. MACROBRUTE probes 0x42. If the slave ACKs, MACROBRUTE reads `DEVICE_ID` (0x00).
3. If `DEVICE_ID == "EFFIGY1"`, MACROBRUTE writes `PAIR_ACTIVE=1` (0x80) and sets
   default role ownership:
   - `CLOCK_MASTER = 0` (MACROBRUTE owns timing — it bridges to MicroBrute)
   - `MENU_OWNER = 1` (EFFIGY shows the richer main menu — bigger feature surface)
   - `FOCUS_OWNER = 1` (EFFIGY encoder drives initially)
4. Both modules update their own UI to reflect paired state.
5. MACROBRUTE polls `HEARTBEAT` (0x0F) every 500 ms. Two consecutive identical
   reads → pair-loss; revert to solo, clear local mirror state.

User can change role ownership at any time via either module's menu by writing
to 0x81 / 0x82 / 0x83.

---

## 6. Implementation notes

### 6.1 MACROBRUTE side (Pico WH, MicroPython)

- Module: `firmware/pico/effigy_bridge.py`
- I²C bus: `I2C(1, sda=Pin(2), scl=Pin(3), freq=100_000)`
- INT pin: `Pin(11, Pin.IN, Pin.PULL_UP)` with falling-edge IRQ
- Pull-ups: physical 4.7 kΩ on SDA and SCL to 3V3 — required even though Pico
  has internal pull-ups, because the Daisy side may not.
- All register addresses defined as module-level constants with the same
  numeric values as the EFFIGY C header.
- Parameter writes are non-blocking (queued). Reads are blocking but bounded
  by the 100 kHz bus speed — a 12-byte `ENGINE_NAME` read is ~1.2 ms.

### 6.2 EFFIGY side (Daisy Seed, libDaisy C++)

- Header: `src/macrobrute_bridge.h` (register constants)
- Implementation: `src/macrobrute_bridge.cpp`
- I²C peripheral: I2C2 or I2C3 (I2C1 is reserved for the panel OLED)
- Slave mode: `daisy::I2CHandle::Config::Mode::I2C_SLAVE` at address 0x42
- Register file: `uint8_t registers_[256]` with appropriate guards for
  read-only, write-only, and reserved regions
- Event queue: circular buffer, bounded depth (16 events). Overflow drops
  oldest, sets `ERROR_STATUS = 5`.
- DSP-side parameter application (param register → actual engine state) is a
  separate layer; the bridge only maintains the register file.
- INT pin: open-drain output, default high. Asserted low when event count > 0.

### 6.3 Versioning

Increment `FW_VERSION_MINOR` for backward-compatible additions (new register,
new event type, new error code). Increment `FW_VERSION_MAJOR` for breaking
changes (renumbered register, removed register, changed semantics).

Both sides verify version compatibility on probe. Major mismatch → MACROBRUTE
displays "EFFIGY incompatible" and stays in solo mode.

---

## 7. What this protocol does NOT do

- **Audio.** Audio flows via Eurorack jacks. EFFIGY's stereo IN and OUT are
  cabled to wherever the rack wants. Even at 1 MHz I²C (well above the 100 kHz
  spec'd here), this bus cannot move audio.
- **Audio-rate CV.** CV signals above ~100 Hz must be patched physically.
  Slow CV (LFO at < 10 Hz, envelope contours, macro sweeps) can travel via
  parameter writes at the 100 Hz update rate.
- **Timing-critical clock distribution.** The `CLOCK_TICK` register exists for
  coarse phase alignment, but a hardware patch from MACROBRUTE clock-out to
  EFFIGY's CLK input jack remains the canonical way to share clock with sub-ms
  jitter. I²C clock ticks are best-effort.
- **Bulk preset transfer.** Presets remain local to each module's flash. The
  protocol coordinates *recall* (0x93) but does not stream preset data over
  the bus.

---

## 8. Reference: opposing-side companions

This document is mirrored on the EFFIGY side as
`EFFIGY/docs/MACROBRUTE_BRIDGE_ADOPTION.md` (when produced). Both sides
maintain the same register map; the C and Python constant headers must agree
numerically. Drift is an integration bug.
