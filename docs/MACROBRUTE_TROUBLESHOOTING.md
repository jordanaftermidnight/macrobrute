# MACROBRUTE Troubleshooting & Common Pitfalls

Real failure modes, organized by phase. Most of these come from
`schematics/CIRCUIT_REVIEW.md`, `docs/firmware/lpc2361_investigation_guide.md`,
and the Phase 0 bench-validation notes — collected here so you can spot
them before they bite.

If you hit something not on this page, check the original review docs;
they go deeper on the analog circuits.

---

## Phase 0 — Bench validation (Pico + breadboard)

### The OLED shows nothing

The main display is the 1.3″ 7-pin SPI OLED on SPI0, write-only: SCK GP2 (module D0),
MOSI GP3 (D1), DC GP4, RES GP5, CS GP11. SPI has no address and no scan, and the
firmware has no SPI driver yet (follow-up), so a blank screen before that driver lands
is expected.

**Fix:** check the module pin order against its silkscreen (UNVERIFIED; the common order
is GND, VCC, D0, D1, RES, DC, CS), that D0/D1 are not swapped, that RES is driven high
after reset and CS low while writing, then VCC and GND. If the picture is shifted by two
columns or shows a stripe at the edge, the chip is probably SH1106 (UNVERIFIED): set
`OLED_CHIP="SH1106"` and `OLED_COL_OFFSET=2` (BF Q22).

### KY-040 encoder reports two ticks per detent

The KY-040 module has on-board 10 kΩ pull-ups *and* the firmware enables
`Pin.PULL_UP` on GP13/14/15. That's intentional — without it the rotational
A/B sequence is too noisy on long jumper wires. Two-ticks-per-detent usually
means contact bounce on a worn or cheap encoder.

**Fix:** wire the optional 10 kΩ + 100 nF RC filter shown in
`schematics/pico_pinout.md` (Hardware Debounce section). Adds ~1 ms of lag,
kills the bounce.

### RGB LED is always lit — pin LOW makes it brighter

You probably have a **common-anode** RGB LED instead of common-cathode.
They look identical; only the long-lead position is different (CC: long lead
= cathode = GND; CA: long lead = anode = +3V3). With CA wired into a CC
firmware, pulling the GPIO LOW lights the LED.

**Fix:** verify the part with a multimeter (diode-test mode + the long lead
will be the common one). Either swap to a CC LED or invert the firmware
duty cycle in `firmware/pico/leds.py`.

### Centre-channel jumpers cross the Pico body

The Pico straddles the breadboard centre channel along its long axis. A
straight vertical drop from a top-edge pin to a bottom-row peripheral
pierces the Pico body. Use the drop columns shown in
`schematics/phase0_breadboard.svg` — the ones in the gap between the Pico
and the encoder/RGB blocks.

### Pico won't enumerate after firmware copy

If `main.py` raises an exception at boot, the Pico sometimes won't expose
the USB MicroPython filesystem. Hold **BOOTSEL** when plugging in to enter
the RP2 bootloader, then reflash MicroPython. Your `main.py` is preserved
on the FAT partition.

---

## Phase 1 — Breakout board build

### -12V rail measures +12V (or vice versa)

The protection diode on the -12V rail (an owned BAT85 or 1N5819, or a 1N5817 if one is
bought) must be installed with the **cathode toward the TP71 / -12 V header
side and the anode toward the breakout rail** (audit B15). The old text here
said the opposite. Installed the wrong way round, the diode blocks the normal
-12 V current and the V- pins float near 0 V.

**Fix:** check the band orientation on each diode before powering up. The band
marks the cathode: it goes to the -12 V (TP71) side. Multimeter diode-test
mode: probe red on the plain (anode) side and black on the band (cathode)
side, you should read the Schottky forward drop (BAT85 about 0.24 V at 0.1 mA,
0.4 V at 10 mA).

### TL074 outputs sit at +12V (or -12V) when no signal applied

The +IN pin is floating. The MicroBrute test points are AC-coupled at the
tap, so each op-amp +IN needs a DC bias path to GND.

