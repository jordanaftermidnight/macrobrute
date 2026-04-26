# DSO138 Deep Mods

Extracted from MACROBRUTE `docs/mods/deep_circuit_bending.md` because
the DSO138 is now a desktop spinoff, not a Eurorack module.

---

## DSO138/DSO138 Deep Mods

### DAC Output for Function Generator

The STM32F103 on the DSO138 has a 12-bit DAC (PA4).
With alternative firmware, it can output waveforms.

```
  STM32 PA4 (DAC output, normally unused)
    │
  [1kΩ] (isolation)
    │
  TL072 buffer (+in)
    │
  Output → function generator jack
  
  Firmware mod: generate sine/square/triangle/noise
  on PA4 while displaying on screen
```

**Note:** Requires custom firmware modification. Stock firmware
does not expose DAC functionality.

### Trigger Output for Clock Generation

The trigger output (normally just for scope sync) can be
repurposed as a clock/gate generator:

```
  DSO138 trigger output (3.3V logic)
    │
  [1kΩ]
    │
  2N3904 base
    │
  Collector ── +5V via 10kΩ pull-up
    │
  Output → clock jack (0/5V)
  
  Emitter → GND
```

Set trigger mode to "auto" with desired threshold for
rhythm-synchronized clock derived from audio input.

### Serial Data Export

The DSO138 Mini has a serial output that can stream ADC samples:

```
  DSO138 Mini serial TX (3.3V TTL)
    │
  USB-TTL adapter (CP2102 or similar)
    │
  Computer: depau/dso138mini-viewer (Python)
  
  Streams: raw ADC samples at ~1Msps
  Use for: data logging, FFT analysis, recording waveforms
```

### DLO-138 Alternative Firmware Features

The DLO-138 firmware adds:
- Better trigger stability
- Larger buffer (with DMA optimization)
- Serial protocol for remote control
- Faster sweep rates
- DLO-138-SPI variant for SPI-connected displays

---
