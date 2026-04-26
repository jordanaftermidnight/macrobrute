> ⚠️ **DEPRECATED — superseded by current docs.** This file reflects an
> earlier iteration (different connector, expander HP, or pin map). Kept
> for historical reference only. See `README.md`, `docs/MACROBRUTE_BUILD_PLAN.md`,
> and `docs/MACROBRUTE_CONNECTION_MAP.md` for the current authoritative spec.

# MACROBRUTE Revised Specification

**Last Updated:** April 2026  
**Status:** Planning → Prototyping

---

## CURRENT HARDWARE (In Hand / Ordered)

| Item | Status | Notes |
|------|--------|-------|
| MicroBrute | ✓ Owned | Target synth |
| Pico H | ✓ Bought | Main expansion controller |
| Arduino Nano | ✓ Bought | Secondary brain (ADC, expansion) |
| PL2303HX USB-TTL | ✓ Bought | For LPC2361 ISP |
| 1.3" OLED SPI/I²C 7-pin | ✓ Bought | Display (body mount) |
| 0.96" SSD1306 I²C | ✓ Ordered | Backup/alternative display |
| 2× DB-9 + connectors | ✓ Bought | 18 pins total for expander |
| IC kit (555, TL074, etc.) | ✓ Ordered | For expander circuits |
| 6U 84HP Eurorack case | ✓ Owned | For expander module |

---

## ARCHITECTURE DECISIONS (CONFIRMED)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Connector** | 2× DB-9 (18 pins) | What we have; forces prioritization |
| **Connector location** | Rear panel | Clean, accessible when racked |
| **Mod matrix** | PRESERVED | Keep stock functionality |
| **OLED location** | Body mount (TBD) | Right cheek or custom position |
| **Pico H location** | Inside MicroBrute | Near LPC2361, UART connection |
| **Nano role** | TBD | ADC, extra I/O, or dedicated function |

---

## CONNECTOR PINOUT: 2× DB-9 (18 Pins Total)

With only 18 pins, we prioritize **essential signals** that add the most value beyond stock.

### DB-9 A: Audio + Main CV (Rear Left)

| Pin | Signal | Direction | Notes |
|-----|--------|-----------|-------|
| 1 | **Pitch CV Out** | → Expander | 1V/Oct (stock provides this) |
| 2 | **Gate Out (Buffered)** | → Expander | Must buffer TP83 (weak) |
| 3 | **VCO Mix Out** | → Expander | TP30 — pre-filter tap (NEW) |
| 4 | **VCF Out** | → Expander | TP19 — post-filter tap (NEW) |
| 5 | **Saw Out** | → Expander | TP94 via 1kΩ (NEW) |
| 6 | **Square Out** | → Expander | TP93 via 1kΩ (NEW) |
| 7 | **Sub Out** | → Expander | TP102 via 1kΩ (NEW) |
| 8 | **GND** | ⏚ | |
| 9 | **GND** | ⏚ | |

### DB-9 B: CV Inputs + Power (Rear Right)

| Pin | Signal | Direction | Notes |
|-----|--------|-----------|-------|
| 1 | **Filter CV In** | ← Expander | U8A summing node via 220kΩ |
| 2 | **VCA CV In** | ← Expander | TP10/11, 0-5V |
| 3 | **Sync In** | ← Expander | VCO hard sync |
| 4 | **Clock Out** | → Expander | From Pico H |
| 5 | **Clock In** | ← Expander | To Pico H (external sync) |
| 6 | **Gate In** | ← Expander | External gate/trigger |
| 7 | **+12V** | ⏚ | Power to expander |
| 8 | **-12V** | ⏚ | Power to expander |
| 9 | **GND** | ⏚ | |

### Signal Summary

| Direction | Count |
|-----------|-------|
| MB → Expander (outputs) | 8 |
| Expander → MB (inputs) | 4 |
| Bidirectional (clock) | 2 |
| Power/Ground | 4 |
| **Total** | **18** |

### What's NOT Included (Use Stock/Mod Matrix)

| Signal | Where to Access |
|--------|-----------------|
| Envelope Out | Mod matrix (stock) |
| LFO Out | Mod matrix (stock) |
| Pitch In (CV) | Rear panel (stock) |
| Gate In | Rear panel (stock) — also on DB-9 |
| Ext Audio In | Rear panel (stock) |
| Main L/R Out | Rear panel (stock) |
| Triangle, Metalizer, Ultrasaw | Future expansion or body taps |

---

## WHAT'S ON THE MICROBRUTE BODY

### OLED + Controls

| Component | Location | Connection |
|-----------|----------|------------|
| 1.3" OLED | Right cheek (TBD) | SPI/I²C to Pico H (4-5 wires) |
| Button 1 | Near OLED | GPIO to Pico H |
| Button 2 | Near OLED | GPIO to Pico H |

