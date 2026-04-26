#!/usr/bin/env python3
"""Generate firmware/pico/_effigy_constants.py from EFFIGY's C header.

EFFIGY's `firmware/src/macrobrute_bridge.h` is the **authoritative source** for
the bridge protocol's register addresses, event types, and error codes. The
MACROBRUTE Pico-side firmware imports those values from a generated Python
module — this script does the parsing and emits the file.

Run this whenever the C header changes. The generated file is committed
(MicroPython on a Pico can't run a code-gen step at boot), but it's marked
as generated and includes the source's git revision in a header comment.

Usage:
    python3 tools/sync_effigy_constants.py [--check]

    --check     Don't rewrite the file. Exit non-zero if regen would change it.
                Useful for CI / pre-commit hooks.

The companion script `tools/check_effigy_bridge_sync.py` does end-to-end
verification (parses both files, diffs them); this one is the one-way
generator that produces the Python file from the C header.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT     = Path(__file__).resolve().parent.parent
C_HEADER_PATH = REPO_ROOT.parent / "EFFIGY/firmware/src/macrobrute_bridge.h"
OUTPUT_PATH   = REPO_ROOT / "firmware/pico/_effigy_constants.py"


# Map C namespace name → Python prefix used in MACROBRUTE-side code.
NAMESPACES = (
    ("reg",   "REG"),
    ("event", "EVENT"),
    ("err",   "ERR"),
    ("btn",   "BTN"),
)


# Hand-curated map: C name (sans 'k' prefix, snake-cased) → Python uppercase name.
# This avoids surprise renames; if a constant in the C header doesn't appear
# in this map, the generator emits a literal CamelCase-stripped name and warns.
NAME_MAP = {
    # reg::
    "DeviceId":         "DEVICE_ID",
    "FwVersionMajor":   "FW_VERSION_MAJOR",
    "FwVersionMinor":   "FW_VERSION_MINOR",
    "Capabilities":     "CAPABILITIES",
    "Heartbeat":        "HEARTBEAT",
    "Mass":             "MASS",
    "Entropy":          "ENTROPY",
    "Position":         "POSITION",
    "Texture":          "TEXTURE",
    "Mix":              "MIX",
    "Fold":             "FOLD",
    "Filter":           "FILTER",
    "Reverb":           "REVERB",
    "Crush":            "CRUSH",
    "DestructionMacro": "DESTRUCTION_MACRO",
    "EngineIndex":      "ENGINE_INDEX",
    "HarmonizerInt":    "HARMONIZER_INT",
    "MicroLfoRate":     "MICRO_LFO_RATE",
    "EnvShape":         "ENV_SHAPE",
    "TrigVoice1":       "TRIG_VOICE_1",
    "Freeze":           "FREEZE",
    "PanelOverride":    "PANEL_OVERRIDE",
    "LevelL":           "LEVEL_L",
    "LevelR":           "LEVEL_R",
    "ClipFlags":        "CLIP_FLAGS",
    "EngineName":       "ENGINE_NAME",
    "PresetSlot":       "PRESET_SLOT",
    "CpuLoad":          "CPU_LOAD",
    "GrainBufferFill":  "GRAIN_BUFFER_FILL",
    "FreezeState":      "FREEZE_STATE",
    "EnvStage":         "ENV_STAGE",
    "CvOut1Value":      "CV_OUT_1_VALUE",
    "CvOut2Value":      "CV_OUT_2_VALUE",
    "EventCount":       "EVENT_COUNT",
    "EventPop":         "EVENT_POP",
    "EventClear":       "EVENT_CLEAR",
    "PairActive":       "PAIR_ACTIVE",
    "ClockMaster":      "CLOCK_MASTER",
    "MenuOwner":        "MENU_OWNER",
    "FocusOwner":       "FOCUS_OWNER",
    "ClockTick":        "CLOCK_TICK",
    "ClockBpm":         "CLOCK_BPM",
    "TransportState":   "TRANSPORT_STATE",
    "PresetRecall":     "PRESET_RECALL",
    "SrcCount":         "SRC_COUNT",
    "SrcName0":         "SRC_NAME",  # base of the per-slot block
    "ErrorStatus":      "ERROR_STATUS",
    "ResetBridge":      "RESET_BRIDGE",
    # event::
    "Encoder": "ENCODER",
    "Button":  "BUTTON",
    "Preset":  "PRESET",
    "Engine":  "ENGINE",
    "Clip":    "CLIP",
    "Panel":   "PANEL",
    # err::
    "Ok":                  "OK",
    "BadRegister":         "BAD_REGISTER",
    "WriteToReadOnly":     "WRITE_TO_READONLY",
    "ReadFromWriteOnly":   "READ_FROM_WRITEONLY",
    "EventQueueOverflow":  "EVENT_QUEUE_OVERFLOW",
    "HeartbeatTimeout":    "HEARTBEAT_TIMEOUT",
    # btn::
    "Frz":         "FRZ",
    "Page":        "PAGE",
    "EncoderPush": "ENCODER_PUSH",
}


def parse_c_namespace(text: str, namespace: str) -> list[tuple[str, int]]:
    """Return [(c_name, value), ...] preserving source order."""
    open_pat = re.compile(rf"namespace\s+{namespace}\s*\{{")
    m = open_pat.search(text)
    if not m:
        return []
    depth = 1
    i = m.end()
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    body = text[m.end():i]
    pat = re.compile(r"constexpr\s+uint8_t\s+k([A-Za-z0-9]+)\s*=\s*(0x[0-9a-fA-F]+)")
    return [(name, int(val, 16)) for name, val in pat.findall(body)]


def get_header_revision() -> str:
    """Best-effort: return git short-sha + dirty flag for the C header."""
    try:
        sha = subprocess.check_output(
            ["git", "-C", str(C_HEADER_PATH.parent), "log", "-n", "1", "--format=%h", "--", str(C_HEADER_PATH)],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        if not sha:
            return "unknown"
        # Check dirty
        diff = subprocess.run(
            ["git", "-C", str(C_HEADER_PATH.parent), "diff", "--quiet", "--", str(C_HEADER_PATH)],
            stderr=subprocess.DEVNULL,
        )
        return sha + ("-dirty" if diff.returncode != 0 else "")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def python_name(c_name: str) -> str:
    if c_name in NAME_MAP:
        return NAME_MAP[c_name]
    # Fallback: convert CamelCase → SNAKE_CASE
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", c_name).upper()
    print(f"WARNING: unmapped C name 'k{c_name}' → using fallback '{snake}'", file=sys.stderr)
    return snake


def render(text: str) -> str:
    rev = get_header_revision()
    lines: list[str] = [
        '"""EFFIGY bridge constants — GENERATED, do not edit by hand.',
        "",
        "Generated from EFFIGY/firmware/src/macrobrute_bridge.h by",
        "tools/sync_effigy_constants.py. The C header is the authoritative",
        "source of register addresses, event types, and error codes; this",
        "module mirrors them for the MACROBRUTE Pico firmware to import.",
        "",
        f"Source revision: {rev}",
        '"""',
        "",
        "from micropython import const",
        "",
    ]

    headings = {
        "reg":   "Register addresses",
        "event": "Event type tags (first byte returned by EVENT_POP at 0x61)",
        "err":   "Error codes (register ERROR_STATUS at 0xF0)",
        "btn":   "Button identifiers (event 0x02 BUTTON, byte a)",
    }
    prefixes = {ns: pfx for ns, pfx in NAMESPACES}

    for ns, pfx in NAMESPACES:
        items = parse_c_namespace(text, ns)
        if not items:
            continue
        lines.append("# " + "─" * 67)
        lines.append(f"# {headings.get(ns, ns)}")
        lines.append("# " + "─" * 67)
        # Determine name width for alignment
        py_names = [f"{pfx}_{python_name(name)}" for name, _ in items]
        max_w = max(len(n) for n in py_names) if py_names else 0
        for (c_name, value), py_full in zip(items, py_names):
            comment = ""
            if ns == "reg":
                comment = "  # 0x{:02X}".format(value)
            lines.append(f"{py_full:<{max_w}} = const(0x{value:02X}){comment}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="Verify file is up to date; exit 1 if not.")
    args = parser.parse_args()

    if not C_HEADER_PATH.exists():
        print(f"ERROR: missing {C_HEADER_PATH}")
        print("       (sibling EFFIGY project not found)")
        return 1

    text = C_HEADER_PATH.read_text()
    rendered = render(text)

    if args.check:
        if not OUTPUT_PATH.exists():
            print(f"FAIL: {OUTPUT_PATH} does not exist; run without --check to generate.")
            return 1
        existing = OUTPUT_PATH.read_text()
        # Ignore the source-revision line for staleness check (changes constantly)
        def normalize(s: str) -> str:
            return re.sub(r"^Source revision:.*$", "Source revision: <stripped>", s, flags=re.M)
        if normalize(existing) != normalize(rendered):
            print(f"FAIL: {OUTPUT_PATH} is out of sync with C header.")
            print("      Re-run: python3 tools/sync_effigy_constants.py")
            return 1
        print(f"OK: {OUTPUT_PATH} matches C header.")
        return 0

    OUTPUT_PATH.write_text(rendered)
    print(f"Wrote {OUTPUT_PATH} ({rendered.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
