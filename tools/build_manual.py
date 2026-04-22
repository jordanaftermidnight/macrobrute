#!/usr/bin/env python3
"""
MACROBRUTE Interactive Manual Builder

Reads all project markdown docs and generates a single-page HTML manual
with sidebar navigation, full-text search, quick-reference tabs, and
collapsible document sections. Zero dependencies beyond Python 3.

Usage:
    python3 tools/build_manual.py
    open manual.html
"""

import re
import html as _html
from pathlib import Path
from datetime import date

PROJECT = Path(__file__).resolve().parent.parent
OUTPUT = PROJECT / "Macrobrute Manual.html"

# ─── SVG Mappings ───────────────────────────────────────────────────
# Maps markdown files to their associated SVG layout diagrams
SVG_MAP = {
    "schematics/wiring_diagram.md": [
        "schematics/system_architecture_block.svg",
        "schematics/audio_signal_flow.svg",
        "schematics/cv_control_flow.svg",
        "schematics/signal_flow_overview.svg",
        "schematics/wiring_overview.svg",
        "schematics/wiring_internal.svg",
        "schematics/wiring_power_distribution.svg",
        "schematics/interconnect_wiring.svg",
        "schematics/db9_connector_diagram.svg",
        "schematics/testpoints_map.svg",
        "schematics/midi_interface_circuit.svg",
    ],
    "schematics/breakout_pcb.md": [
        "schematics/wiring_output_buffer.svg",
        "schematics/wiring_gate_buffer.svg",
        "schematics/wiring_vactrol_driver.svg",
        "schematics/wiring_cv_protection.svg",
        "schematics/breakout_layout.svg",
        "schematics/power_distribution.svg",
        "schematics/output_buffer_board.svg",
        "schematics/power_regulation_diagram.svg",
    ],
    "schematics/pico_pinout.md": [
        "schematics/pico_pinout_diagram.svg",
        "schematics/lpc2361_pinout_diagram.svg",
    ],
    "schematics/ic_pinout_reference.md": [
        "schematics/ic_pinout_tl074.svg",
        "schematics/ic_pinout_tl072.svg",
        "schematics/ic_pinout_cd40106.svg",
        "schematics/ic_pinout_cd4051.svg",
        "schematics/ic_pinout_cd4024.svg",
        "schematics/ic_pinout_cd4066.svg",
        "schematics/ic_pinout_lm358.svg",
        "schematics/ic_pinout_pt2399.svg",
    ],
    "schematics/breakout_stripboard.md": [
        "schematics/breakout_layout.svg",
        "schematics/zone_layout_stripboard.svg",
    ],
    "schematics/expander_circuits.md": [
        "schematics/noise_generator_schematic.svg",
        "schematics/lfo_schematic.svg",
        "schematics/sah_schematic.svg",
        "schematics/clock_divider_schematic.svg",
        "schematics/slew_limiter_schematic.svg",
        "schematics/attenuverter_schematic.svg",
        "schematics/dip_pinout_reference.svg",
    ],
    "schematics/expander_stripboard.md": [
        "schematics/expander_noise.svg",
        "schematics/expander_lfo.svg",
        "schematics/expander_clockdiv.svg",
        "schematics/expander_sah.svg",
        "schematics/expander_slew.svg",
        "schematics/expander_attenuverter.svg",
        "schematics/expander_power_distribution.svg",
    ],
    "schematics/CIRCUIT_REVIEW.md": [
        "schematics/led_driver_array_schematic.svg",
        "schematics/vactrol_full_schematic.svg",
        "schematics/input_protection_schematic.svg",
        "schematics/esd_protection_schematic.svg",
        "schematics/cv_input_protection_diagram.svg",
        "schematics/cd4051_multiplexer.svg",
        "schematics/buffered_multiple_schematic.svg",
        "schematics/manual_gate_button_schematic.svg",
    ],
    "schematics/touch_plates.md": [
        "schematics/touch_plate_schematic.svg",
        "schematics/touch_test_board.svg",
        "schematics/touch_plate_redesign.svg",
    ],
    "schematics/jf33_cv_control.md": [
        "schematics/pt2399_cv_control_schematic.svg",
        "schematics/jf33_integration_schematic.svg",
    ],
    "schematics/dso138_input_protection.md": [
        "schematics/dso138_analog_frontend.svg",
    ],
}

# ─── Document Organization ──────────────────────────────────────────

QUICK_REF = [
    ("Test Points", "tp", "docs/hardware/MACROBRUTE_TEST_POINTS_VERIFIED.md"),
    ("Pico GPIO", "gpio", "schematics/pico_pinout.md"),
    ("Touch Bends", "bends", "docs/mods/touch_bend_specs.md"),
]

