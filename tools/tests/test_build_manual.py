from pathlib import Path
from tools.build_manual import missing_svgs


def test_reports_missing_svg(tmp_path):
    (tmp_path / "a.svg").write_text("<svg/>")
    m = {"x.md": ["a.svg", "gone.svg"]}
    assert missing_svgs(m, tmp_path) == ["gone.svg"]


def test_new_card_captions_have_no_stale_text():
    from tools.build_manual import SVG_DESCRIPTIONS
    keys = ["schematics/phase0_wiring_schematic.svg", "schematics/phase0_breadboard.svg",
            "schematics/pico_pinout_diagram.svg", "schematics/pico_power_protection.svg",
            "schematics/power_regulation_diagram.svg"]
    for k in keys:
        text = SVG_DESCRIPTIONS[k]
        for bad in ("0x3D", "0.91", "strip", "1N5817"):
            assert bad not in text, f"{k} caption still contains {bad!r}"
