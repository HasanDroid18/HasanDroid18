"""Neofetch-style info card -> info-card.svg.

Lines fade+slide in on a stagger (CSS keyframes inside the SVG, play once,
freeze). STATIC=1 emits a frozen frame for local previews.

Run locally when details change:  python scripts/make_info_card.py
"""

import os
import pathlib
from xml.sax.saxutils import escape

from asciiart import BG, BORDER, FONT, GREEN

ROOT = pathlib.Path(__file__).resolve().parent.parent

FG = "#c9d1d9"
DIM = "#8b949e"
CYAN = "#56d4dd"
YELLOW = "#e3b341"

FONT_SIZE = 13
LINE_H = 21
PAD_X = 24
WIDTH = 480

# (key, value) — key printed in green like neofetch; None key = plain line
LINES = [
    ("hasan@hasandroid", None),
    ("----------------", None),
    ("Name", "Hasan Taha"),
    ("Role", "Android Dev · IT Support · React Native"),
    ("Location", "Beirut, Lebanon"),
    ("Education", "B.Sc. Computer Science — Al Maaref (2025)"),
    ("", ""),
    ("Now", "Android · Kotlin · MVVM · Clean Arch"),
    ("Learning", "iOS — Swift / SwiftUI"),
    ("Stack", "Kotlin · Java · React Native · Node/ASP.NET"),
    ("Data", "Firebase · Room/SQLite · MongoDB · MySQL"),
    ("", ""),
    ("Highlights", "Le5aa Scorer — first app on Play Store"),
    ("", "Expense Tracker · Health Care App · Sawa"),
    ("Exp", "SYC IT Support · TedMob Android intern"),
    ("", ""),
    ("Web", "hasantaha.online"),
    ("Email", "hassan181taha@gmail.com"),
    ("", ""),
    ("colors", None),
]


def main():
    static = os.environ.get("STATIC") == "1"
    top = 30 + 16
    height = top + len(LINES) * LINE_H + 18
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img">'
    ]
    anim = "" if static else (
        "<style>"
        ".ln{opacity:0;transform:translateX(-8px);"
        "animation:in .45s ease-out forwards}"
        "@keyframes in{to{opacity:1;transform:translateX(0)}}"
        "</style>"
    )
    if static:
        parts.append("<style>.ln{opacity:1}</style>")
    else:
        parts.append(anim)
    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" '
        f'rx="8" fill="{BG}" stroke="{BORDER}"/>'
    )
    # terminal title bar
    parts.append('<circle cx="20" cy="19" r="5" fill="#ff5f56"/>')
    parts.append('<circle cx="38" cy="19" r="5" fill="#ffbd2e"/>')
    parts.append('<circle cx="56" cy="19" r="5" fill="#27c93f"/>')
    parts.append(
        f'<text x="{WIDTH / 2:.0f}" y="23" text-anchor="middle" font-family="{FONT}" '
        f'font-size="12" fill="{DIM}">hasan@hasandroid: ~/neofetch</text>'
    )
    parts.append(f'<line x1="1" y1="34" x2="{WIDTH - 1}" y2="34" stroke="{BORDER}"/>')

    for i, (key, val) in enumerate(LINES):
        y = top + i * LINE_H + FONT_SIZE
        delay = 0.25 + i * 0.13
        style = "" if static else f' style="animation-delay:{delay:.2f}s"'
        if key == "colors":
            # neofetch-style palette swatches
            sw = "".join(
                f'<rect x="{PAD_X + j * 26}" y="{y - FONT_SIZE + 1}" width="22" '
                f'height="14" rx="3" fill="{c}"/>'
                for j, c in enumerate(
                    ["#ff5f56", "#ffbd2e", "#27c93f", GREEN, CYAN, "#a371f7", FG, DIM]
                )
            )
            parts.append(f'<g class="ln"{style}>{sw}</g>')
            continue
        if val is None:
            color = GREEN if "@" in key else DIM
            parts.append(
                f'<text class="ln"{style} x="{PAD_X}" y="{y}" font-family="{FONT}" '
                f'font-size="{FONT_SIZE}" font-weight="bold" fill="{color}">'
                f"{escape(key)}</text>"
            )
            continue
        if not key and not val:
            continue
        tspans = ""
        if key:
            tspans += (
                f'<tspan fill="{GREEN}" font-weight="bold">{escape(key)}:</tspan>'
            )
        pad = "" if not key else " "
        val_fill = CYAN if key in ("Web", "Email") else FG
        hl = YELLOW if key == "Highlights" else val_fill
        tspans += f'<tspan fill="{hl}" x="{PAD_X + 96}">{escape(val)}</tspan>'
        parts.append(
            f'<text class="ln"{style} x="{PAD_X}" y="{y}" font-family="{FONT}" '
            f'font-size="{FONT_SIZE}">{tspans}{pad}</text>'
        )

    parts.append("</svg>")
    out = ROOT / "info-card.svg"
    out.write_text("\n".join(parts))
    print(f"wrote {out} ({len(LINES)} lines, {WIDTH}x{height})")


if __name__ == "__main__":
    main()