SECTIONS = [
    ("1. Getting Started", "start", [
        "docs/MACROBRUTE_INDEX.md",
    ]),
    ("2. Planning & Preparation", "plan", [
        "docs/hardware/MACROBRUTE_BOM.md",
        "docs/hardware/MACROBRUTE_SHOPPING_LIST.md",
        "docs/MACROBRUTE_MOD_SELECTION.md",
        "docs/MACROBRUTE_BUILD_PLAN.md",
    ]),
    ("3. System Architecture", "arch", [
        "docs/MACROBRUTE_CONNECTION_MAP.md",
        "schematics/expander_block_diagram.md",
    ]),
    ("4. Interconnect & Wiring", "wire", [
        "schematics/wiring_diagram.md",
    ]),
    ("5. Breakout Board", "breakout", [
        "schematics/breakout_pcb.md",
        "schematics/breakout_stripboard.md",
        "schematics/pico_pinout.md",
    ]),
    ("6. Expander Modules", "expander", [
        "schematics/expander_circuits.md",
        "schematics/expander_stripboard.md",
    ]),
    ("7. Protection & Safety", "protection", [
        "schematics/CIRCUIT_REVIEW.md",
    ]),
    ("8. Control & Interface", "control", [
        "schematics/touch_plates.md",
        "schematics/jf33_cv_control.md",
        "docs/firmware/MACROBRUTE_FIRMWARE_PROJECT.md",
        "docs/MACROBRUTE_FIRMWARE_MOD_PLAN.md",
    ]),
    ("9. Hardware Reference", "hw", [
        "docs/hardware/MACROBRUTE_TEST_POINTS_VERIFIED.md",
        "schematics/ic_pinout_reference.md",
    ]),
    ("10. Mods & Extensions", "mods", [
        "docs/mods/touch_bend_specs.md",
        "docs/mods/microbrute_mods_guide.md",
        "docs/mods/microbrute_circuit_bending_guide.md",
        "docs/mods/deep_circuit_bending.md",
        "docs/mods/ultimate_microbrute_project.md",
    ]),
    ("11. Optional Separate Modules (Phase 7)", "optional", [
        "schematics/dso138_input_protection.md",
    ]),
    ("12. Research", "research", [
        "docs/research/additional_mods_findings.md",
        "docs/research/mbf_analysis.md",
        "docs/research/firmware_re_findings.md",
        "docs/research/pt2399_dso138_findings.md",
        "docs/firmware/lpc2361_investigation_guide.md",
        "docs/architecture/MACROBRUTE_COMPLETE_EXPANSION_MAP.md",
        "docs/architecture/MACROBRUTE_COMPREHENSIVE_RESEARCH.md",
    ]),
    ("13. Legacy & Archive", "legacy", [
        "docs/legacy/MACROBRUTE_FINAL_ARCHITECTURE.md",
        "docs/legacy/MACROBRUTE_PROJECT_HANDOFF.md",
        "docs/legacy/MACROBRUTE_EXPANDER_DB37_PINOUT.md",
        "docs/legacy/MACROBRUTE_MASTER_PLAN.md",
        "docs/legacy/MACROBRUTE_REVISED_SPEC.md",
        "docs/legacy/MACROBRUTE_V2_SPEC.md",
        "docs/legacy/MACROBRUTE_V2_COMPLETE_SPEC.md",
    ]),
]


# ─── Markdown → HTML Converter ──────────────────────────────────────

def _inline(text):
    """Convert inline markdown to HTML."""
    # Extract code spans first to protect their content
    codes = []
    def _save(m):
        codes.append(_html.escape(m.group(1)))
        return f"\x00C{len(codes)-1}\x00"
    text = re.sub(r"`([^`]+)`", _save, text)

    # Escape HTML in remaining text
    text = _html.escape(text)

    # Bold **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic *text*
    text = re.sub(r"(?<!\*)\*(.+?)\*(?!\*)", r"<em>\1</em>", text)
    # Links [text](url)
    def _link(m):
        url = _html.unescape(m.group(2))
        return f'<a href="{_html.escape(url)}" target="_blank">{m.group(1)}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, text)

    # Restore code spans
    for i, c in enumerate(codes):
        text = text.replace(f"\x00C{i}\x00", f"<code>{c}</code>")
    return text


