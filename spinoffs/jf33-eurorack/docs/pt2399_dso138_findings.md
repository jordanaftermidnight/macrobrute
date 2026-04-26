# PT2399 / JF-33 & DSO138 — Research Findings

Compiled 2026-04-09 from web research.

---

## PT2399 / JOYO JF-33

### Delay Time Equation (Confirmed)
```
Delay (ms) = 11.46 × R (kΩ) + 29.70
```
Where R is the resistance on Pin 6.

### Pin 6 Anti-Latch-Up — Best Reference
- **Eddy Bergman BMC 83 VC Delay module** — production-ready Eurorack design
- Anti-latch-up: 1MΩ + 100nF + diode + NPN transistor (collector to Pin 6)
- Source: https://www.eddybergman.com/2025/04/voltage-controlled-delay.html
- Also: Peter J. Vis MOSFET-based solution using 2N7000
- Source: https://petervis.com/guitar-circuits/pt2399/pin-6-hack.html

### PT2399 Clones
- **CD2399 / CD2399GP**: Direct Chinese clone, functionally identical
- Same pinout, same specs, available in SMD variant
- No documented differences — drop-in replacement

### JF-33 PCB Mapping
- Gut shots on FreestompBoxes confirm IC positions:
  - U1 = PT2399
  - U2 = SA571D (compander, large chip under middle pot)
  - Op-amp position visible but designator unclear
- No published full schematic or component designator map
- Source: https://www.freestompboxes.org/viewtopic.php?t=17484

### Havoc / Self-Oscillation
- Feedback overdrive technique documented on YouTube (DIY Guitar Pedals)
- Source: https://www.youtube.com/watch?v=9sHnaUfTWug
- Clock injection via Pin 8 enables external sync + pitch-shift glitch
- 1MΩ between Pin 6 and Pin 8 creates gentle warble (confirmed in our docs)

### PT2399 Cascade (Dual Chip)
- Prism Circuits CASCADE DELAY LW: Dual PT2399 in series for longer delays
- Accutronics/Belton Brick reverb modules chain 3x PT2399s internally
- Series cascading requires impedance matching (output > 10kΩ)
- Source: https://bom-squad.com/blog/the-ultimate-pt2399-delay-list/

### Freeze/Hold
- Buffer loop via pausing clock input (Pin 8) with external gate
- Prototype circuits exist in glitch-focused designs, no finalized commercial products
- Achievable with MCU-controlled clock switching

---

## DSO138 / DSO138

### Alternative Firmware
| Firmware | Features | Source |
|----------|----------|--------|
| DLO-138 | Dual channel, digital inputs, enhanced UI | https://github.com/ardyesp/DLO-138 |
| DLO-138-SPI | Optimized for SPI TFT, Blue Pill variant | https://github.com/siliconvalley4066/DLO-138-SPI |
| MicroDSO | Base codebase, spectrum analyzer mode | https://github.com/lcgamboa/MicroDSO |

Stock firmware upgradeable via built-in bootloader.

### Bandwidth
- True bandwidth: ~200kHz (12-bit ADC limitation)
- STM32F103 ADC max: ~1MHz sample rate
- Cannot be meaningfully improved beyond replacing input buffer opamp

### External Trigger
- Not available on stock hardware
- Can be added via GPIO + firmware polling (software trigger)
- Auto/Normal/Single trigger modes exist in stock firmware

### Function Generator Mode
- STM32F103 has DAC on PA4/PA5 — NOT exposed on DSO138 PCB
- ST AN3126 documents waveform generation via DMA + timers
- Requires hardware mod to expose DAC pins via new connector
- Reference: https://github.com/NidasioAlberto/signal-generator

### Serial Data Output
- Stock firmware supports UART serial output
- depau/dso138mini-viewer: Python app reads waveforms via serial
- Source: https://github.com/depau/dso138mini-viewer
- JYE Tech Forum post #1797: serial output protocol documentation

### Power & Eurorack Mounting
- **Power:** 120mA at 9V (~1.1W). Use 7809 from +12V Eurorack rail.
- **PCB size:** ~80mm × 60mm
- **Mounting options:**
  - AI Synthesis: Mounted to two 2HP blank panels via spacers
  - Clarionut Thingiverse: 3D-printed Eurorack mount kit (thing:7136870)
  - MeeBilt YouTube: Complete integration walkthrough
- Source: https://aisynthesis.com/cheap-eurorack-oscilloscope/
- Source: https://www.thingiverse.com/thing:7136870

---

## Source URLs (All)

- https://petervis.com/guitar-circuits/pt2399/pin-6-hack.html
- https://bom-squad.com/blog/the-ultimate-pt2399-delay-list/
- https://electricdruid.net/useful-design-equations-for-the-pt2399/
- https://www.eddybergman.com/2025/04/voltage-controlled-delay.html
- https://www.youtube.com/watch?v=9sHnaUfTWug
- https://www.freestompboxes.org/viewtopic.php?t=17484
- https://github.com/ardyesp/DLO-138
- https://github.com/siliconvalley4066/DLO-138-SPI
- https://github.com/lcgamboa/MicroDSO
- https://github.com/depau/dso138mini-viewer
- https://github.com/NidasioAlberto/signal-generator
- https://aisynthesis.com/cheap-eurorack-oscilloscope/
- https://www.thingiverse.com/thing:7136870
- https://www.youtube.com/watch?v=gS6kTWKKlRY