**Fix:** add 10 MΩ from each `+IN` pin to GND (rows 8/10 in the breakout
layout). Sets the operating point at 0 V, doesn't load the high-impedance
test point. See CIRCUIT_REVIEW.md §2.

### Ferrite beads (FB1/FB2) burning hot

Ferrite beads are not part of the decided breakout power chain (they are not
owned; audit S20 and decision 8). If you did fit them, a bead's rating is an
impedance at 100 MHz, not a DC resistance, and cheap ones run hot at full
op-amp current. Omit the beads, or use 10 Ω in series with 2-4× 10 µF in
parallel where filtering is wanted (CM 5.3).

### TL074 audio sounds clipped or distorted at line-level

TL074 output current = 50 mA max. Driving a 600 Ω headphone = ~10 mA at
line level — fine. Driving a 32 Ω earbud = ~50 mA = at the edge. Driving
a 8 Ω speaker = blown op-amp.

**Fix:** ensure the breakout's outputs only feed line-level inputs. If you
need to drive headphones, use the TL072 follower at the destination, not
the TL074 directly.

---

## Phase 2 — Internal wiring

### Static pop / click when touching breakout board

ESD discharge through ungrounded fingers into the bias-resistor input.
Won't damage CMOS in the breakout (BAT54S clamps it) but it will pop the
audio output.

**Fix:** wear an antistatic wrist strap when working on the open synth, or
touch the chassis ground (TP72) before each session. Also: the touch bolts
are *deliberately* exposed — those will pop too, by design.

### Audio bleeding from one buffered output into another

Ground loop. TP72 is the MicroBrute-side star ground. Every DB-9 ground pin
and the breakout ground go to TP72 by their own short wires, not through the
breakout's ground strip and not via the MicroBrute's own ground rail.

**Fix:** verify your wiring against `MACROBRUTE_CONNECTION_MAP.md` section 11.
The rule is load-bearing: the DB-9 ground conductors (A:9; B:2, 4, 7, 8, 9) are the
ONLY ground connection between the synth and the rack.

### Test-point voltage on a multimeter is "noisy" / unstable

That's fine — most TPs are AC signals (waveform taps, LFO, etc.) and your
multimeter is averaging them poorly. Probe with an oscilloscope, not a
multimeter, for anything that's an audio or modulation signal. Use the
multimeter only for DC checks (TP70/71/72 = ±12V/-12V/GND).

---

## Phase 3 — Panel modifications (irreversible)

### Drilled hole is the wrong size for the jack/toggle

Always measure the *thread* of the part, not the body. A "6 mm" jack
typically has 6 mm threads but a 7 mm body — the panel hole needs to be
6.2–6.3 mm so the threads pass with clearance.

**Fix:** test-fit every part against a scrap of identical panel material
*before* drilling the synth. The provided `panel/microbrute_panel_template.svg`
shows tested hole diameters — print at 1:1 and pinprick the centres.

### Panel paint chips around the drilled hole

You drilled too fast or used a worn bit. The MicroBrute panel is anodized
aluminum, brittle on the surface.

**Fix:** mark the centre with a punch. Drill in stages: 2 mm pilot →
3 mm → 5 mm → final size. Keep RPM low (300-500), feed slow, use a sharp
HSS bit. A drop of cutting fluid helps.

### Touch bolt makes no sound when touched

Most likely either (a) you've isolated it with a track cut you didn't
mean to make, (b) the series safety resistor is too high (try 1 kΩ–10 kΩ
range), or (c) the bolt isn't electrically connected to anything bendable
(a "ground" bolt has nothing to bend — it just provides the return path).

**Fix:** with a multimeter on continuity, probe between the bolt and the
TP it's supposed to bend. You should see your safety resistor's value.
If you see open circuit, the wire's broken or the track's cut.

---

## Phase 5 — System integration (DB-9 cable)

### Audio sounds different through the expander vs. direct from synth

Expected: the A outputs are buffered on the MicroBrute side, and the expander
jacks are passive. Sound *should* be ~indistinguishable. If you hear hum, work
through the fallback ladder in `MACROBRUTE_CONNECTION_MAP.md` section 11 (BF 4.5),
in order, and measure after each step.

