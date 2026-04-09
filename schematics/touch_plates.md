# MACROBRUTE Touch Plate Interface — Schematic & Design

## Overview

Touch plates add body-contact expression to the MicroBrute expander.
Copper pads on the panel (or body bolts) create variable resistance
paths through the player's body, generating CV signals for modulation.

Two approaches: resistive (simplest) and capacitive (more precise).

---

## 1. Resistive Touch Plates (Body Contact)

The simplest approach — uses skin resistance (~10kR-1MR depending
on moisture, pressure, and contact area) as a voltage divider.

### Single Touch Plate -> CV Output

```
  +3.3V (Pico 3V3_OUT)
    │
  [10kΩ] (pull-up)
    │
    ├─── to Pico ADC (GP26/GP27/GP28)
    │
  TOUCH PAD (copper)
    │
  [body resistance ~10k-1M]
    │
  GROUND PAD (second contact point or chassis)
```

**Output range:**
- No touch: ADC reads 3.3V (pull-up dominates)
- Light touch (~1MR): ADC reads ~3.27V
- Firm touch (~50kR): ADC reads ~2.75V
- Wet/hard press (~10kR): ADC reads ~1.65V

**Problem:** Range is small and nonlinear. Better with op-amp.

### Buffered Touch Plate with Gain

```
  +3.3V
    │
  [10kΩ]
    │
    ├─── [100nF] ─── GND (noise filter)
    │
  TOUCH PAD ── [body] ── GND PAD
    │
  U1A (TL072, non-inverting amp)
    (+in) = touch node
    Rf = 100kΩ (feedback)
    Rg = 10kΩ (to GND)
    Gain = 11x
    │
  out ── [1kΩ] ── CV OUTPUT jack (0-5V range)
```

**Better:** Amplifies the small voltage change from touch.

---

## 2. Capacitive Touch (RP2040 Native)

The RP2040 can measure capacitance changes using its PIO or
a simple charge-time measurement on GPIO pins.

### Principle

```
  Pico GPIO (configured as output, then input)
    │
  [1MΩ] (discharge resistor)
    │
  TOUCH PAD ── capacitance to GND (~10-50pF)
```

**Measurement cycle:**
1. Set GPIO HIGH (charge pad capacitance through 1MR)
2. Switch GPIO to INPUT
3. Measure time until pin reads LOW (RC discharge)
4. Touch adds ~10-30pF body capacitance → longer discharge time
5. Convert time difference to touch intensity

### MicroPython Implementation (for Pico)

```python
import machine
import time

TOUCH_PIN = 26  # GP26

def read_touch():
    pin = machine.Pin(TOUCH_PIN, machine.Pin.OUT)
    pin.value(1)           # Charge
    time.sleep_us(10)      # Brief charge time
    
    pin = machine.Pin(TOUCH_PIN, machine.Pin.IN)
    
    count = 0
    while pin.value() == 1 and count < 1000:
        count += 1
    
    return count            # Higher = more capacitance = touching

# Calibrate: read with no touch, then with touch
baseline = read_touch()
```

### CircuitPython (if using CircuitPython on Pico)

```python
import touchio
import board

touch = touchio.TouchIn(board.GP26)

while True:
    if touch.value:
        print("Touched!")
    print(touch.raw_value)  # Capacitance reading
```

---

## 3. Dedicated Touch IC: MPR121

For more touch points with better sensitivity, use the MPR121
capacitive touch controller (I2C, up to 12 touch channels).

### Wiring

```
  Pico GP2 (I2C0 SDA) ─── MPR121 SDA
  Pico GP3 (I2C0 SCL) ─── MPR121 SCL
  3.3V ────────────────── MPR121 VCC
  GND ─────────────────── MPR121 GND
  MPR121 ADDR ─────────── GND (address 0x5A)
  MPR121 IRQ ──────────── Pico GP6 (optional interrupt)
  
  MPR121 ELE0-ELE11 ────── 12 touch pads (copper tape/PCB pads)
```

**Advantages:** 12 channels, auto-calibration, proximity detection,
I2C interface (only 2 GPIO pins needed from Pico).

**MicroPython driver:** Available on PyPI (`micropython-mpr121`).

---

## 4. Touch Pad Construction

### Option A: Copper Tape on Panel

```
  Aluminium panel (grounded via chassis)
  ├── Adhesive insulation layer (Kapton tape)
  └── Copper tape pads (self-adhesive)
       │
       Wire soldered to each pad → touch circuit
       
  Player touches copper pad while other hand touches
  grounded chassis (or second pad) → circuit completes
```

**Pad size:** 15-25mm diameter circles or 20×30mm rectangles.
Space between pads: minimum 5mm to prevent cross-talk.

### Option B: PCB Pads

```
  Custom PCB with exposed copper areas (no solder mask)
  HASL or ENIG finish for corrosion resistance
  Mount behind panel cutouts
  
  Trace width to pad: 0.5mm minimum
  Pad to ground pour spacing: 2mm minimum
```

