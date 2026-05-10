# MACROBRUTE Troubleshooting & Common Pitfalls

Real failure modes, organized by phase. Most of these come from
`schematics/CIRCUIT_REVIEW.md`, `docs/firmware/lpc2361_investigation_guide.md`,
and the Phase 0 bench-validation notes — collected here so you can spot
them before they bite.

If you hit something not on this page, check the original review docs;
they go deeper on the analog circuits.

---

## Phase 0 — Bench validation (Pico + breadboard)

### Both OLEDs report dead, or only one shows up

Both 0.96″ and 0.91″ SSD1306 modules ship with I²C address `0x3C` by default.
On a shared bus that's a hard collision — only one device responds and the
other looks dead.

**Fix:** before applying power, move the strip OLED's ADDR jumper (or solder
pad) to put it on `0x3D`. Confirm with an I²C scan from the Pico:
`for addr in I2C.scan(): print(hex(addr))` should print both `0x3c` and `0x3d`.

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

The protection diode (1N5817) on the -12V rail must be installed with the
**cathode towards the rail** — the schematic shows the band on the rail
side. Reversed, the diode forward-biases the wrong way and clamps -12V to
~+0.3V or worse.

**Fix:** check the band orientation on each 1N5817 before powering up.
Multimeter diode-test mode: probe red on the band-side, black on the
plain-side, you should read ~0.25 V (Schottky forward drop).

### TL074 outputs sit at +12V (or -12V) when no signal applied

The +IN pin is floating. The MicroBrute test points are AC-coupled at the
tap, so each op-amp +IN needs a DC bias path to GND.

**Fix:** add 10 MΩ from each `+IN` pin to GND (rows 8/10 in the breakout
layout). Sets the operating point at 0 V, doesn't load the high-impedance
test point. See CIRCUIT_REVIEW.md §2.

### Ferrite beads (FB1/FB2) burning hot

You used 100 mΩ DC resistance ferrites at full op-amp current. Fine on
paper but the cheap eBay ones run hot. Switch to specified 100 Ω @ 100 MHz
beads (Murata BLM31 series or equivalent), DC resistance ≈ 30 mΩ.

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

Ground loop. The breakout taps TP72 as a star ground. Make sure each test
point's *signal* tap and the *return* go to TP72 via the breakout, not via
the MicroBrute's own ground rail.

**Fix:** verify your wiring against `MACROBRUTE_CONNECTION_MAP.md`. The
"signal goes via DB-9, ground returns via DB-9 pin 9 only" rule is
load-bearing.

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

Expected — the expander uses TL072 unity-gain followers at the receive
side. Sound *should* be ~indistinguishable. If you hear hum: the cable
is acting as an antenna because the shield isn't connected at the
expander side.

**Fix:** terminate DB-9 pin 9 (GND) at the expander, not just at the
synth side. The cable shield should connect to one side only; pick the
expander.

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

1. **TX/RX crossed?** Pico GP0 (TX) → LPC P0.16 (RX); Pico GP1 (RX) ←
   LPC P0.15 (TX). It's a *cross* — tx-to-rx, not tx-to-tx.
2. **Common ground?** Both processors must share GND. Verify TP72 (LPC
   side) reads continuous to GND on the Pico side.
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
