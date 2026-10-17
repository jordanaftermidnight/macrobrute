"""Doc-vs-firmware consistency checker. Run: python3 tools/check_docs.py"""
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.hwdata.pico import FIRMWARE_ROLES, PICO_USABLE_GP

ROW = re.compile(r"^\|\s*GP(\d+)\s*\|[^|]*\|\s*([^|]+)\|", re.M)
# "GP23", "GP 23", "GP23/24/25", "GP2, 3, 6", "GP23-25", "GP23–GP25"
GP_LIST = re.compile(r"\bGP\s*(\d+)((?:\s*(?:[,/]|-|\u2013)\s*(?:GP\s*)?\d+)*)")
_GP_TAIL = re.compile(r"([,/]|-|\u2013)\s*(?:GP\s*)?(\d+)")
NOT_EXPOSED = (23, 24, 25, 29)
SPARE_WORDS = re.compile(r"\b(spare|free|available|unused)\b|GPIOs", re.I)

# Expected wording per GP, matching firmware roles in FIRMWARE_ROLES.
ROLE_HINTS = {
    0: "UART0 TX", 1: "UART0 RX", 2: "OLED SCK", 3: "OLED MOSI",
    4: "OLED DC", 5: "OLED RES",
    19: "Aux output 1", 20: "Aux output 2", 6: "Aux output 3", 7: "Aux output 4",
    8: "RGB LED R", 9: "RGB LED G", 10: "RGB LED B", 11: "Gate input",
    12: "Tap button", 13: "Encoder switch", 14: "Encoder CLK",
    15: "Encoder DT", 16: "Clock divider out 1", 17: "Clock divider out 2",
    18: "Clock divider out 3",
    21: "Clock input", 22: "Clock output",
}


def gp_numbers(line):
    """All GP numbers named in a line, expanding lists and ranges."""
    found = set()
    for m in GP_LIST.finditer(line):
        prev = int(m.group(1))
        found.add(prev)
        for op, num in _GP_TAIL.findall(m.group(2)):
            n = int(num)
            if op in ("-", "\u2013") and prev <= n <= prev + 40:
                found.update(range(prev, n + 1))
            else:
                found.add(n)
            prev = n
    return found


def _hint_matches(hint, func):
    # "Aux output 1" must not match "Aux output 10"; numbered hints are exact.
    return re.search(re.escape(hint.lower()) + r"(?!\d)", func.lower()) is not None


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
        found = gp_numbers(line)
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
        if hint and gp in fw and not _hint_matches(hint, func):
            problems.append(f"GP{gp} row says '{func}', firmware role is '{hint}'")
    return problems


# lines that describe history or say a pin is NOT spare are fine
_ALLOW_SPARE = re.compile(
    r"historical|superseded|stale|legacy|archiv|shelved|\bwas\b|\bwere\b|went to|"
    r"\b(not|no|none|never)\b[^.;:]{0,60}\b(free|spare|available|unused)\b|"
    r"\b(free|spare|available|unused)\b[^.;]{0,12}\b(not|no)\b", re.I)


def check_spare_claims(docs):
    """docs: {filename: text}. Flag prose lines that call an allocated GP free or spare."""
    fw = _flat_firmware_gps()
    problems = []
    for f, t in docs.items():
        for n, line in enumerate(t.splitlines(), 1):
            if line.lstrip().startswith("|") or not SPARE_WORDS.search(line):
                continue
            if _ALLOW_SPARE.search(line):
                continue
            for gp in sorted(gp_numbers(line) & fw):
                problems.append(f"{f}:{n}: GP{gp} is allocated in firmware but the line calls "
                                f"it spare/free: {line.strip()[:80]}")
    return problems


def doc_files(root):
    """Current docs: docs/**/*.md (not legacy, not superpowers), schematics/*.md, README.md."""
    out = [p for p in sorted(root.glob("docs/**/*.md"))
           if not ({"superpowers", "legacy"} & set(p.relative_to(root).parts))]
    out += sorted(root.glob("schematics/*.md"))
    if (root / "README.md").exists():
        out.append(root / "README.md")
    return out


_CONTEXT = re.compile(r"bridge|Pico|\bGP[01]\b|DB-9", re.I)
_UART1 = re.compile(r"P0\.1[56]\b")
_UART0 = re.compile(r"P0\.[23]\b")
# UART0 is P0.2 / P0.3 (pins 98 / 99, DATASHEETS (b)); P0.0 / P0.1 are not UART0
_WRONG_UART0 = re.compile(r"P0\.[01]\b")
_UART0_WORD = re.compile(r"UART0|TXD0|RXD0", re.I)


def check_lpc_uart_claims(docs):
    """docs: {filename: text}. Flag if the Pico bridge UART is described two ways."""
    uart1, uart0, wrong = [], [], []
    for f, t in docs.items():
        for n, line in enumerate(t.splitlines(), 1):
            if _WRONG_UART0.search(line) and _UART0_WORD.search(line):
                wrong.append(f"{f}:{n}")
            if not _CONTEXT.search(line):
                continue
            if _UART1.search(line):
                uart1.append(f"{f}:{n}")
            if _UART0.search(line):
                uart0.append(f"{f}:{n}")
    problems = [f"P0.0/P0.1 claimed as UART0 (UART0 is P0.2/P0.3) at {w}" for w in wrong]
    if uart1 and uart0:
        problems.append(
            f"bridge UART conflict: UART1 (P0.15/16) at {uart1}, UART0 (P0.2/3) at {uart0}")
    return problems


def main():
    root = Path(__file__).resolve().parents[1]
    docs = {str(p.relative_to(root)): p.read_text() for p in sorted(root.glob("docs/**/*.md"))
            if "superpowers" not in p.relative_to(root).parts}
    problems = []
    cmap = docs.get("docs/MACROBRUTE_CONNECTION_MAP.md", "")
    problems += check_connection_map(cmap)
    # docs/legacy carries a DEPRECATED banner and keeps the old pin claims on purpose
    current = {k: v for k, v in docs.items() if not k.startswith("docs/legacy/")}
    problems += check_lpc_uart_claims(current)
    problems += check_spare_claims({str(f.relative_to(root)): f.read_text() for f in doc_files(root)})
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
