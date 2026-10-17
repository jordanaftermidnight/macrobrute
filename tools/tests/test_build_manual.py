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


def test_oled_captions_describe_the_spi_baseline():
    from tools.build_manual import SVG_DESCRIPTIONS
    keys = ["schematics/phase0_wiring_schematic.svg", "schematics/phase0_breadboard.svg",
            "schematics/pico_pinout_diagram.svg"]
    for k in keys:
        text = SVG_DESCRIPTIONS[k]
        for bad in ("I²C", "I2C", "0x3C", "SDA", "SCL", "SH1106 likely"):
            assert bad not in text, f"{k} caption still contains {bad!r}"
        assert "SPI" in text, k
    for k in keys[:2]:
        assert "pin order" in SVG_DESCRIPTIONS[k] and "UNVERIFIED" in SVG_DESCRIPTIONS[k], k


# SVG text that shows the withdrawn design: supply or I2C on DB-9 B, or the dropped strip OLED
_STALE_SVG = (r"7:\s*\+12V|\(Inputs \+ Power\)|via DB-9 B|SDA|0x3D|strip OLED|I²C from Pico"
              r"|DB-9, Power Distribution")


def _svg_texts(path):
    import re
    return " ".join(re.findall(r">([^<]+)<", path.read_text(encoding="utf-8")))


def test_captions_of_withdrawn_designs_are_marked_stale():
    import re
    from tools.build_manual import PROJECT, SVG_DESCRIPTIONS, SVG_MAP
    bad = []
    for svgs in SVG_MAP.values():
        for svg in svgs:
            path = PROJECT / svg
            if not path.exists():
                continue
            cap = SVG_DESCRIPTIONS.get(svg, "")
            shows_old = re.search(_STALE_SVG, _svg_texts(path), re.I)
            says_old = (("±12" in cap or "12 V" in cap) and "DB-9 B" in cap) or (
                re.search(r"strip.OLED", cap, re.I) and "dropped" not in cap.lower())
            if (shows_old or says_old) and not cap.startswith("STALE"):
                bad.append(svg)
    assert bad == []


def test_db9_caption_does_not_call_the_old_map_frozen():
    from tools.build_manual import SVG_DESCRIPTIONS
    cap = SVG_DESCRIPTIONS["schematics/db9_connector_diagram.svg"]
    assert cap.startswith("STALE") and "NO supply on the cable" in cap