**Possible OLED functions:**
- Clock BPM display
- Pattern/sequence info (if firmware cracked)
- Mode indicator
- Tuner (via audio input to Nano ADC?)

### Potential Body-Mount Touch Points

| Signal | Location Idea | Notes |
|--------|---------------|-------|
| Metalizer Out | Left cheek | 3.5mm jack |
| Triangle Out | Left cheek | 3.5mm jack |
| VCF Insert S/R | Left cheek | 2× 3.5mm jacks |

These don't go through DB-9 — wired directly inside body.

---

## EURORACK EXPANDER (Scaled Down)

With 18-pin connector, expander scope is reduced but still useful:

### Signals Received from MB (7)

| Jack | Signal |
|------|--------|
| Pitch CV Out | Buffered on expander |
| Gate Out | From buffered source |
| VCO Mix Out | Pre-filter audio |
| VCF Out | Post-filter audio |
| Saw Out | Raw waveform |
| Square Out | Raw waveform |
| Sub Out | Sub oscillator |

### Signals Sent to MB (4)

| Jack | Signal |
|------|--------|
| Filter CV In | With attenuator pot |
| VCA CV In | With attenuator pot |
| Sync In | VCO hard sync |
| Gate In | External trigger |

### Clock Section

| Jack | Signal |
|------|--------|
| Clock Out | From Pico (to Eurorack) |
| Clock In | From Eurorack (to Pico) |

### Expander-Generated Utilities (No MB Connection Needed)

| Utility | How |
|---------|-----|
| Clock ÷2, ÷4, ÷8 | CD4024 fed by Clock Out |
| White Noise | 2N3904 + TL072 |
| LFO (Tri/Sqr) | TL072 oscillator |
| S&H | CD4066 + noise + clock |
| Manual Gate | Button |

### Revised Panel Size

With reduced I/O: **20-30HP** could be enough instead of 84HP.

```
┌────────────────────────────────────────────────┐
│          MACROBRUTE EXPANDER · 24HP             │
├────────────────────────────────────────────────┤
│                                                │
│  OUTPUTS        INPUTS         UTILITIES       │
│  ┌───┐┌───┐    ┌───┐┌───┐    ┌───┐┌───┐      │
│  │PCH││GAT│    │FLT││VCA│    │CLK││÷2 │      │
│  └───┘└───┘    │ ○ ││ ○ │    └───┘└───┘      │
│  ┌───┐┌───┐    └───┘└───┘    ┌───┐┌───┐      │
│  │MIX││VCF│    ┌───┐┌───┐    │÷4 ││÷8 │      │
│  └───┘└───┘    │SYN││G.I│    └───┘└───┘      │
│  ┌───┐┌───┐    └───┘└───┘    ┌───┐┌───┐      │
│  │SAW││SQR│                   │LFO││NOI│      │
│  └───┘└───┘    CLK I/O       └───┘└───┘      │
│  ┌───┐         ┌───┐┌───┐    ┌───┐           │
│  │SUB│         │OUT││ IN│    │S&H│  ○ Rate   │
│  └───┘         └───┘└───┘    └───┘           │
│                                                │
│        [══ DB-9 A ══]  [══ DB-9 B ══]         │
│                                                │
└────────────────────────────────────────────────┘
```

---

## MULTI-BRAIN ARCHITECTURE

### Inside MicroBrute

```
┌─────────────────────────────────────────────────────┐
│                   MICROBRUTE                        │
│                                                     │
│  ┌────────────┐   UART?   ┌────────────┐           │
│  │  LPC2361   │◄─ ─ ─ ─ ─►│  Pico H    │           │
│  │  (Stock)   │  Unknown  │            │           │
│  │            │           │ • OLED     │           │
│  │ • Keyboard │           │ • Buttons  │───► Body  │
│  │ • Sequencer│           │ • Clock    │           │
│  │ • MIDI     │           │            │           │
│  └────────────┘           └─────┬──────┘           │
│                                 │                   │
│                           ┌─────▼──────┐           │
│                           │   Nano     │  Optional │
│                           │ • ADC      │  second   │
│                           │ • Extra IO │  brain    │
│                           └────────────┘           │
│                                                     │
│  Analog Path: VCO → Animator → Mixer → VCF → VCA  │
│       ↓ taps                            ↓ inject   │
└───────┼────────────────────────────────┼───────────┘
        │          DB-9 A + B            │
        └────────────────────────────────┘
                      │
              ════════╧════════
                   CABLE
              ════════╤════════
                      │
┌─────────────────────┼─────────────────────────────┐
│  EURORACK EXPANDER  │                             │
│         ┌───────────┴───────────┐                 │
│         │  Buffers + Utilities  │                 │
│         └───────────────────────┘                 │
└───────────────────────────────────────────────────┘
```