def _table(lines):
    """Convert markdown table lines to HTML."""
    if len(lines) < 2:
        return ""
    headers = [c.strip() for c in lines[0].strip("|").split("|")]
    rows = []
    for line in lines[2:]:  # skip header + separator
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)

    out = ['<div class="table-wrap"><table><thead><tr>']
    for h in headers:
        out.append(f"<th>{_inline(h)}</th>")
    out.append("</tr></thead><tbody>")
    for row in rows:
        # Add id anchors for TP## and GP## rows
        joined = "|".join(row)
        tp = re.search(r"TP(\d+)", joined)
        gp = re.search(r"GP(\d+)", joined)
        rid = ""
        if tp:
            rid = f' id="tp-{tp.group(1)}"'
        elif gp:
            rid = f' id="gp-{gp.group(1)}"'
        out.append(f"<tr{rid}>")
        for cell in row:
            out.append(f"<td>{_inline(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def _md(text, doc_id=""):
    """Convert a full markdown document to HTML."""
    lines = text.split("\n")
    parts = []
    i = 0
    hcount = 0

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # blank
        if not s:
            i += 1
            continue

        # fenced code block
        if s.startswith("```"):
            lang = s[3:].strip()
            cls = f' class="lang-{_html.escape(lang)}"' if lang else ""
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(_html.escape(lines[i]))
                i += 1
            if i < len(lines):
                i += 1
            parts.append(f'<pre><code{cls}>{chr(10).join(code)}</code></pre>')
            continue

        # header
        m = re.match(r"^(#{1,6})\s+(.+)", s)
        if m:
            lvl = len(m.group(1))
            raw = m.group(2).strip()
            hcount += 1
            slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
            sid = f"{doc_id}--{slug}" if doc_id else slug
            parts.append(f'<h{lvl} id="{sid}">{_inline(raw)}</h{lvl}>')
            i += 1
            continue

        # hr
        if re.match(r"^[-*]{3,}\s*$", s):
            parts.append("<hr>")
            i += 1
            continue

        # table
        if s.startswith("|") and "|" in s[1:]:
            tlines = []
            while i < len(lines) and lines[i].strip().startswith("|") and "|" in lines[i].strip()[1:]:
                tlines.append(lines[i])
                i += 1
            parts.append(_table(tlines))
            continue

        # checklist
        if re.match(r"^[-*]\s+\[[ xX]\]", s):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+\[[ xX]\]", lines[i].strip()):
                lt = lines[i].strip()
                done = "[x]" in lt.lower()
                txt = re.sub(r"^[-*]\s+\[[ xX]\]\s*", "", lt)
                ck = "&#9745;" if done else "&#9744;"
                items.append(f'<li class="ck">{ck} {_inline(txt)}</li>')
                i += 1
            parts.append(f'<ul class="checklist">{"".join(items)}</ul>')
            continue

        # unordered list
        if re.match(r"^[-*]\s", s):
            items = []
            while i < len(lines) and lines[i].strip() and re.match(r"^[-*]\s", lines[i].strip()):
                items.append(f"<li>{_inline(lines[i].strip()[2:])}</li>")
                i += 1
            parts.append(f'<ul>{"".join(items)}</ul>')
            continue

        # ordered list
        if re.match(r"^\d+[.)]\s", s):
            items = []
            while i < len(lines) and lines[i].strip() and re.match(r"^\d+[.)]\s", lines[i].strip()):
                txt = re.sub(r"^\d+[.)]\s", "", lines[i].strip())
                items.append(f"<li>{_inline(txt)}</li>")
                i += 1
            parts.append(f'<ol>{"".join(items)}</ol>')
            continue

        # blockquote
        if s.startswith(">"):
            bq = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                bq.append(lines[i].strip().lstrip(">").strip())
                i += 1
            parts.append(f'<blockquote><p>{_inline(" ".join(bq))}</p></blockquote>')
            continue

        # paragraph (fallback)
        para = []
        while i < len(lines) and lines[i].strip():
            t = lines[i].strip()
            # Only break for actual markdown headers (# followed by space)
            if (re.match(r"^#{1,6}\s", t) or t.startswith("```") or t.startswith("|")
                    or re.match(r"^[-*]{3,}\s*$", t)
                    or re.match(r"^[-*]\s", t) or re.match(r"^\d+[.)]\s", t)):
                break
            para.append(t)
            i += 1
        if para:
            parts.append(f"<p>{_inline(' '.join(para))}</p>")

    return "\n".join(parts)


def _autolink(html_text):
    """Auto-link TP## and GP## references (skip inside <pre> and <a> tags)."""
    pre_re = re.compile(r"(<pre>.*?</pre>)", re.DOTALL)
    chunks = pre_re.split(html_text)

    for ci, chunk in enumerate(chunks):
        if chunk.startswith("<pre>"):
            continue
        tag_parts = re.split(r"(<[^>]+>)", chunk)
        in_a = False
        for j, p in enumerate(tag_parts):
            if re.match(r"<a[\s>]", p):
                in_a = True
            elif p == "</a>":
                in_a = False
            elif not p.startswith("<") and not in_a:
                p = re.sub(r"\bTP(\d+)\b",
                           r'<a class="ref tp" href="#tp-\1">TP\1</a>', p)
                p = re.sub(r"\bGP(\d+)\b",
                           r'<a class="ref gp" href="#gp-\1">GP\1</a>', p)
                tag_parts[j] = p
        chunks[ci] = "".join(tag_parts)
    return "".join(chunks)


# ─── Document Utilities ─────────────────────────────────────────────

def _make_id(fpath):
    p = Path(fpath)
    return re.sub(r"[^a-z0-9]+", "-", f"{p.parent.name}-{p.stem}".lower()).strip("-")


def _read(fpath):
    """Read a markdown file. Returns (title, body_without_title)."""
    full = PROJECT / fpath
    if not full.exists():
        name = Path(fpath).stem.replace("_", " ").title()
        return name, f'<p class="miss">File not found: {fpath}</p>'
    text = full.read_text(encoding="utf-8")
    lines = text.split("\n")
    for idx, line in enumerate(lines):
        m = re.match(r"^#\s+(.+)", line)
        if m:
            title = m.group(1).strip()
            rest = "\n".join(lines[idx + 1:]).lstrip("\n")
            return title, rest
    return Path(fpath).stem.replace("_", " ").title(), text


def _short(title):
    """Strip common prefixes for sidebar display."""
    for pfx in ("MACROBRUTE \u2014 ", "MACROBRUTE - ", "MACROBRUTE "):
        if title.startswith(pfx):
            return title[len(pfx):]
    return title


# ─── CSS ─────────────────────────────────────────────────────────────

CSS = """\
:root {
    --bg:#0d1117; --bg2:#161b22; --bg3:#21262d; --bg4:#1c2129;
    --tx:#c9d1d9; --txd:#8b949e; --txb:#f0f6fc;
    --blue:#58a6ff; --green:#3fb950; --red:#f85149;
    --yel:#d29922; --purple:#bc8cff; --border:#30363d; --r:6px;
}
/* Light mode variables */
body.light-mode {
    --bg:#ffffff; --bg2:#f6f8fa; --bg3:#eaeef2; --bg4:#f3f4f6;
    --tx:#1f2328; --txd:#57606a; --txb:#24292f;
    --blue:#0969da; --green:#1a7f37; --red:#cf222e;
    --yel:#9a6700; --purple:#8250df; --border:#d0d7de; --r:6px;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
    background:var(--bg);color:var(--tx);line-height:1.6;font-size:15px;transition:background .3s,color .3s}

/* Sidebar */
#side{position:fixed;top:0;left:0;bottom:0;width:280px;background:var(--bg2);
    border-right:1px solid var(--border);overflow-y:auto;z-index:100;
    display:flex;flex-direction:column}
#side-hd{padding:16px;border-bottom:1px solid var(--border);position:relative}
#side-hd h1{font-size:16px;color:var(--txb);margin-bottom:12px;letter-spacing:1px;display:inline-block}
#theme-toggle{position:absolute;top:16px;right:16px;width:32px;height:32px;background:var(--bg3);border:1px solid var(--border);border-radius:50%;cursor:pointer;font-size:16px;line-height:1;transition:all .2s}
#theme-toggle:hover{background:var(--bg4);transform:scale(1.1)}
#q{width:100%;padding:8px 12px;background:var(--bg);border:1px solid var(--border);
    border-radius:var(--r);color:var(--tx);font-size:14px;outline:none}
#q:focus{border-color:var(--blue)}
#q-hint{font-size:11px;color:var(--txd);margin-top:4px}
#toc{flex:1;overflow-y:auto;padding:8px 0}
.ts{padding:4px 16px}
.ts-t{font-size:11px;font-weight:700;color:var(--txd);text-transform:uppercase;
    letter-spacing:.5px;padding:8px 0 4px}
.tl{display:block;padding:4px 8px;color:var(--tx);text-decoration:none;font-size:13px;
    border-radius:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tl:hover{background:var(--bg4)} .tl.active{color:var(--blue);background:var(--bg3)}

/* Main */
#main{margin-left:280px;padding:24px 32px;max-width:1000px}
.hdr{margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border)}
.hdr h1{font-size:22px;color:var(--txb)} .hdr p{color:var(--txd);font-size:13px}
.hdr .author{color:var(--blue);font-weight:600;font-size:14px !important;margin-top:8px}

/* Quick ref tabs */
.qr{margin-bottom:32px}
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--border);margin-bottom:16px;overflow-x:auto}
.tab{padding:8px 16px;background:none;border:none;border-bottom:2px solid transparent;
    color:var(--txd);font-size:14px;cursor:pointer;white-space:nowrap}
.tab:hover{color:var(--tx)} .tab.on{color:var(--blue);border-bottom-color:var(--blue)}
.tc{display:none} .tc.on{display:block}

/* Doc sections */
.ds{margin-bottom:8px;border:1px solid var(--border);border-radius:var(--r);overflow:hidden}
details.ds[open]{border-color:var(--blue)}
/* Search highlighting */
mark{background:var(--yel);color:var(--bg);border-radius:2px;padding:0 2px}
.dh{padding:12px 16px;background:var(--bg2);cursor:pointer;display:list-item;
    align-items:center;gap:8px;user-select:none;list-style:none}
.dh::-webkit-details-marker{display:none}
.dh::marker{display:none;content:''}
.dh:hover{background:var(--bg4)}
.dh .arr{color:var(--txd);font-size:12px;transition:transform .2s;display:inline-block}
details[open]>.dh .arr{transform:rotate(90deg)}
.dt{font-size:14px;font-weight:600;color:var(--txb)}
.dp{font-size:12px;color:var(--txd);margin-left:auto;font-family:monospace}
.db{padding:16px 24px;border-top:1px solid var(--border)}
.cat{font-size:18px;font-weight:600;color:var(--txb);margin:32px 0 12px;
    padding-bottom:8px;border-bottom:1px solid var(--border)}
.cat:first-child{margin-top:0}

/* Typography */
h1{font-size:22px;margin:24px 0 12px;color:var(--txb)}
h2{font-size:18px;margin:20px 0 10px;color:var(--txb)}
h3{font-size:15px;margin:16px 0 8px;color:var(--txb)}
h4{font-size:14px;margin:12px 0 6px;color:var(--txb)}
h5,h6{font-size:13px;margin:10px 0 4px;color:var(--tx)}
p{margin:8px 0} hr{border:none;border-top:1px solid var(--border);margin:16px 0}
blockquote{border-left:3px solid var(--blue);padding:4px 16px;margin:8px 0;color:var(--txd)}
ul,ol{padding-left:24px;margin:8px 0} li{margin:3px 0}
.checklist{list-style:none;padding-left:4px} .ck{padding:2px 0}
a{color:var(--blue)}

code{font-family:'SF Mono','Fira Code','Cascadia Code',monospace;font-size:.88em;
    background:var(--bg3);padding:2px 6px;border-radius:3px}
pre{margin:12px 0;padding:16px;background:var(--bg2);border:1px solid var(--border);
    border-radius:var(--r);overflow-x:auto;font-size:13px;line-height:1.5;
    -webkit-overflow-scrolling:touch}
pre code{background:none;padding:0;font-size:inherit}

/* Tables */
.table-wrap{overflow-x:auto;margin:12px 0;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:var(--bg3);text-align:left;padding:8px 12px;border-bottom:2px solid var(--blue);
    font-weight:600;white-space:nowrap}
td{padding:6px 12px;border-bottom:1px solid var(--border);vertical-align:top}
tr:hover td{background:var(--bg4)}
tr:target td{animation:flash 1.5s ease}
@keyframes flash{0%{background:var(--blue);color:var(--txb)}100%{background:transparent;color:inherit}}

/* Ref links */
.ref{text-decoration:none;font-weight:600;border-bottom:1px dotted}
.ref.tp{color:var(--green)} .ref.gp{color:var(--purple)}

.miss{color:var(--red);font-style:italic}

/* SVG Diagrams */
.svg-diagrams{margin:16px 0}
.svg-wrap{margin:16px 0;border:1px solid var(--border);border-radius:var(--r);overflow:hidden;background:var(--bg2)}
.svg-caption{padding:8px 12px;background:var(--bg3);font-size:13px;font-weight:600;color:var(--txb);border-bottom:1px solid var(--border)}
.svg-container{overflow-x:auto;padding:16px;background:var(--svg-bg,#F5F5F0);-webkit-overflow-scrolling:touch}
.svg-container svg{max-width:none;display:block;margin:0 auto}
/* Dark mode: all SVG text adapts to theme */
.svg-container text{fill:var(--svg-tx,#1a1a1a) !important}
/* Light-on-dark labels (inside colored boxes/buses) — keep light in both modes */
.svg-container .l,.svg-container .ic-name,.svg-container .rail,
.svg-container .bus-label,.svg-container .sl,.svg-container .legend-title,
.svg-container .bl,.svg-container .conn,.svg-container .conns,
.svg-container .comp-label,.svg-container .rail-label
{fill:var(--svg-txl,#f0f6fc) !important}
/* Title/subtitle — primary heading text */
.svg-container .title,.svg-container .subtitle,.svg-container .t,
.svg-container .colhead
{fill:var(--svg-tx,#1a1a1a) !important;font-weight:700 !important}
/* Secondary/annotation text */
.svg-container .st,.svg-container .v,.svg-container .value,.svg-container .anno,
.svg-container .note,.svg-container .label,.svg-container .legend-text,
.svg-container .val,.svg-container .sub-label,.svg-container .cable-arrow,
.svg-container .pin-label,.svg-container .col-num,.svg-container .row-num,
.svg-container .sumsub
{fill:var(--svg-txd,#555) !important}
/* Component/pin/zone labels */
.svg-container .pin,.svg-container .pin-num,.svg-container .pin-func,
.svg-container .comp,.svg-container .component,.svg-container .zone-label,
.svg-container .p,.svg-container .vl,.svg-container .connector,
.svg-container .ic-label,.svg-container .ic-type,
.svg-container .func,.svg-container .net-label,.svg-container .gnd-label,
.svg-container .section-head,.svg-container .sect
{fill:var(--svg-txm,#222) !important}
/* Summary/highlight text — keep themed */
.svg-container .sum{fill:var(--svg-tx,#1a1a1a) !important;font-weight:700 !important}
/* Row/column labels in stripboard layouts */
.svg-container .row-label,.svg-container .col-label
{fill:var(--svg-txm,#333) !important;font-weight:700 !important}
/* No text-shadow — just use fill color */
.svg-container text{text-shadow:none !important}
/* Theme-specific backgrounds and colors */
body.light-mode .svg-container{--svg-bg:#F5F5F0;--svg-tx:#1a1a1a;--svg-txd:#555;--svg-txm:#222;--svg-txl:#f0f6fc;background:#F5F5F0}
body:not(.light-mode) .svg-container{--svg-bg:#2d333b;--svg-tx:#c9d1d9;--svg-txd:#8b949e;--svg-txm:#b0b8c1;--svg-txl:#f0f6fc;background:#2d333b}
@media(max-width:768px){.svg-container{padding:8px}.svg-container svg{height:auto}}
#no-res{text-align:center;padding:48px;color:var(--txd);font-size:16px;display:none}

/* Signal path highlighting - per wire, not per type */
.svg-container .wire,.svg-container .wire-thick{transition:all .2s;cursor:pointer;stroke:#1a1a1a !important}
.svg-container .wire:hover,.svg-container .wire-thick:hover{stroke:#ff6600 !important;stroke-width:3 !important;filter:drop-shadow(0 0 4px #ff6600) !important}
body:not(.light-mode) .svg-container .wire,body:not(.light-mode) .svg-container .wire-thick{stroke:#1a1a1a !important}
/* SVG arrow markers - lighter in dark mode */
body:not(.light-mode) .svg-container svg defs marker polygon{fill:#aaa !important}
body:not(.light-mode) .svg-container svg polygon[fill="#333"],body:not(.light-mode) .svg-container svg polygon[fill="#666"]{fill:#aaa !important}
/* Bus trace mode — when a bus is active, dim everything else */
.svg-container .bus-trace svg{opacity:1}
.svg-container .bus-trace .wire,.svg-container .bus-trace .wire-thick,
.svg-container .bus-trace rect,.svg-container .bus-trace .filled,
.svg-container .bus-trace .component,.svg-container .bus-trace .junction
{opacity:0.15;transition:opacity .3s}
.svg-container .bus-trace .bus-active,.svg-container .bus-trace .bus-active.wire,
.svg-container .bus-trace .bus-active.wire-thick{opacity:1 !important;stroke-width:3 !important;
    filter:drop-shadow(0 0 3px #ff6600) !important}
.svg-container .bus-trace .bus-label{opacity:1 !important;cursor:pointer}
/* Bus label hint */
.svg-container .bus-label{cursor:pointer;transition:all .2s}
.svg-container .bus-label:hover{filter:brightness(1.3)}

/* Back to top */
#top-btn{position:fixed;bottom:24px;right:24px;width:40px;height:40px;
    background:var(--bg2);border:1px solid var(--border);color:var(--tx);
    font-size:20px;border-radius:50%;cursor:pointer;opacity:0;transition:opacity .3s;z-index:50}
#top-btn.vis{opacity:1}

/* Mobile toggle */
#mb-toggle{display:none;position:fixed;top:8px;left:8px;z-index:200;background:var(--bg2);
    border:1px solid var(--border);color:var(--tx);padding:8px 12px;border-radius:var(--r);
    cursor:pointer;font-size:18px}

@media(max-width:768px){
    #side{transform:translateX(-100%);transition:transform .3s;width:280px}
    #side.open{transform:translateX(0)}
    #main{margin-left:0;padding:16px}
    #mb-toggle{display:block!important}
    table{font-size:12px} th,td{padding:4px 8px}
}

/* Scrollbar */
::-webkit-scrollbar{width:8px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:var(--txd)}

/* Print */
@media print{
    #side,#mb-toggle,#top-btn{display:none!important}
    #main{margin-left:0} details.ds{display:block} .db{display:block!important}
    body{background:#fff;color:#000;counter-reset:figure} pre{border:1px solid #ccc}
    
    /* Page break hints - prevent awkward splits */
    .ds{page-break-inside:avoid;break-inside:avoid}
    .svg-wrap{page-break-inside:avoid;break-inside:avoid;margin-bottom:16px}
    table{page-break-inside:avoid;break-inside:avoid}
    tr{page-break-inside:avoid;break-inside:avoid}
    pre{page-break-inside:avoid;break-inside:avoid}
    blockquote{page-break-inside:avoid;break-inside:avoid}
    
    /* Major sections start on new pages */
    .cat{page-break-before:always;break-before:page}
    .cat:first-child{page-break-before:auto;break-before:auto}
    
    /* Keep headers with content */
    h1,h2,h3{page-break-after:avoid;break-after:avoid}
    
    /* SVG diagrams get proper spacing and figure numbers */
    .svg-container{background:#fff}
    .svg-container svg{max-width:100%;height:auto}
    .svg-caption{counter-increment:figure}
    .svg-caption::before{content:"Figure " counter(figure) ": ";font-weight:700}
    
    /* Links show URLs */
    a[href]:after{content:" (" attr(href) ")";font-size:10px;color:#666}
    a[href^="#"]:after{content:""}
}
"""

# ─── JavaScript ──────────────────────────────────────────────────────

JS = """\
document.addEventListener('DOMContentLoaded',()=>{
    // Tabs
    document.querySelectorAll('.tab').forEach(b=>{
        b.addEventListener('click',()=>{
            document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));
            document.querySelectorAll('.tc').forEach(t=>t.classList.remove('on'));
            b.classList.add('on');
            document.getElementById('tc-'+b.dataset.t).classList.add('on');
        });
    });

    // Search
    const q=document.getElementById('q');
    const hint=document.getElementById('q-hint');
    const secs=document.querySelectorAll('details.ds');
    const cats=document.querySelectorAll('.cg');
    const qr=document.querySelector('.qr');
    const nr=document.getElementById('no-res');

    q.addEventListener('input',e=>{
        const v=q.value.trim().toLowerCase();
        if(!v){
            hint.textContent='TP##, GP##, component, signal...';
            secs.forEach(s=>{s.style.display='';s.open=false;
                const db=s.querySelector('.db');
                if(db){let h=db.innerHTML;h=h.split('<mark>').join('').split('</mark>').join('');db.innerHTML=h;}
            });
            cats.forEach(c=>c.style.display='');
            qr.style.display=''; nr.style.display='none'; return;
        }
        qr.style.display='none';
        let n=0;
        secs.forEach(s=>{
            const db=s.querySelector('.db');
            if(!db)return;
            // Clear previous marks
            let dh = db.innerHTML;
            dh = dh.split('<mark>').join('').split('</mark>').join('');
            db.innerHTML = dh;
            if(s.textContent.toLowerCase().includes(v)){
                s.style.display=''; n++; s.open=true;
                // Highlight matches
                const txt=db.innerText.toLowerCase();
                if(txt.includes(v)){
                    const regex=new RegExp('('+v+')','gi');
                    db.innerHTML=db.innerHTML.replace(regex,'<mark>$1</mark>');
                }
            }else{
                s.style.display='none';
            }
        });
        cats.forEach(c=>{
            const vis=c.querySelectorAll('.ds:not([style*="display: none"])');
            c.style.display=vis.length?'':'none';
        });
        hint.textContent=n?n+' document'+(n===1?'':'s')+' found':'No matches';
        nr.style.display=n?'none':'block';
    });

    // Keyboard: / to search, Esc to clear (already exists at line 689)
    document.addEventListener('keydown',e=>{
        if(e.key==='\\/'&&document.activeElement!==q){e.preventDefault();q.focus()}
        if(e.key==='Escape'){q.value='';q.dispatchEvent(new Event('input'));q.blur()}
    });

    // Mobile menu
    const mb=document.getElementById('mb-toggle');
    const side=document.getElementById('side');
    if(mb)mb.addEventListener('click',e=>{e.stopPropagation();side.classList.toggle('open')});
    document.addEventListener('click',e=>{
        if(side.classList.contains('open')&&!side.contains(e.target)&&e.target!==mb){side.classList.remove('open')}
    });

    // TOC smooth scroll
    document.querySelectorAll('.tl').forEach(a=>{
        a.addEventListener('click',e=>{
            e.preventDefault();
            const t=document.querySelector(a.getAttribute('href'));
            if(t){
                const ds=t.closest('details.ds');
                if(ds)ds.open=true;
                t.scrollIntoView({behavior:'smooth',block:'start'});
            }
            document.getElementById('side').classList.remove('open');
        });
    });

    // Scroll observer: highlight active TOC link
    const obs=new IntersectionObserver(entries=>{
        entries.forEach(en=>{
            if(en.isIntersecting){
                document.querySelectorAll('.tl').forEach(l=>l.classList.remove('active'));
                const lnk=document.querySelector('.tl[href=\"#'+en.target.id+'\"]');
                if(lnk)lnk.classList.add('active');
            }
        });
    },{threshold:0.1});
    secs.forEach(s=>obs.observe(s));

    // Back to top
    window.addEventListener('scroll',()=>{
        document.getElementById('top-btn').classList.toggle('vis',window.scrollY>300);
    });

    // Theme toggle (light/dark mode)
    const themeBtn=document.getElementById('theme-toggle');
    const savedTheme=localStorage.getItem('macrobrute-theme');
    if(savedTheme==='light')document.body.classList.add('light-mode');
    
    if(themeBtn){
        themeBtn.addEventListener('click',()=>{
            document.body.classList.toggle('light-mode');
            const isLight=document.body.classList.contains('light-mode');
            localStorage.setItem('macrobrute-theme',isLight?'light':'dark');
            themeBtn.innerHTML=isLight?'🌙':'☀️';
        });
    }

    // Bus signal tracing — click a bus-label or wire to highlight its group
    let activeBus=null;
    document.querySelectorAll('.svg-container').forEach(container=>{
        container.addEventListener('click',e=>{
            const el=e.target;
            const bus=el.dataset&&el.dataset.bus?el.dataset.bus:
                       el.closest('[data-bus]')?el.closest('[data-bus]').dataset.bus:null;
            if(bus){
                if(activeBus===bus){container.classList.remove('bus-trace');
                    container.querySelectorAll('.bus-active').forEach(b=>b.classList.remove('bus-active'));
                    activeBus=null;return;}
                container.classList.add('bus-trace');
                container.querySelectorAll('.bus-active').forEach(b=>b.classList.remove('bus-active'));
                container.querySelectorAll('[data-bus="'+bus+'"]').forEach(b=>b.classList.add('bus-active'));
                activeBus=bus;
            }else if(!el.closest('.wire')&&!el.closest('.wire-thick')){
                container.classList.remove('bus-trace');
                container.querySelectorAll('.bus-active').forEach(b=>b.classList.remove('bus-active'));
                activeBus=null;
            }
        });
    });
});
"""


# ─── HTML Builders ───────────────────────────────────────────────────

def _sidebar():
    toc = []
    toc.append('<div class="ts"><a class="tl" href="#quick-ref" '
               'style="color:var(--yel)">Quick Reference</a></div>')
    for cat_title, cat_id, files in SECTIONS:
        toc.append(f'<div class="ts"><div class="ts-t">{cat_title}</div>')
        for fp in files:
            did = _make_id(fp)
            title, _ = _read(fp)
            toc.append(f'<a class="tl" href="#{did}">{_html.escape(_short(title))}</a>')
        toc.append("</div>")

    return f"""<nav id="side">
<div id="side-hd">
<h1>MACROBRUTE</h1>
<button id="theme-toggle" title="Toggle light/dark mode">☀️</button>
<input type="text" id="q" placeholder="Search... (press /)" aria-label="Search manual">
<div id="q-hint">TP##, GP##, component, signal...</div>
</div>
<div id="toc">{''.join(toc)}</div>
</nav>"""


def _quick_ref():
    tabs = []
    panes = []
    for i, (label, tid, fp) in enumerate(QUICK_REF):
        on = " on" if i == 0 else ""
        tabs.append(f'<button class="tab{on}" data-t="{tid}">{label}</button>')
        _, body = _read(fp)
        html = _autolink(_md(body, f"qr-{tid}"))
        panes.append(f'<div class="tc{on}" id="tc-{tid}">{html}</div>')

    return f"""<div class="qr" id="quick-ref">
<div class="cat">Quick Reference</div>
<div class="tabs">{''.join(tabs)}</div>
{''.join(panes)}
</div>"""


def _svg_preprocess(svg_content):
    """Strip background <rect> and filter artifacts from SVG for theme adaptation."""
    svg_content = re.sub(
        r'<rect[^>]*fill="#[FfEe0-9]{6}"[^>]*\s*/?>',
        '', svg_content, count=1
    )
    svg_content = re.sub(
        r'<rect[^>]*fill="#2F4F4F"[^>]*\s*/?>',
        '', svg_content, count=1
    )
    svg_content = re.sub(
        r'<rect[^>]*fill="#1[01][0-9a-fA-F]*"[^>]*\s*/?>',
        '', svg_content, count=1
    )
    svg_content = re.sub(r'filter:\s*url\(#ts\)', '', svg_content)
    svg_content = re.sub(r'filter:\s*url\(#textshadow\)', '', svg_content)
    svg_content = re.sub(r'filter="url\(#ts\)"', '', svg_content)
    svg_content = re.sub(r'filter="url\(#textshadow\)"', '', svg_content)
    svg_content = re.sub(
        r'<filter[^>]*id="ts"[^>]*>.*?</filter>',
        '', svg_content, flags=re.DOTALL
    )
    svg_content = re.sub(
        r'<filter[^>]*id="textshadow"[^>]*>.*?</filter>',
        '', svg_content, flags=re.DOTALL
    )
    svg_content = re.sub(
        r'<filter[^>]*>.*?feFlood[^>]*flood-color="white"[^>]*>.*?</filter>',
        '', svg_content, flags=re.DOTALL
    )
    return svg_content


def _embed_svgs(fpath):
    """Generate HTML for embedded SVGs associated with a markdown file."""
    svg_paths = SVG_MAP.get(fpath, [])
    if not svg_paths:
        return ""

    embeds = ['<div class="svg-diagrams">']
    for svg_path in svg_paths:
        full_path = PROJECT / svg_path
        if full_path.exists():
            try:
                svg_content = _svg_preprocess(full_path.read_text(encoding="utf-8"))
                # Extract title for caption (handle HTML entities like &amp;)
                title_match = re.search(r'<text[^>]*class="title"[^>]*>(.+?)</text>', svg_content)
                if title_match:
                    caption = title_match.group(1)
                    # Decode common HTML entities
                    caption = caption.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                else:
                    caption = Path(svg_path).stem.replace("_", " ").title()

                embeds.append(f'<div class="svg-wrap">')
                embeds.append(f'<div class="svg-caption">{_html.escape(caption)}</div>')
                embeds.append(f'<div class="svg-container">{svg_content}</div>')
                embeds.append('</div>')
            except Exception as e:
                embeds.append(f'<!-- Error loading {svg_path}: {e} -->')
    embeds.append('</div>')
    return "\n".join(embeds)


def _doc_section(fpath):
    did = _make_id(fpath)
    title, body = _read(fpath)
    html = _autolink(_md(body, did))
    svgs = _embed_svgs(fpath)
    return f"""<details class="ds" id="{did}">
<summary class="dh"><span class="arr">&#9654;</span>
<span class="dt">{_html.escape(_short(title))}</span>
<span class="dp">{_html.escape(fpath)}</span></summary>
<div class="db">{svgs}{html}</div></details>"""


def _count_docs():
    seen = set()
    for _, _, files in SECTIONS:
        seen.update(files)
    return len(seen)


def build():
    """Build the complete manual."""
    ndocs = _count_docs()
    today = date.today().isoformat()

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<meta name="theme-color" content="#0d1117">',
        "<title>MACROBRUTE Manual</title>",
        f"<style>\n{CSS}</style>",
        "</head><body>",
        '<button id="mb-toggle">&#9776;</button>',
        _sidebar(),
        '<main id="main">',
        f'<div class="hdr"><h1>MACROBRUTE Manual</h1>'
        f'<p>MicroBrute &rarr; Semi-Modular Synthesizer Expansion</p>'
        f'<p>Generated {today} &middot; {ndocs} documents</p>'
        f'<p class="author">Authored by: jordanaftermidnight</p></div>',
        _quick_ref(),
        '<div id="no-res">No matching documents</div>',
    ]

    for cat_title, cat_id, files in SECTIONS:
        parts.append(f'<div class="cg" id="cat-{cat_id}">')
        parts.append(f'<div class="cat">{_html.escape(cat_title)}</div>')
        for fp in files:
            parts.append(_doc_section(fp))
        parts.append("</div>")

    parts.extend([
        "</main>",
        '<button id="top-btn" onclick="window.scrollTo({top:0,behavior:\'smooth\'})">'
        "&#8679;</button>",
        f"<script>\n{JS}</script>",
        "</body></html>",
    ])

    html = "\n".join(parts)
    OUTPUT.write_text(html, encoding="utf-8")
    size = OUTPUT.stat().st_size
    print(f"Built: {OUTPUT.name} ({size // 1024}KB, {ndocs} docs)")


if __name__ == "__main__":
    build()