**Fix:** the shield rule is one end only: the braid is bonded to its connector
shell at the **MicroBrute end**, that shell is wired with a short lead to TP72,
and at the expander end the braid is cut back and insulated and the panel shell
is isolated from the aluminium panel (insulating shoulder washers, BF 4.2). A
molded off-the-shelf cable bonds the braid at both hoods and must be modified.
The ground conductors are terminated at both ends. The older advice here to
pick the expander end is replaced; swapping the bond to the expander end is
ladder step 3, to be tried only if hum persists. Never connect USB to the Pico
while the DB-9 cables are connected.

### Eurorack modules see noise / tick on +12V rail

The CP1A or other PSU is shared between expander + other Eurorack
modules. The expander's digital section (LFO Schmitt trigger) injects
edges onto +12V if not decoupled.

**Fix:** add 100 µF electrolytic + 100 nF ceramic across +12V/GND on the
expander board, near the noisy IC. The breakout has these by design;
expander often forgets them.

---

## Firmware (Pico + LPC2361)

### Pico USB-MIDI doesn't show up on the host

The TinyUSB stack inits during the first 100 ms of boot. If your host
opens the device too fast, it can race.

**Fix:** unplug, wait 2 s, replug. If still nothing, check `usbmidi.py`
is imported in `main.py` and the host has USB-MIDI class drivers (built
into macOS, Windows, modern Linux).

### LPC2361 ISP entry hangs at "Synchronized?"

Two probable causes: (a) the LPC isn't actually in ISP mode (P0.14 must
be LOW at reset — the rear ISP header pulls this), or (b) baud-rate
mismatch.

**Fix:** verify ISP mode pin with a scope or LED. Use 115 200 baud first
(the LPC's ISP supports auto-baud but the host has to send the magic
"?" sync at the right rate). See `lpc2361_investigation_guide.md`.

### CRP fuse blown on the LPC2361 — can't read out original firmware

Expected — Arturia ships with CRP1 enabled. You can still **flash** new
firmware (writes work), you just can't dump the existing image back out.
The decrypted .mbf binary in `firmware/` (recovered from Arturia's update
file) is your reference.

### Pico ↔ LPC2361 UART bridge sees garbage characters

Three things to check, in order:

1. **TX/RX crossed?** Pico GP0 (TX) → DB-9 B:1 → LPC P0.16 (RXD1, pin 63);
   Pico GP1 (RX) ← DB-9 B:6 ← LPC P0.15 (TXD1, pin 62). It's a *cross* —
   tx-to-rx, not tx-to-tx. The LPC UART is UART1, **UNVERIFIED** until the
   Phase 0 continuity check passes; if the check found those pins taken, the
   bridge may use the ISP UART (pins 98/99) instead.
2. **Common ground?** Both processors must share GND. Verify TP72 (LPC
   side) reads continuous to GND on the Pico side through the cable ground pins.
   Check the 1 kΩ series resistors at both ends and that the Pico keeps GP0
   as an input until GP1 reads high (BF 3.1).
3. **Baud rate?** Both ends configured for 115 200 8-N-1. Mismatch shows
   up as repeating but garbled bytes (right framing, wrong content).

---

## When in doubt

- **Re-read the relevant phase in `MACROBRUTE_BUILD_PLAN.md`.** It's
  written linearly — the gotcha is often called out two paragraphs after
  the step you're on.
- **Check `MACROBRUTE_CONNECTION_MAP.md`.** The canonical wiring
  reference. If your wiring disagrees with it, your wiring is wrong.
- **Check `MACROBRUTE_GLOSSARY.md`** if a term in an error message looks
  unfamiliar.
- **Open an issue / write it down for next time.** If you hit a
  pitfall not on this page, that's worth a note in `docs/research/`.

---

> If the synth still works when you unplug everything you've added,
> you've succeeded — the project is incremental on purpose, and the
> stock MicroBrute should be untouched throughout Phases 0–2.
