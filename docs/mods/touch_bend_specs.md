# MACROBRUTE Touch Bend Specifications

8 body-contact circuit bends for the Arturia MicroBrute, optimized for
industrial/techno performance. Touch brass bolts on the panel to modify
sound in real-time via body capacitance and resistance.

---

## Touch Mod Table

| # | Name | PCB Point | Safety R | Effect | Intensity | Risk | Techno |
|---|------|-----------|----------|--------|-----------|------|--------|
| 1 | Pitch Shimmer | R309 area (near blue trimmers, rear board) | 10k | Analog pitch vibrato/detune via body capacitance | 4/5 | 1/5 | 5/5 |
| 2 | Metalizer Crunch | C111 (wavefolder stage 3) | 4.7k | Sweeps harmonic folding intensity | 5/5 | 2/5 | 5/5 |
| 3 | Filter Wah | Filter CV input area (Steiner-Parker cutoff) | 22k | Manual filter sweep, overrides LFO | 4/5 | 2/5 | 5/5 |
| 4 | Brute Distortion | Feedback path (Brute Factor circuit) | 15k | Variable feedback: clean to aggressive self-oscillation | 5/5 | 3/5 | 5/5 |
| 5 | Envelope Decay | ADSR decay timing cap area | 33k | Pluck-to-swell morphing, changes decay time | 3/5 | 1/5 | 4/5 |
| 6 | Dual Harmonic Morph | C107 + C106 (wavefolder stages 1 & 2, two bolts) | 10k each | Cross-coupled folding stages, touch both for complex harmonics | 5/5 | 2/5 | 5/5 |
| 7 | LFO Speed Throb | LFO timing resistor network | 47k | Manual tremolo/vibrato speed control | 3/5 | 1/5 | 4/5 |
| 8 | Metalizer Feedback Gate | Metalizer output to input (series connection) | 1k | Touch closes feedback loop: industrial harmonic chaos | 5/5 | 4/5 | 5/5 |

**Recommended top 6 for panel:** 1, 2, 3, 4, 6, 8 (all rated 5/5 techno utility)

---

## Wiring Diagram

Each touch bolt:
```
MicroBrute PCB point ──[safety R]──┬── Brass bolt (panel mount)
                                    │
                            (body contact)
                                    │
                                   GND (via skin resistance ~10k-1M)
```

For dual-point bends (mod 6), two separate bolts wire to different
circuit points. Touching both simultaneously creates cross-coupling
through your body.

For feedback gate (mod 8), the circuit is:
```
Metalizer output ──[1k]── Brass bolt A
                            │
                     (touch to close)
                            │
Metalizer input  ──[1k]── Brass bolt B
```

---

## Test Protocol

1. Build the touch test board (`schematics/touch_test_board.svg`)
2. Wire each channel to the MicroBrute via clip leads (non-destructive)
3. Probe dry-fingered at 50% touch pressure — document effect onset
4. Increase to full pressure for dynamic range
5. Repeat with slightly damp finger to map moisture sensitivity
6. Record 10-second audio clip per mod (baseline + touch effect)
7. Rate musical usefulness vs stability/predictability
8. Select top 6 for permanent panel installation

---

## Safety Notes

- All points connect to signal-level circuits (max +/-12V), not power rails or CPU
- Higher risk mods (4, 6, 8) involve feedback coupling -- test thoroughly
  with dry fingers before wet-touch experiments
- Moisture increases body conductivity: effects become stronger and less
  predictable with damp fingers
- Optional: add 100pF cap in parallel with safety R to limit HF transients
- B1M pot in series allows variable touch sensitivity (use during testing)

---

## Panel Installation

After testing, select 6 mods for permanent panel bolts:
- Drill 6x 6mm holes in bottom-left panel area (below mod wheel)
- Insert brass M3 bolts from outside, nut on inside
- Solder wire from bolt to safety resistor to PCB point
- Label each bolt on panel (PITCH, CRUNCH, WAH, DISTORT, HARMONIC, GATE)
- Spacing: 15mm horizontal between bolts to avoid accidental multi-touch

---

## Sources

- Yusynth MicroBrute schematics: https://hackabrute.yusynth.net
- Maffez Pedrobrute: https://maffez.com/?page_id=2285
- ModWiggler MicroBrute thread: https://modwiggler.com/forum/viewtopic.php?t=152071
- Project circuit bending guide: docs/mods/microbrute_circuit_bending_guide.md
