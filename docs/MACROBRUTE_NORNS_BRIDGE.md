# MACROBRUTE ↔ Norns Shield Bridge — design placeholder

> **Status:** anticipated, not implemented. This file is a stub that
> reserves the design space and pins down the open questions. No code
> exists yet on either side.

## Why this exists

A planned third module — a custom Eurorack build of the **monome Norns
Shield** (Raspberry Pi 3B+ + audio HAT + monome software stack) — will join
the rack as a network-connected scripting brain and Ableton Link node.

EFFIGY's `firmware/FIRMWARE_SPEC.md §13.8` documents the topology from
EFFIGY's side. The MACROBRUTE-side responsibilities live here.

## Topology (chained, not meshed)

```
[Wi-Fi / Ableton Link peers]
            │
            ▼
       NORNS (ii bus controller, Lua + SC, Link clock)
            │  ii bus (front-of-rack header)
            ▼
     MACROBRUTE (ii target on Norns bus + pair-bus controller for EFFIGY)
            │  pair bus (rear JST-XH, EFFIGY register map)
            ▼
       EFFIGY (I²C target at 0x42 — pair bus only)
```

EFFIGY does not change. MACROBRUTE absorbs the translator role.

## What MACROBRUTE owns

| Responsibility | Status |
|----------------|--------|
| Second I²C peripheral in target mode (ii bus to Norns) | 🟡 not implemented |
| ii-compatible target interface (monome convention) | 🟡 not implemented |
| ii address allocation (suggested 0x60) | 🟡 reserve later |
| Command translator: ii → local state OR → EFFIGY register write | 🟡 not implemented |
| Link clock republisher (ii Link tick → pair-bus `CLOCK_TICK`/`CLOCK_BPM`) | 🟡 not implemented |
| Lua-side wrapper module conventions (`ii.macrobrute.*`) | 🟡 not specified |

## Hardware-level conflict to resolve

RP2040 has only **two** hardware I²C peripherals:

| Peripheral | Currently used for |
|------------|--------------------|
| I²C0 (GP4/GP5) | Main OLED + strip OLED (shared bus, 0x3C / 0x3D) |
| I²C1 (GP2/GP3) | EFFIGY pair bus (target 0x42) |

Both are full. The ii target needs a third bus. Two viable options:

1. **PIO-driven I²C target** on spare GPIO. RP2040 PIO can implement an I²C
   target with no hardware peripheral. Cost: more firmware, slightly more
   CPU. Candidate pins: GP6/GP7 (currently aux outputs — would need to
   move aux 3/4 to other pins).
2. **Bus reassignment.** Move the OLEDs to PIO-bitbanged I²C and reclaim
   I²C0 for the ii target. Cost: rewriting the OLED driver path (which
   already runs at 100 kHz, so PIO is fine).

Option 1 is closer to non-breaking. Decide at Phase 7D start based on PIO
state-machine availability and how clean the libraries look at that point.

## ii address allocation (proposed)

| Address | Owner |
|---------|-------|
| 0x68 | Just Friends (reserved) |
| 0x69 | Teletype (reserved) |
| 0x70 | Crow (reserved) |
| 0x65–0x67 | W/ family (reserved) |
| 0x34 | Faderbank (reserved) |
| **0x60** | **MACROBRUTE — proposed** (clear of all reserved ranges) |

If anyone disputes the address, swap it. Unlike the EFFIGY pair bus
(frozen at 0x42 in the C header), MACROBRUTE's ii address can move.

## Translator command split (rough draft)

| ii command | Mapping | Target |
|-----------|---------|--------|
| `ii.macrobrute.bpm(120)` | local | MACROBRUTE clock subsystem |
| `ii.macrobrute.tap()` | local | MACROBRUTE tap-tempo register |
| `ii.macrobrute.aux(idx, mode, params)` | local | MACROBRUTE aux output config |
| `ii.macrobrute.effigy_set('mass', 0.5)` | proxy → I²C1 write | EFFIGY register `MASS` (0x10) |
| `ii.macrobrute.effigy_engine(idx)` | proxy → I²C1 write | EFFIGY register `ENGINE_INDEX` (0x1A) |
| `ii.macrobrute.effigy_preset(slot)` | proxy → I²C1 write | EFFIGY register `PRESET_RECALL` (0x93) |
| `ii.macrobrute.effigy_meter()` | proxy → I²C1 read | EFFIGY register `LEVEL_L`+`LEVEL_R` (0x40/0x41) |

The proxy layer is thin — Norns Lua scripts just see the same kind of
calls they make to Crow/W/JF. From EFFIGY's perspective, every write is
indistinguishable from a direct controller write.

## Pull-up topology when both buses are populated

| Bus | Pull-ups live on |
|-----|------------------|
| Front: ii to Norns | **Norns side** (Pi 3B+ has 1.8 kΩ on i2c-1; Norns is the master). MACROBRUTE side adds nothing. |
| Rear: pair to EFFIGY | **MACROBRUTE side** (4.7 kΩ to 3V3 on SDA + SCL). EFFIGY side adds nothing. |

Avoid stacking pull-ups when MACROBRUTE sits in the middle of both buses.

## Power notes (informational)

- Pi 3B+ peak draw is ~700 mA on +5V. Add Pico WH (~100 mA) and Daisy
  (~150 mA) and you're at ~950 mA on the +5V rail before any other
  modules. CP1A delivers 1 A on +5V — comfortable but tight if you stack
  more digital modules.
- Pi 3B+, Pico WH, and Daisy Seed all run 3.3V I²C. No level shifting
  needed for ii bus interop.

## Reference

- EFFIGY topology spec: `EFFIGY/firmware/FIRMWARE_SPEC.md §13.8`
- EFFIGY adoption notes: `EFFIGY/firmware/docs/MACROBRUTE_BRIDGE_ADOPTION.md`
- Pair bus contract (frozen): `docs/MACROBRUTE_EFFIGY_BRIDGE.md`
- monome ii ecosystem: <https://monome.org/docs/norns/> (ii namespace)
