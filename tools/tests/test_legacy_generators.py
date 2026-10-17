import re
from pathlib import Path

import tools.diagrams.phase0_breadboard as a
import tools.diagrams.phase0_wiring as b
import tools.diagrams.pico_pinout as c
import tools.diagrams.pico_protection as d
import tools.diagrams.power_chain as e

TOOLS = Path(__file__).resolve().parents[1]


def test_legacy_generators_do_not_write_new_card_outputs():
    stems = [m.OUT.stem for m in (a, b, c, d, e)]
    assert len(stems) == 5
    for path in TOOLS.glob("generate_*.py"):
        text = path.read_text()
        for stem in stems:
            hit = re.search(r"(?<![A-Za-z0-9_])" + re.escape(stem) + r"(?![A-Za-z0-9_])", text)
            assert not hit, f"{path.name} still mentions {stem}"
