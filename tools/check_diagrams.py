"""Net validator for diagram netlists. Run: python3 tools/check_diagrams.py"""
import importlib
import pkgutil
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.hwdata.pico import PICO_USABLE_GP

CABLE_DIGITAL_PREFIXES = ("CABLE_UART", "CABLE_I2C", "CABLE_CLK")


def validate_nets(nets, rails):
    """nets: {name: [(part, pin), ...]}; rails: {net name: volts}. Returns problems."""
    problems, seen = [], {}
    for rail in rails:
        if rail not in nets:
            problems.append(f"rail {rail} matches no net")
    for name, raw_ends in nets.items():
        ends = []
        for e in raw_ends:
            if not isinstance(e, (tuple, list)) or len(e) != 2:
                problems.append(f"net {name} endpoint {e!r} must be a (part, pin) pair")
                continue
            # normalise spelling so case/space variants cannot dodge GPIO rules
            ends.append((str(e[0]).upper(), str(e[1]).upper().replace(" ", "")))
        if len(raw_ends) < 2:
            problems.append(f"net {name} is floating")
        if name.startswith(CABLE_DIGITAL_PREFIXES):
            if not any(part == "R" for part, _ in ends):
                problems.append(f"net {name} crosses the cable with no series resistor")
        gps = [p for part, p in ends if part == "PICO" and p.startswith("GP")]
        # the same GP appearing twice on the SAME net is allowed (several taps)
        for gp in gps:
            if not gp[2:].isdigit() or int(gp[2:]) not in PICO_USABLE_GP:
                problems.append(f"{gp} is not an exposed Pico GPIO (net {name})")
            if gp in seen and seen[gp] != name:
                problems.append(f"{gp} used on nets {seen[gp]} and {name}")
            seen[gp] = name
        if gps and rails.get(name, 0) > 3.3:
            if not any(part in ("SHIFT", "DIV") for part, _ in ends):
                problems.append(f"net {name} is {rails[name]} V into a Pico GPIO with no shifter")
    return problems


def check_all():
    """Validate every tools.diagrams.* module that exposes NETS and RAILS."""
    import tools.diagrams as pkg
    problems = []
    for info in pkgutil.iter_modules(pkg.__path__):
        mod = importlib.import_module(f"tools.diagrams.{info.name}")
        if hasattr(mod, "NETS") and hasattr(mod, "RAILS"):
            problems += [f"{info.name}: {p}" for p in validate_nets(mod.NETS, mod.RAILS)]
    return problems


def main():
    problems = check_all()
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
