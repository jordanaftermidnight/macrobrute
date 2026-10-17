"""Net validator for diagram netlists."""
from tools.hwdata.pico import PICO_USABLE_GP

CABLE_DIGITAL_PREFIXES = ("CABLE_UART", "CABLE_I2C", "CABLE_CLK")


def validate_nets(nets, rails):
    """nets: {name: [(part, pin), ...]}; rails: {net name: volts}. Returns problems."""
    problems, seen = [], {}
    for name, ends in nets.items():
        if len(ends) < 2:
            problems.append(f"net {name} is floating")
        if name.startswith(CABLE_DIGITAL_PREFIXES):
            if not any(part == "R" for part, _ in ends):
                problems.append(f"net {name} crosses the cable with no series resistor")
        gps = [p for part, p in ends if part == "PICO" and p.startswith("GP")]
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
