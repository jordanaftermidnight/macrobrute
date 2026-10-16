"""Doc-vs-firmware consistency checker. Run: python3 tools/check_docs.py"""
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.hwdata.pico import FIRMWARE_ROLES, PICO_USABLE_GP

ROW = re.compile(r"^\|\s*GP(\d+)\s*\|[^|]*\|\s*([^|]+)\|", re.M)
GP_LIST = re.compile(r"\bGP(\d+(?:\s*[,/]\s*\d+)*)")
NOT_EXPOSED = (23, 24, 25, 29)
SPARE_WORDS = re.compile(r"\b(spare|free|available|unused)\b|GPIOs", re.I)

# Expected wording per GP, matching firmware roles in FIRMWARE_ROLES.
ROLE_HINTS = {
    0: "UART0 TX", 1: "UART0 RX", 2: "I²C1 SDA", 3: "I²C1 SCL",
    4: "I²C0 SDA", 5: "I²C0 SCL", 6: "Aux output", 7: "Aux output",
    8: "RGB LED R", 9: "RGB LED G", 10: "RGB LED B", 11: "EFFIGY INT",
    12: "Tap button", 13: "Encoder switch", 14: "Encoder CLK",
    15: "Encoder DT", 16: "Clock divider", 17: "Clock divider",
    18: "Clock divider", 19: "Aux output", 20: "Aux output",
    21: "Clock input", 22: "Clock output",
}


def _flat_firmware_gps():
    gps = set()
    for v in FIRMWARE_ROLES.values():
        gps.update(v if isinstance(v, tuple) else (v,))
    return gps


def check_connection_map(text):
    problems = []
    for line in text.splitlines():
        if not SPARE_WORDS.search(line):
            continue
        found = set()
        for m in GP_LIST.finditer(line):
            found.update(int(n) for n in re.findall(r"\d+", m.group(1)))
        for gp in NOT_EXPOSED:
            if gp in found:
                problems.append(
                    f"GP{gp} is not exposed on the Pico but is listed as spare/available: {line.strip()[:90]}")
    fw = _flat_firmware_gps()
    for m in ROW.finditer(text):
        gp, func = int(m.group(1)), m.group(2).strip()
        if gp not in PICO_USABLE_GP:
            problems.append(f"GP{gp} row exists but GP{gp} is not a usable Pico pin")
            continue
        hint = ROLE_HINTS.get(gp)
        if hint and gp in fw and hint.lower() not in func.lower():
            problems.append(f"GP{gp} row says '{func}', firmware role is '{hint}'")
    return problems


_CONTEXT = re.compile(r"bridge|Pico|\bGP[01]\b|DB-9", re.I)
_UART1 = re.compile(r"P0\.1[56]\b")
_UART0 = re.compile(r"P0\.[23]\b")


def check_lpc_uart_claims(docs):
    """docs: {filename: text}. Flag if the Pico bridge UART is described two ways."""
    uart1, uart0 = [], []
    for f, t in docs.items():
        for n, line in enumerate(t.splitlines(), 1):
            if not _CONTEXT.search(line):
                continue
            if _UART1.search(line):
                uart1.append(f"{f}:{n}")
            if _UART0.search(line):
                uart0.append(f"{f}:{n}")
    if uart1 and uart0:
        return [f"bridge UART conflict: UART1 (P0.15/16) at {uart1}, UART0 (P0.2/3) at {uart0}"]
    return []


def main():
    root = Path(__file__).resolve().parents[1]
    docs = {str(p.relative_to(root)): p.read_text() for p in sorted(root.glob("docs/**/*.md"))
            if "superpowers" not in p.relative_to(root).parts}
    problems = []
    cmap = docs.get("docs/MACROBRUTE_CONNECTION_MAP.md", "")
    problems += check_connection_map(cmap)
    problems += check_lpc_uart_claims(docs)
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