### Option C: Brass Bolts (Body Contacts)

```
  M4 or M6 brass bolt through panel
  Inside: ring terminal + wire to touch circuit
  Outside: exposed bolt head = touch point
  
  Player touches bolt with finger
  Ground: second bolt, or panel chassis (if metal)
  
  Advantages: durable, easy to install, industrial aesthetic
  Disadvantage: point contact (less area than pad)
```

### Option D: Conductive Paint / Velostat

```
  Apply conductive paint (Bare Conductive) to panel surface
  Or mount Velostat (pressure-sensitive conductive sheet)
  Wire to circuit via copper tape underneath
  
  Velostat: resistance decreases with pressure
  30kΩ-100kΩ range, good for pressure-sensitive response
```

---

## 5. Multiplexed Touch (8 Pads via CD4051)

Use the same CD4051 multiplexer to read 8 touch pads through
a single ADC channel on the Pico.

```
  Touch Pads 0-7 ──[10kΩ pull-up each]──┬── CD4051 Y0-Y7
                                          │
  CD4051 Z (common) ──── Pico GP26 (ADC0)
  
  CD4051 A ── Pico GP6
  CD4051 B ── Pico GP7
  CD4051 C ── Pico GP11
  
  CD4051 VDD = +3.3V
  CD4051 VEE = GND
  CD4051 VSS = GND
  CD4051 INH = GND
```

**Scan loop:**
1. Set ABC to select pad 0
2. Read ADC (baseline or touched)
3. Increment ABC
4. Repeat for all 8 pads
5. Compare to baseline for touch detection

**Scan rate:** 8 pads × 10us each = 80us per full scan = 12.5kHz
(more than adequate, debounce at software level)

---

## 6. Touch-to-CV Conversion

### Simple: Pico ADC -> PWM DAC -> CV Output

```
  Pico ADC reads touch value (0-4095, 12-bit)
  Apply smoothing (exponential moving average)
  Map to PWM duty cycle on spare GPIO
  
  PWM GPIO ──[10kΩ]──┬── CV OUT jack
                      │
                    [100nF] (LP filter, fc = 160Hz)
                      │
                     GND
  
  PWM frequency: 100kHz (inaudible, easy to filter)
  Resolution: ~10-bit effective after filtering
```

### Better: MCP4728 DAC Channel

If MCP4728 is already in the system (for pitch CV), use a spare
channel for touch CV output.

```
  Touch value → Pico → I2C → MCP4728 channel 2 → CV OUT
  12-bit resolution, 0-4.096V output
```

---

## 7. Musical Applications

| Touch Config | Musical Effect |
|-------------|---------------|
| Single pad → filter cutoff CV | Touch-wah expression |
| Single pad → VCA CV | Touch-sensitive volume |
| Dual pads → pitch + filter | Theremin-like control |
| 8-pad keyboard → note select | Touch keyboard (no keys) |
| Pressure pad → mod amount | Aftertouch-like expression |
| Two-hand touch (body resistance) | Variable feedback/resonance |

### Recommended for MACROBRUTE

- **4 brass bolts on panel** (body contact points)
- **Pico ADC via CD4051 multiplexer** (reuse existing mux)
- **Map to:** Filter CV, VCA CV, LFO rate, resonance
- **PWM → RC filter → CV output** (cheapest, adequate resolution)
- Optional: MPR121 for capacitive proximity detection (I2C on GP2/GP3)

---

## Component Summary

| Component | Qty | Purpose |
|-----------|-----|---------|
| Brass bolts M6 | 4 | Touch contact points |
| 10kΩ resistor | 4 | Pull-ups for resistive sensing |
| 100nF capacitor | 4 | Noise filtering |
| CD4051 | 1 | 8:1 multiplexer (shared with DSO) |
| MPR121 (optional) | 1 | 12-ch capacitive touch controller |
| Copper tape | 1 roll | Alternative to brass bolts |
| Velostat (optional) | 1 sheet | Pressure-sensitive pads |

---

## References

- **AncientJames/jtouch**: https://github.com/AncientJames/jtouch — PIO capacitive touch for RP2040 (76 stars)
- **Gerriko/PicoCapSense**: https://github.com/Gerriko/PicoCapSense — PIO capacitive library (27 stars)
- **CircuitPython touchio**: https://docs.circuitpython.org/en/latest/shared-bindings/touchio/
- **Adafruit MPR121 guide**: https://learn.adafruit.com/adafruit-mpr121-12-key-capacitive-touch-sensor-breakout-tutorial
- **NXP MPR121 filtering**: https://nxp.com/docs/en/application-note/AN3890.pdf
- **Cell Factory Sounds touch prototype**: https://www.cellfactorysounds.com/touch-plate-prototype

**Note:** RP2040 `touchio` is NOT available on RP2350 — use MPR121 for future-proofing.
