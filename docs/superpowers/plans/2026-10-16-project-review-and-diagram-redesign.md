# Project Review + Diagram Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Audit and correct the whole MACROBRUTE project (pinouts, wiring, power, docs structure), then regenerate the Phase 0 diagrams in the stripboard-template style from a single verified hardware data source.

**Architecture:** Phase A produces one canonical hardware data module plus a doc/firmware consistency checker, uses them to write an audit report, gates on user decisions, then corrects docs and re-orders the manual. Phase B builds a shared SVG kit and a net validator, gets a visual sign-off in the Design app, and regenerates the five Phase 0 cards. Later diagram batches (breakout + interconnect, expander, mods m01-m14) get their own plans after Phase A's decisions land.

**Tech Stack:** Python 3 (stdlib only, plus `pytest` for tests), `rsvg-convert` for render checks, existing `tools/build_manual.py`.

**Spec:** `docs/superpowers/specs/2026-10-16-diagram-redesign-design.md`

## Global Constraints

- Canonical pin source is `firmware/pico/config.py`; `docs/MACROBRUTE_CONNECTION_MAP.md` must agree with it (its own header says so).
- Connector is 2x DB-9 today (HD-15/VGA rejected: cable shorts pins 6-8 to GND). Task 3 may change this by user decision.
- Never add `Co-Authored-By` lines to commits or any file (user's global rule).
- Do not mention music genre in any new or edited document. Task 5 removes existing mentions.
- Diagram cards are self-contained light cards (own palette), fixed-width font, minimum 9px text, no clipped canvas, labels in knock-out boxes.
- Docs conflicts are reported to the user and resolved explicitly; never silently picked.
- No hardware is built yet; no step may assume measured values. Mark anything unverified "UNVERIFIED".
- Do not touch the untracked `MicroBrute_v1.0.4.114.bin.c/.h` files.

## Review Focus

- Two GPIO claims for one pin (e.g. a pin listed both as spare and allocated) must be caught by the checker.
- A diagram or doc naming a pin that does not exist on the Pico (GP23-25, GP29) must fail validation.
- A 5 V net reaching a Pico GPIO without a level shifter or divider must fail validation (RP2040 is not 5 V tolerant).
- Two different sources for the same rail (e.g. breakout +/-12 V from MicroBrute TP70/71 vs from the expander over DB-9 B) must be flagged as a conflict, not drawn twice.
- Manual build must not silently skip a missing SVG listed in `SVG_MAP`; it must report it.

---

## Phase A — Audit, decisions, corrections

### Task 1: Canonical hardware data module

**Files:**
- Create: `tools/hwdata/__init__.py` (empty)
- Create: `tools/hwdata/pico.py`
- Create: `tools/tests/test_hwdata_pico.py`

**Interfaces:**
- Produces: `PICO_PHYSICAL_PIN: dict[int, int]` (GP number to physical header pin), `PICO_USABLE_GP: frozenset[int]`, `load_firmware_gpio(config_path) -> dict[str, int | tuple[int, ...]]`, `FIRMWARE_ROLES: dict[str, int | tuple[int, ...]]` (role name to GP).

- [ ] **Step 1: Write the failing test**

```python
# tools/tests/test_hwdata_pico.py
from pathlib import Path
from tools.hwdata.pico import (
    PICO_PHYSICAL_PIN, PICO_USABLE_GP, FIRMWARE_ROLES, load_firmware_gpio,
)

CONFIG = Path(__file__).resolve().parents[2] / "firmware/pico/config.py"

def test_physical_pins_match_pico_datasheet():
    assert PICO_PHYSICAL_PIN[0] == 1 and PICO_PHYSICAL_PIN[1] == 2
    assert PICO_PHYSICAL_PIN[4] == 6 and PICO_PHYSICAL_PIN[22] == 29
    assert PICO_PHYSICAL_PIN[28] == 34

def test_unexposed_gpios_are_not_usable():
    assert not ({23, 24, 25, 29} & PICO_USABLE_GP)

def test_firmware_roles_match_config_py():
    cfg = load_firmware_gpio(CONFIG)
    for role, gp in FIRMWARE_ROLES.items():
        assert cfg[role] == gp, role

def test_no_gpio_assigned_twice():
    flat = []
    for gp in FIRMWARE_ROLES.values():
        flat.extend(gp if isinstance(gp, tuple) else (gp,))
    assert len(flat) == len(set(flat))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/jordan_after_midnight/Projects/music/macrobrute && python3 -m pytest tools/tests/test_hwdata_pico.py -v`
Expected: FAIL (ModuleNotFoundError: tools.hwdata.pico). If `tools/__init__.py` is missing, create it empty.

- [ ] **Step 3: Write minimal implementation**

```python
# tools/hwdata/pico.py
"""Canonical Pico WH pin data. Firmware config.py is the source of truth for roles."""
import ast
from pathlib import Path

PICO_PHYSICAL_PIN = {
    0: 1, 1: 2, 2: 4, 3: 5, 4: 6, 5: 7, 6: 9, 7: 10, 8: 11, 9: 12,
    10: 14, 11: 15, 12: 16, 13: 17, 14: 19, 15: 20, 16: 21, 17: 22,
    18: 24, 19: 25, 20: 26, 21: 27, 22: 29, 26: 31, 27: 32, 28: 34,
}
PICO_USABLE_GP = frozenset(PICO_PHYSICAL_PIN)

FIRMWARE_ROLES = {
    "LPC_TX": 0, "LPC_RX": 1,
    "DAISY_SDA": 2, "DAISY_SCL": 3,
    "OLED_SDA": 4, "OLED_SCL": 5,
    "AUX_OUT_PINS": (19, 20, 6, 7),
    "LED_CLOCK": 8, "LED_GATE": 9, "LED_MODE": 10,
    "DAISY_INT": 11, "BTN_TAP": 12,
    "ENC_SW": 13, "ENC_CLK": 14, "ENC_DT": 15,
    "CLK_DIV_PINS": (16, 17, 18),
    "CLOCK_IN": 21, "CLOCK_OUT": 22,
}


def load_firmware_gpio(config_path):
    """Return {NAME: int | tuple[int]} for literal assignments in config.py."""
    out = {}
    tree = ast.parse(Path(config_path).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            name = getattr(node.targets[0], "id", None)
            try:
                val = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                continue
            if name and isinstance(val, (int, tuple)):
                out[name] = val
    return out
```

Note: the tuple values duplicate GP6/7 (aux) with no other role; the test in Step 1 confirms no overlap with LED/encoder pins.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tools/tests/test_hwdata_pico.py -v`
Expected: 4 PASS

- [ ] **Step 5: Commit**

```bash
git add tools/hwdata tools/tests tools/__init__.py
git commit -m "feat: add canonical Pico pin data with firmware cross-check"
```

### Task 2: Doc consistency checker

**Files:**
- Create: `tools/check_docs.py`
- Create: `tools/tests/test_check_docs.py`

**Interfaces:**
- Consumes: `FIRMWARE_ROLES`, `PICO_USABLE_GP` from Task 1.
- Produces: `check_connection_map(md_text) -> list[str]` (list of human-readable problems), CLI `python3 tools/check_docs.py` exiting non-zero when problems exist.

Checks implemented: (a) every `GPn` row in the connection map GPIO table maps to a role in `FIRMWARE_ROLES` at the same GP; (b) no doc text names `GP23`, `GP24`, `GP25`, `GP29` as usable; (c) the phrase "spare GPIO" is not claimed alongside "No truly spare GPIO"; (d) LPC UART pin names (`P0.2`/`P0.3` vs `P0.15`/`P0.16`) used in the bridge description are consistent across `docs/*.md` and `firmware/lpc2361/src/config.h`.

- [ ] **Step 1: Write the failing test**

```python
# tools/tests/test_check_docs.py
from tools.check_docs import check_connection_map, check_lpc_uart_claims

def test_flags_unexposed_gpio_listed_as_spare():
    text = "With 8 spare GPIOs (GP2,3,6,7,11,23,24,25) + 3 ADC"
    problems = check_connection_map(text)
    assert any("GP23" in p for p in problems)

def test_flags_gpio_row_disagreeing_with_firmware():
    text = "| GP9 | 12 | Encoder switch | IN | x |"
    problems = check_connection_map(text)
    assert any("GP9" in p for p in problems)

def test_clean_row_passes():
    text = "| GP13 | 17 | Encoder switch | IN | Pull-up |"
    assert check_connection_map(text) == []

def test_lpc_uart_conflict_detected():
    docs = {"a.md": "bridge uses P0.16 (RXD1)", "b.md": "bridge uses P0.2/P0.3 (TXD0/RXD0)"}
    assert check_lpc_uart_claims(docs)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tools/tests/test_check_docs.py -v`
Expected: FAIL (cannot import check_docs)

- [ ] **Step 3: Write minimal implementation**

```python
# tools/check_docs.py
import re
import sys
from pathlib import Path

from tools.hwdata.pico import FIRMWARE_ROLES

ROW = re.compile(r"^\|\s*GP(\d+)\s*\|[^|]*\|\s*([^|]+)\|", re.M)
NOT_EXPOSED = (23, 24, 25, 29)
ROLE_HINTS = {
    0: "UART0 TX", 1: "UART0 RX", 2: "I²C1 SDA", 3: "I²C1 SCL",
    4: "I²C0 SDA", 5: "I²C0 SCL", 8: "RGB LED R", 9: "RGB LED G",
    10: "RGB LED B", 11: "EFFIGY INT", 12: "Tap button",
    13: "Encoder switch", 14: "Encoder CLK", 15: "Encoder DT",
    21: "Clock input", 22: "Clock output",
}


def check_connection_map(text):
    problems = []
    for gp in NOT_EXPOSED:
        if re.search(rf"\bGP{gp}\b", text) and "internal" not in text.lower():
            problems.append(f"GP{gp} is not exposed on the Pico but is mentioned")
    for m in ROW.finditer(text):
        gp, func = int(m.group(1)), m.group(2).strip()
        hint = ROLE_HINTS.get(gp)
        if hint and hint.lower() not in func.lower():
            problems.append(f"GP{gp} row says '{func}', firmware role is '{hint}'")
    return problems


def check_lpc_uart_claims(docs):
    """docs: {filename: text}. Flag if bridge UART pins are described two ways."""
    uart1 = [f for f, t in docs.items() if re.search(r"P0\.1[56]", t)]
    uart0 = [f for f, t in docs.items() if re.search(r"P0\.[23]\b.*(bridge|Pico)", t)]
    if uart1 and uart0:
        return [f"bridge UART conflict: UART1 (P0.15/16) in {uart1}, UART0 (P0.2/3) in {uart0}"]
    return []


def main():
    root = Path(__file__).resolve().parents[1]
    docs = {str(p.relative_to(root)): p.read_text() for p in root.glob("docs/**/*.md")}
    problems = []
    cmap = docs.get("docs/MACROBRUTE_CONNECTION_MAP.md", "")
    problems += check_connection_map(cmap)
    problems += check_lpc_uart_claims(docs)
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests, then run the checker on the real docs**

Run: `python3 -m pytest tools/tests/test_check_docs.py -v && python3 tools/check_docs.py`
Expected: tests PASS; checker prints PROBLEM lines for the stale `12G` spare-GPIO paragraph and the LPC UART conflict (these are the known findings to fix in Task 5). Save the output for Task 3.

- [ ] **Step 5: Commit**

```bash
git add tools/check_docs.py tools/tests/test_check_docs.py
git commit -m "feat: add doc-vs-firmware consistency checker"
```

### Task 3: Project audit report

**Files:**
- Create: `docs/superpowers/reviews/2026-10-16-project-audit.md`

Run five independent read-only reviews in parallel (one subagent each, each told to write findings with file:line and severity, and to mark anything it cannot verify as UNVERIFIED), then merge into the report. Reviewers:

1. **Pins and buses:** `firmware/pico/config.py`, `docs/MACROBRUTE_CONNECTION_MAP.md`, `schematics/pico_pinout.md`, `schematics/phase0_wiring_schematic.svg`; plus LPC UART (UART0 vs UART1) using `firmware/lpc2361/src/config.h`, `docs/research/mbf_analysis.md`, `tools/ghidra`.
2. **Power:** every statement about where +/-12 V, +5 V, 3V3 come from (`docs/MACROBRUTE_BUILD_PLAN.md`, connection map section 5.3, `schematics/power_regulation_diagram.svg`, `schematics/pico_power_protection.svg`, `docs/hardware/MACROBRUTE_BOM.md`); current budgets; ground-loop risk.
3. **Analog/protection circuits:** output buffers, CD40106 gate path, CD4049 level shifting, CV input clamps (`schematics/CIRCUIT_REVIEW.md`, `breakout_pcb.md`, `cv_input_protection_diagram.svg`); confirm no 5 V net reaches a Pico GPIO.
4. **Scope and structure:** which expander modules are in or out (`docs/MACROBRUTE_CONNECTION_MAP.md` section 10 vs `schematics/expander_*.svg`/`expander_stripboard.md`/README/manual TOC); stale legacy docs; `SVG_MAP` entries pointing at missing files in `tools/build_manual.py`.
5. **Cable/connector options:** signal count across DB-9 A + B, and feasibility of a single connector (DB-25, DB-37 per `docs/legacy/MACROBRUTE_EXPANDER_DB37_PINOUT.md`, or multiplexing). Include that analog audio and CV signals should not share a CD4051 mux, and that two CD4051 are already earmarked in the BOM.

Known findings to include and verify (already seen during planning):
- Power source conflict: connection map 5.3 and Phase 0 power diagram tap MicroBrute TP70/TP71/+5 V for the breakout, while the build plan, DB-9 B pins 7/8 and the power-chain diagram say +/-12 V comes from the Eurorack supply over the cable.
- Strip OLED 0.91" is described as powered from MicroBrute 5 V "with onboard level shifter" while sharing the Pico's 3.3 V I2C bus; most SSD1306 modules have no level shifter, so 5 V pull-ups could reach RP2040 GPIOs.
- LPC bridge UART: firmware config and connection map 5.4 say UART1 (P0.15/P0.16); connection map 12D says UART0 (P0.2/P0.3); `mbf_analysis.md` says UART0 is free and flags UART1 as possibly MIDI.
- Connection map 12G still claims 8 spare GPIOs; section 1 says none are spare and GP23-25 are not exposed.
- Breakout U4 CD4049UBE is listed on the MicroBrute-side breakout but "powered from 3.3 V"; the 3.3 V rail lives on the Pico (expander) side. Confirm which side the level shifter belongs on.
- Expander scope: section 10 says the expander is minimal (slew limiter only; LFO, S&H, noise, mult, attenuverter dropped because the user's rack already has equivalents), but `schematics/expander_lfo.svg`, `expander_sah.svg`, `expander_noise.svg`, `expander_attenuverter.svg`, `expander_clockdiv.svg`, `expander_stripboard.md` and the README still describe them.
- `SVG_MAP` references files that do not exist (e.g. `wiring_overview.svg`, `system_architecture_block.svg`, `testpoints_map.svg`).
- Several legacy docs (42 HP, DB-37) still appear in the manual's main flow.

- [ ] **Step 1:** Dispatch the five reviewers in parallel (single message, five Agent calls), each with the file list above and the instruction to report, not fix.
- [ ] **Step 2:** Merge their output plus the Task 2 checker output into the report with a severity-ranked table (Blocker / Should fix / Nice to have), each row with file:line, the conflict, and a recommendation.
- [ ] **Step 3:** Add a "Decisions needed" section listing the five user decisions in Task 4.
- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/reviews
git commit -m "docs: add project audit report"
```

### Task 4: User decision gate (no code)

Present the report and get explicit answers before any doc is edited:

1. **Cable:** keep 2x DB-9, or one connector. Planning-time recommendation: one shielded DB-25 (parallel-port style) cable; 8 outputs + 2 CV inputs + UART + I2C + +/-12 V is 16 signals, leaving 9 pins for interleaved grounds. Multiplexing is not recommended for audio/CV (crosstalk, level loss, needs simultaneous signals); a CD4051 stays reserved for touch/slow control.
2. **Breakout power source:** MicroBrute TP70/TP71 (self-contained) versus Eurorack over the cable. Recommendation pending Task 3 review of current budget and ground-loop risk.
3. **Strip OLED supply:** run from a 3.3 V source (MicroBrute +3V3ARM on P4 pin 5, or via cable) rather than 5 V, unless the module is verified to have a level shifter.
4. **LPC bridge UART:** confirm UART1 (P0.15/16) after reading the Ghidra evidence, or choose UART0.
5. **Expander scope:** confirm the minimal expander (slew, clock I/O, firmware dividers and aux outs) with LFO/S&H/noise/mult/attenuverter as separate modules from the user's rack, or add any of them back to the expander. Dropped-module files go to `spinoffs/` or `docs/legacy/`.

- [ ] **Step 1:** Ask the five questions (AskUserQuestion, one call, with the report's recommendation first).
- [ ] **Step 2:** Record the answers at the top of the audit report under "Decisions" and commit.

```bash
git add docs/superpowers/reviews
git commit -m "docs: record audit decisions"
```

### Task 5: Apply documentation corrections

**Files (modify):** `docs/MACROBRUTE_CONNECTION_MAP.md`, `schematics/pico_pinout.md`, `docs/MACROBRUTE_BUILD_PLAN.md`, `docs/MACROBRUTE_README.md`, `README.md`, `docs/hardware/MACROBRUTE_BOM.md`, `docs/MACROBRUTE_VISION.md`, others named by the audit report; plus the 12 files that mention genre: `README.md`, `docs/MACROBRUTE_FIRMWARE_MOD_PLAN.md`, `docs/MACROBRUTE_MOD_SELECTION.md`, `docs/MACROBRUTE_BUILD_PLAN.md`, `docs/architecture/MACROBRUTE_COMPREHENSIVE_RESEARCH.md`, `docs/legacy/MACROBRUTE_MASTER_PLAN.md`, `docs/hardware/MACROBRUTE_BOM.md`, `docs/mods/microbrute_mods_guide.md`, `docs/mods/microbrute_circuit_bending_guide.md`, `docs/mods/touch_bend_specs.md`, `docs/legacy/MACROBRUTE_PROJECT_HANDOFF.md`, `schematics/touch_plates.md`, and `spinoffs/jf33-eurorack/docs/pt2399_deep_bending.md`.

- [ ] **Step 1:** Re-run `python3 tools/check_docs.py` and keep the list.
- [ ] **Step 2:** For each Blocker/Should-fix row in the audit report, edit the affected doc to match the decision from Task 4 (pin tables first, then prose). Update the connection map and `firmware/pico/config.py` comments together when a pin role changes.
- [ ] **Step 3:** Remove genre wording from the 13 files above (rewrite the sentence neutrally, e.g. "high-impact sound-shaping mods"); verify with `grep -rIil -E "techno|industrial" . --exclude-dir=.git --exclude-dir=firmware --exclude="Macrobrute Manual.html"` returning nothing.
- [ ] **Step 4:** Run `python3 tools/check_docs.py && python3 -m pytest tools/tests -v`. Expected: exit 0, all tests pass.
- [ ] **Step 5: Commit** (one commit per logical doc group)

```bash
git add -A docs schematics README.md spinoffs
git commit -m "docs: apply audit corrections and neutral wording"
```

### Task 6: Re-order and prune the manual

**Files:**
- Modify: `tools/build_manual.py` (`SVG_MAP`, section/TOC grouping, missing-file reporting)
- Move: dropped expander module docs/SVGs per decision 5 to `spinoffs/` or `docs/legacy/`
- Create: `tools/tests/test_build_manual.py`

**Interfaces:**
- Produces: `missing_svgs(svg_map, root) -> list[str]`; build prints a warning and exits non-zero when it is non-empty.

- [ ] **Step 1: Write the failing test**

```python
# tools/tests/test_build_manual.py
from pathlib import Path
from tools.build_manual import missing_svgs

def test_reports_missing_svg(tmp_path):
    (tmp_path / "a.svg").write_text("<svg/>")
    m = {"x.md": ["a.svg", "gone.svg"]}
    assert missing_svgs(m, tmp_path) == ["gone.svg"]
```

- [ ] **Step 2: Run to verify fail:** `python3 -m pytest tools/tests/test_build_manual.py -v` (FAIL: cannot import `missing_svgs`).
- [ ] **Step 3: Implement**

```python
def missing_svgs(svg_map, root):
    root = Path(root)
    return sorted({s for svgs in svg_map.values() for s in svgs if not (root / s).exists()})
```

Add to `main()` in `tools/build_manual.py`: call `missing_svgs(SVG_MAP, PROJECT)`, print each, and `sys.exit(1)` if any. Then fix `SVG_MAP` entries (remove or repoint) until it is empty.

- [ ] **Step 4:** Re-order manual sections: Start Here, Architecture/Connection map, Power, Breakout, Expander (reduced scope), Control and firmware, Reference, Legacy collapsed last. Change only titles/groups/order in `build_manual.py`, not document text.
- [ ] **Step 5:** `python3 -m pytest tools/tests -v && python3 tools/build_manual.py`, open the manual, confirm the TOC order and no console errors.
- [ ] **Step 6: Commit**

```bash
git add tools docs spinoffs schematics "Macrobrute Manual.html"
git commit -m "docs: reorder manual, prune dropped expander modules, report missing SVGs"
```

---

## Phase B — Diagram system and Phase 0 batch

### Task 7: Shared SVG kit

**Files:**
- Create: `tools/diagram_kit.py`
- Create: `tools/tests/test_diagram_kit.py`

**Interfaces:**
- Produces: `PALETTE: dict[str, str]`, `Card(width, height, title, subtitle)` with `.add(svg_fragment)`, `.legend(items: list[tuple[str, str]])`, `.render() -> str`; glyph functions `resistor(x, y, label, horizontal=True)`, `led(x, y, label, color)`, `diode(x, y, label)`, `capacitor(x, y, label)`, `jack(x, y, label)`, `dip(x, y, name, pins: list[str])`, `wire(points, color, junctions=())`, `label_box(x, y, text)` each returning an SVG string.

- [ ] **Step 1: Write the failing test**

```python
# tools/tests/test_diagram_kit.py
import xml.etree.ElementTree as ET
from tools.diagram_kit import Card, PALETTE, resistor, wire, label_box

def test_card_is_valid_xml_and_fits_viewbox():
    c = Card(400, 200, "T", "sub")
    c.add(resistor(50, 50, "1kΩ"))
    c.add(wire([(10, 10), (100, 10)], PALETTE["audio"]))
    root = ET.fromstring(c.render())
    assert root.get("viewBox") == "0 0 400 200"

def test_text_never_below_9px():
    c = Card(300, 100, "T", "s")
    c.add(label_box(20, 20, "hello"))
    for el in ET.fromstring(c.render()).iter():
        fs = el.get("font-size")
        if fs:
            assert float(fs.replace("px", "")) >= 9

def test_card_uses_light_self_contained_background():
    svg = Card(100, 100, "T", "s").render()
    assert PALETTE["card"] in svg
```

- [ ] **Step 2:** Run `python3 -m pytest tools/tests/test_diagram_kit.py -v`. Expected: FAIL (import error).
- [ ] **Step 3: Implement** `tools/diagram_kit.py`: palette taken from the stripboard template (`#f5f5ee` card, `#222` title, red `#d9534f` +12V, purple `#6a5acd` -12V, green `#5cb85c` GND, orange `#e8a317` 3V3/5V, audio blue `#1f6fd1`, CV amber `#c96a00`, gate green `#1a9a3a`, clock purple `#8a2be2`); `Card.render()` emits `<svg xmlns=... viewBox="0 0 W H" width=W height=H>` with a `<style>` block using `"SF Mono", Consolas, "Liberation Mono", monospace`, a card `<rect>` filled `PALETTE["card"]` with a 1px stroke, a title and subtitle at the top, and the legend row at the bottom; each glyph builds its fragment from `<line>/<rect>/<path>/<text font-size="10">`; `label_box` draws a white-filled rounded `<rect>` sized from `len(text) * 6.2` plus the `<text font-size="10">` on top so wires never run through text.
- [ ] **Step 4:** Run the tests again. Expected: 3 PASS.
- [ ] **Step 5: Commit**

```bash
git add tools/diagram_kit.py tools/tests/test_diagram_kit.py
git commit -m "feat: add shared diagram kit in stripboard-template style"
```

### Task 8: Net validator

**Files:**
- Create: `tools/check_diagrams.py`
- Create: `tools/tests/test_check_diagrams.py`

**Interfaces:**
- Consumes: `PICO_USABLE_GP` (Task 1).
- Produces: `validate_nets(nets: dict[str, list[tuple[str, str]]], rails: dict[str, float]) -> list[str]`. A net is a name mapped to endpoints `(part, pin)`; rails maps net names to volts.

Rules: (1) any `("PICO", "GPn")` endpoint with n not in `PICO_USABLE_GP` fails; (2) a GP used on two nets fails; (3) a net with rail voltage > 3.3 that touches a Pico GP endpoint fails unless it also contains a `("SHIFT", ...)` or `("DIV", ...)` endpoint; (4) a net with a single endpoint (floating) fails.

- [ ] **Step 1: Write the failing test**

```python
# tools/tests/test_check_diagrams.py
from tools.check_diagrams import validate_nets

def test_unexposed_gpio_rejected():
    nets = {"n": [("PICO", "GP23"), ("LED", "A")]}
    assert any("GP23" in p for p in validate_nets(nets, {}))

def test_five_volt_to_gpio_rejected():
    nets = {"gate": [("PICO", "GP12"), ("U3", "out")]}
    assert any("5" in p for p in validate_nets(nets, {"gate": 5.0}))

def test_five_volt_with_shifter_ok():
    nets = {"gate": [("PICO", "GP12"), ("U3", "out"), ("SHIFT", "U4")]}
    assert validate_nets(nets, {"gate": 5.0}) == []

def test_gpio_on_two_nets_rejected():
    nets = {"a": [("PICO", "GP4"), ("X", "1")], "b": [("PICO", "GP4"), ("Y", "1")]}
    assert any("GP4" in p for p in validate_nets(nets, {}))

def test_floating_net_rejected():
    assert validate_nets({"a": [("X", "1")]}, {})
```

- [ ] **Step 2:** Run it; expected FAIL.
- [ ] **Step 3: Implement**

```python
# tools/check_diagrams.py
from tools.hwdata.pico import PICO_USABLE_GP


def validate_nets(nets, rails):
    problems, seen = [], {}
    for name, ends in nets.items():
        if len(ends) < 2:
            problems.append(f"net {name} is floating")
        gps = [p for part, p in ends if part == "PICO" and p.startswith("GP")]
        for gp in gps:
            n = int(gp[2:])
            if n not in PICO_USABLE_GP:
                problems.append(f"{gp} is not an exposed Pico GPIO (net {name})")
            if gp in seen and seen[gp] != name:
                problems.append(f"{gp} used on nets {seen[gp]} and {name}")
            seen[gp] = name
        if gps and rails.get(name, 0) > 3.3:
            if not any(part in ("SHIFT", "DIV") for part, _ in ends):
                problems.append(f"net {name} is {rails[name]} V into a Pico GPIO with no shifter")
    return problems
```

- [ ] **Step 4:** `python3 -m pytest tools/tests -v`. Expected: all PASS.
- [ ] **Step 5: Commit**

```bash
git add tools/check_diagrams.py tools/tests/test_check_diagrams.py
git commit -m "feat: add diagram net validator"
```

### Task 9: Visual sign-off in the Design app (gate)

**Files:** `docs/superpowers/reviews/style-signoff/phase0_wiring_mockup.svg` (output)

- [ ] **Step 1:** Using Task 7's kit, draw one card (Phase 0 wiring: Pico left; two OLEDs, RGB LED, tap button, encoder, clock jacks right) with pin labels read from `FIRMWARE_ROLES`.
- [ ] **Step 2:** Run `quickstart` with intent `design`, open that card in the Design app, and ask the user to approve or mark up the look (palette, density, label style, legend).
- [ ] **Step 3:** Fold the requested changes into `tools/diagram_kit.py` (adjust palette/glyph code, re-run `tools/tests`), and commit.

```bash
git add tools/diagram_kit.py docs/superpowers/reviews/style-signoff
git commit -m "style: apply approved diagram look"
```

Do not generate Tasks 10-14 until the user approves this look.

### Task 10: Phase 0 wiring schematic

**Files:**
- Create: `tools/diagrams/phase0_wiring.py`
- Modify: `schematics/phase0_wiring_schematic.svg` (generated)

- [ ] **Step 1:** Define the nets as data in the script (names, endpoints, rail voltages) using pin names from `FIRMWARE_ROLES`; build the card with kit glyphs; call `validate_nets(...)` before writing; fail loudly on any problem.
- [ ] **Step 2:** `python3 tools/diagrams/phase0_wiring.py` writes the SVG; `rsvg-convert -w 1400 schematics/phase0_wiring_schematic.svg -o <scratchpad>/p0_wiring.png`, then inspect the PNG for overlaps, clipping, and correct pin labels against `config.py`.
- [ ] **Step 3: Commit**

```bash
git add tools/diagrams schematics/phase0_wiring_schematic.svg
git commit -m "diagram: regenerate Phase 0 wiring schematic"
```

### Task 11: Phase 0 breadboard

**Files:** Create `tools/diagrams/phase0_breadboard.py`; modify `schematics/phase0_breadboard.svg`.

- [ ] **Step 1:** Draw a half-size breadboard with numbered rows (1-30) and lettered columns, Pico WH straddling the center channel, each peripheral at a stated row/column, each jumper listed in a table under the board (from, to, color) generated from the same nets as Task 10.
- [ ] **Step 2:** Run the script, validate nets, render with `rsvg-convert`, inspect.
- [ ] **Step 3: Commit** (`diagram: regenerate Phase 0 breadboard`).

### Task 12: Pico pinout card

**Files:** Create `tools/diagrams/pico_pinout.py`; modify `schematics/pico_pinout_diagram.svg`.

- [ ] **Step 1:** Draw the 40-pin header with physical pin numbers (`PICO_PHYSICAL_PIN`), GP numbers, role color-coding (I2C, UART, GPIO out/in, ADC, power, unexposed), and the allocation text from `FIRMWARE_ROLES`.
- [ ] **Step 2:** Run, render, compare every label against `firmware/pico/config.py`.
- [ ] **Step 3: Commit** (`diagram: regenerate Pico pinout`).

### Task 13: Power chain and Pico protection cards

**Files:** Create `tools/diagrams/power_chain.py`, `tools/diagrams/pico_protection.py`; modify `schematics/power_regulation_diagram.svg`, `schematics/pico_power_protection.svg`.

- [ ] **Step 1:** Draw the power source topology chosen in Task 4 decision 2 (one source per rail, current budget stated), with the Pico VSYS filter (1N5817, 100 µF, 100 nF) as a proper schematic.
- [ ] **Step 2:** Run, validate, render, inspect.
- [ ] **Step 3: Commit** (`diagram: regenerate power chain and Pico protection`).

### Task 14: Rebuild manual and verify

- [ ] **Step 1:** `python3 -m pytest tools/tests -v && python3 tools/check_docs.py && python3 tools/build_manual.py`. Expected: all pass, exit 0, no missing SVGs.
- [ ] **Step 2:** Open the manual in both themes (use the Claude in Chrome or Playwright tools) and confirm the five cards render with no clipping or overlap.
- [ ] **Step 3: Commit**

```bash
git add "Macrobrute Manual.html" schematics
git commit -m "docs: rebuild manual with regenerated Phase 0 diagrams"
```

### Task 15: Next-batch plans

- [ ] **Step 1:** Write follow-up plans: breakout + interconnect (single cable or DB-9 pair, per decision 1), expander modules (per decision 5), and mods m01-m14, each as its own plan reusing the kit and validator.

---

## Self-review

- **Spec coverage:** kit (Task 7), pin table (Task 1), validator (Task 8), Phase 0 batch (Tasks 10-13), visual sign-off (Task 9), manual integration and render check (Tasks 6 and 14), doc conflicts reported not guessed (Tasks 3-4). Later batches deliberately deferred to Task 15.
- **Added beyond spec at user request:** full project audit and corrections (Tasks 2-6), single-cable evaluation, expander scope check, genre scrub.
- **Type consistency:** `FIRMWARE_ROLES`, `PICO_USABLE_GP`, `PICO_PHYSICAL_PIN` defined in Task 1 and used with the same names in Tasks 2, 8, 10, 12.
- **Known soft spots:** Tasks 3, 5, 10-13 depend on user decisions in Task 4 and on the audit's findings, so their edit lists are driven by the report rather than fixed here.