### Pico H Responsibilities

| Function | Status |
|----------|--------|
| OLED display driver | Ready to implement |
| Button input | Ready to implement |
| Clock generation (standalone) | Ready to implement |
| Clock IN detection | Ready to implement |
| Clock OUT signal | Ready to implement |
| LPC2361 UART comms | UNKNOWN — needs investigation |

### Nano Responsibilities (TBD)

| Possible Role | Value |
|---------------|-------|
| Read CV from Eurorack (ADC) | Medium — Pico has 3 ADC too |
| Extra gate outputs | Low — Pico has enough GPIO |
| MIDI DIN processing | Medium — if offloading from Pico |
| Dedicated clock processor | Low — Pico handles this |
| Audio-rate processing | No — not fast enough |

**Verdict:** Nano may not be needed. Keep it for experiments.

---

## FIRMWARE INVESTIGATION (LPC2361)

### What We Know

| Aspect | Status |
|--------|--------|
| ISP pins | P0.0 (RX), P0.1 (TX), P0.14 (ISP enable) |
| ISP tool | lpc21isp |
| Baud rate | 115200 typical |
| CRP status | UNKNOWN — must probe |
| JTAG | Possibly available — check schematics |

### First Steps

1. **Connect PL2303HX** — verify serial connection
2. **Check CRP** — try to read device ID
3. **If locked** — assess bypass options (probably none)
4. **If unlocked** — dump firmware for analysis

### If Firmware Is Accessible

Potential mods:
- Expose clock as CV/gate output
- Custom sequencer behavior
- Different MIDI mappings
- Pico ↔ LPC2361 communication protocol

### If Firmware Is Locked (Likely)

Pico H operates independently:
- Standalone clock (not synced to MB sequencer)
- OLED shows Pico-generated info only
- No integration with MB sequencer/arp

---

## PHASED BUILD PLAN

### Phase 0: Verify (NOW)

| Task | Tool |
|------|------|
| Open MicroBrute, photograph PCBs | Camera |
| Probe test points with multimeter | Multimeter |
| Wire Pico H + OLED, test display | Breadboard |
| Connect PL2303HX, check LPC2361 | Terminal |

### Phase 1: Basic Taps (Non-Destructive)

| Mod | Difficulty |
|-----|------------|
| Wire TP94 (Saw) via 1kΩ to DB-9 | Easy |
| Wire TP93 (Square) via 1kΩ to DB-9 | Easy |
| Wire TP102 (Sub) via 1kΩ to DB-9 | Easy |
| Buffer TP83 (Gate) with CD40106 | Easy |
| Wire TP19 (VCF Out) via 1kΩ to DB-9 | Easy |

### Phase 2: CV Inputs

| Mod | Difficulty |
|-----|------------|
| Wire Filter CV to summing node | Medium |
| Wire VCA CV to TP10/11 | Easy |
| Wire Sync to VCO | Medium |

### Phase 3: Expander Build

| Task | Scope |
|------|-------|
| Design 24HP panel | Reduced from 84HP |
| Build buffer board | TL074 × 2 |
| Build utility section | LFO, noise, clock div |
| Wire DB-9 connectors | Panel mount |

### Phase 4: Integration

| Task | Depends On |
|------|------------|
| Pico clock ↔ expander | Phase 3 |
| OLED display finalization | Body mounting decision |
| LPC2361 integration | Firmware investigation |

---

## OPEN QUESTIONS

1. **OLED exact mount location?** — Need to measure MicroBrute body
2. **Nano role?** — May not be needed; keep for experiments
3. **Body-mount jacks?** — Metalizer, Triangle, inserts on left cheek?
4. **Expander panel size?** — 24HP enough? Or 12HP minimal?
5. **LPC2361 CRP status?** — Determines integration depth

---

## DOCUMENTS TO UPDATE

| Document | Change Needed |
|----------|---------------|
| MACROBRUTE_COMPLETE_EXPANSION_MAP.md | Connector section obsolete |
| MACROBRUTE_BOM.md | Reduce to 18-pin scope |
| MACROBRUTE_MASTER_PLAN.md | Update architecture |

---

## NEXT ACTIONS

1. ☐ Open MicroBrute, photograph PCBs
2. ☐ Probe key test points (TP83, TP94, TP19)
3. ☐ Wire Pico H + 1.3" OLED on breadboard
4. ☐ Connect PL2303HX to LPC2361, check response
5. ☐ Decide OLED body mount location
6. ☐ Decide on body-mount jacks (if any)
