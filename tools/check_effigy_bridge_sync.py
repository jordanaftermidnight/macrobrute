#!/usr/bin/env python3
"""Verify the EFFIGY bridge register map agrees on both sides.

Compares register addresses defined in:
    firmware/pico/effigy_bridge.py     (Python, MACROBRUTE side)
    EFFIGY/firmware/src/macrobrute_bridge.h  (C++, EFFIGY side)

Fails (exit 1) if any address differs or if registers exist on one side
that are missing on the other.

Run before each commit that touches either file. Add to CI if available.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PYTHON_PATH = Path(__file__).resolve().parent.parent / "firmware/pico/effigy_bridge.py"
C_HEADER_PATH = Path(__file__).resolve().parent.parent.parent / "EFFIGY/firmware/src/macrobrute_bridge.h"


# Map Python REG_* names → C++ reg::k* equivalent (different naming convention,
# same numeric values are the contract).
NAME_MAP = {
    # 0x00–0x0F device / pair management
    "REG_DEVICE_ID":        "kDeviceId",
    "REG_FW_VERSION_MAJOR": "kFwVersionMajor",
    "REG_FW_VERSION_MINOR": "kFwVersionMinor",
    "REG_CAPABILITIES":     "kCapabilities",
    "REG_HEARTBEAT":        "kHeartbeat",
    # 0x10–0x3F params
    "REG_MASS":              "kMass",
    "REG_ENTROPY":           "kEntropy",
    "REG_POSITION":          "kPosition",
    "REG_TEXTURE":           "kTexture",
    "REG_MIX":               "kMix",
    "REG_FOLD":              "kFold",
    "REG_FILTER":            "kFilter",
    "REG_REVERB":            "kReverb",
    "REG_CRUSH":             "kCrush",
    "REG_DESTRUCTION_MACRO": "kDestructionMacro",
    "REG_ENGINE_INDEX":      "kEngineIndex",
    "REG_HARMONIZER_INT":    "kHarmonizerInt",
    "REG_MICRO_LFO_RATE":    "kMicroLfoRate",
    "REG_ENV_SHAPE":         "kEnvShape",
    "REG_TRIG_VOICE_1":      "kTrigVoice1",
    "REG_FREEZE":            "kFreeze",
    "REG_PANEL_OVERRIDE":    "kPanelOverride",
    # 0x40–0x5F telemetry
    "REG_LEVEL_L":            "kLevelL",
    "REG_LEVEL_R":            "kLevelR",
    "REG_CLIP_FLAGS":         "kClipFlags",
    "REG_ENGINE_NAME":        "kEngineName",
    "REG_PRESET_SLOT":        "kPresetSlot",
    "REG_CPU_LOAD":           "kCpuLoad",
    "REG_GRAIN_BUFFER_FILL":  "kGrainBufferFill",
    "REG_FREEZE_STATE":       "kFreezeState",
    "REG_ENV_STAGE":          "kEnvStage",
    "REG_CV_OUT_1_VALUE":     "kCvOut1Value",
    "REG_CV_OUT_2_VALUE":     "kCvOut2Value",
    # 0x60–0x7F events
    "REG_EVENT_COUNT": "kEventCount",
    "REG_EVENT_POP":   "kEventPop",
    "REG_EVENT_CLEAR": "kEventClear",
    # 0x80–0x9F routing
    "REG_PAIR_ACTIVE":     "kPairActive",
    "REG_CLOCK_MASTER":    "kClockMaster",
    "REG_MENU_OWNER":      "kMenuOwner",
    "REG_FOCUS_OWNER":     "kFocusOwner",
    "REG_CLOCK_TICK":      "kClockTick",
    "REG_CLOCK_BPM":       "kClockBpm",
    "REG_TRANSPORT_STATE": "kTransportState",
    "REG_PRESET_RECALL":   "kPresetRecall",
    # 0xA0–0xBF cross-mod (MACROBRUTE Python uses REG_SRC_NAME for the base address;
    # the C side names it kSrcName0)
    "REG_SRC_COUNT": "kSrcCount",
    "REG_SRC_NAME":  "kSrcName0",
    # 0xF0–0xFF diagnostics
    "REG_ERROR_STATUS": "kErrorStatus",
    "REG_RESET_BRIDGE": "kResetBridge",
}


def parse_python_registers(path: Path) -> dict[str, int]:
    return parse_python_prefix(path, "REG")


def parse_c_namespace(path: Path, namespace: str) -> dict[str, int]:
    """Parse `constexpr uint8_t kFoo = 0xXX;` declarations inside a given namespace block."""
    text = path.read_text()
    # Find the opening of the namespace, then everything up to its closing brace.
    open_pat = re.compile(rf"namespace\s+{namespace}\s*\{{")
    m = open_pat.search(text)
    if not m:
        return {}
    # Walk forward, tracking brace depth, until we close the namespace.
    depth = 1
    i = m.end()
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    body = text[m.end():i]
    pat = re.compile(r"constexpr\s+uint8_t\s+(k[A-Za-z0-9]+)\s*=\s*(0x[0-9a-fA-F]+)")
    return {name: int(val, 16) for name, val in pat.findall(body)}


def parse_python_prefix(path: Path, prefix: str) -> dict[str, int]:
    """Parse `NAME = const(0xXX)` (or `= 0xXX`) for a given name prefix."""
    text = path.read_text()
    pat = re.compile(rf"^({prefix}_[A-Z0-9_]+)\s*=\s*(?:const\()?\s*(0x[0-9a-fA-F]+)", re.M)
    return {name: int(val, 16) for name, val in pat.findall(text)}


EVENT_NAME_MAP = {
    "EVENT_ENCODER": "kEncoder",
    "EVENT_BUTTON":  "kButton",
    "EVENT_PRESET":  "kPreset",
    "EVENT_ENGINE":  "kEngine",
    "EVENT_CLIP":    "kClip",
    "EVENT_PANEL":   "kPanel",
}

ERROR_NAME_MAP = {
    "ERR_OK":                   "kOk",
    "ERR_BAD_REGISTER":         "kBadRegister",
    "ERR_WRITE_TO_READONLY":    "kWriteToReadOnly",
    "ERR_READ_FROM_WRITEONLY":  "kReadFromWriteOnly",
    "ERR_EVENT_QUEUE_OVERFLOW": "kEventQueueOverflow",
    "ERR_HEARTBEAT_TIMEOUT":    "kHeartbeatTimeout",
}


def cross_check(py_values: dict[str, int],
                c_values: dict[str, int],
                name_map: dict[str, str],
                kind: str) -> list[str]:
    errors: list[str] = []
    for py_name, c_name in name_map.items():
        if py_name not in py_values:
            errors.append(f"{kind}: missing in Python: {py_name}")
            continue
        if c_name not in c_values:
            errors.append(f"{kind}: missing in C header: {c_name}")
            continue
        if py_values[py_name] != c_values[c_name]:
            errors.append(
                f"{kind} MISMATCH: {py_name}=0x{py_values[py_name]:02X} "
                f"but {c_name}=0x{c_values[c_name]:02X}"
            )
    py_unmapped = set(py_values) - set(name_map)
    c_unmapped = set(c_values) - set(name_map.values())
    if py_unmapped:
        errors.append(f"{kind}: Python has unmapped: {sorted(py_unmapped)}")
    if c_unmapped:
        errors.append(f"{kind}: C header has unmapped: {sorted(c_unmapped)}")
    return errors


def main() -> int:
    if not PYTHON_PATH.exists():
        print(f"FAIL: missing {PYTHON_PATH}")
        return 1
    if not C_HEADER_PATH.exists():
        print(f"INFO: sibling EFFIGY project not present at {C_HEADER_PATH}")
        print("      Skipping cross-check.")
        return 0

    py_regs   = parse_python_registers(PYTHON_PATH)
    py_events = parse_python_prefix(PYTHON_PATH, "EVENT")
    py_errs   = parse_python_prefix(PYTHON_PATH, "ERR")

    c_regs   = parse_c_namespace(C_HEADER_PATH, "reg")
    c_events = parse_c_namespace(C_HEADER_PATH, "event")
    c_errs   = parse_c_namespace(C_HEADER_PATH, "err")

    all_errors: list[str] = []
    all_errors += cross_check(py_regs,   c_regs,   NAME_MAP,        "register")
    all_errors += cross_check(py_events, c_events, EVENT_NAME_MAP,  "event")
    all_errors += cross_check(py_errs,   c_errs,   ERROR_NAME_MAP,  "error")

    if all_errors:
        print("EFFIGY bridge sync FAILED — drift detected:")
        for e in all_errors:
            print(f"  • {e}")
        return 1

    total = len(NAME_MAP) + len(EVENT_NAME_MAP) + len(ERROR_NAME_MAP)
    print(f"EFFIGY bridge sync OK — {total} symbols verified "
          f"({len(NAME_MAP)} registers, {len(EVENT_NAME_MAP)} events, "
          f"{len(ERROR_NAME_MAP)} errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
