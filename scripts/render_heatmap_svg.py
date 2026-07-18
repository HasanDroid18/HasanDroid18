"""Render data/contributions.json as the classic 53-week calendar of rounded
boxes with a diagonal reveal animation -> contrib-heatmap.svg.

    python scripts/render_heatmap_svg.py
"""

import datetime as dt
import json
import pathlib

from asciiart import BG, BORDER, FONT

ROOT = pathlib.Path(__file__).resolve().parent.parent

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end for the best day)

DIM = "#8b949e"
FG = "#c9d1d9"
GREEN = "#3ddc84"

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 20
LEFT = PAD + 30   # room for weekday labels
TOP = PAD + 18    # room for month labels
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days = data["days"]
    stats = data["stats"]
    best_count = stats["best_day"]["count"]

    # arrange into week columns, Sunday-first like GitHub
    weeks = []
    col = [None] * 7
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        dow = (date.weekday() + 1) % 7  # Sunday = 0
        if dow == 0 and any(v is not None for v in col):
            weeks.append(col)
            col = [None] * 7
        col[dow] = d
    if any(v is not None for v in col):
        weeks.append(col)
    weeks = weeks[-53:]

    n = len(weeks)
    width = LEFT + n * STEP - GAP + PAD
    height = TOP + 7 * STEP - GAP + 46

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">',
        "<style>"
        ".d{opacity:0;animation:pop .5s ease-out forwards}"
        "@keyframes pop{from{opacity:0;transform:translate(0,-14px)}"
        "to{opacity:1;transform:translate(0,0)}}"
        ".t{opacity:0;animation:fade .8s ease-out forwards}"
        "@keyframes fade{to{opacity:1}}"
        "</style>",
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'rx="8" fill="{BG}" stroke="{BORDER}"/>',
    ]

    # month labels: mark columns where a new month starts
    seen = None
    for w, col in enumerate(weeks):
        first = next((d for d in col if d), None)
        if not first:
            continue
        month = dt.date.fromisoformat(first["date"]).month
        if month != seen:
            if seen is not None or w == 0:
                parts.append(
                    f'<text class="t" style="animation-delay:{0.2 + w * 0.02:.2f}s" '
                    f'x="{LEFT + w * STEP}" y="{TOP - 8}" font-family="{FONT}" '
                    f'font-size="11" fill="{DIM}">{MONTHS[month - 1]}</text>'
                )
            seen = month

    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        parts.append(
            f'<text class="t" style="animation-delay:.3s" x="{PAD}" '
            f'y="{TOP + row * STEP + CELL - 2}" font-family="{FONT}" '
            f'font-size="10" fill="{DIM}">{label}</text>'
        )

    # cells with diagonal reveal: delay grows with week + day
    for w, col in enumerate(weeks):
        for r, d in enumerate(col):
            if d is None:
                continue
            level = min(int(d["level"]), 4)
            if best_count > 0 and d["count"] == best_count and level == 4:
                level = 5  # neon top end for the best day
            delay = 0.15 + (w + r) * 0.018
            parts.append(
                f'<rect class="d" style="animation-delay:{delay:.3f}s" '
                f'x="{LEFT + w * STEP}" y="{TOP + r * STEP}" width="{CELL}" '
                f'height="{CELL}" rx="3" fill="{PALETTE[level]}">'
                f'<title>{d["count"]} contributions on {d["date"]}</title></rect>'
            )

    # footer: stats left, Less -> More legend right
    fy = TOP + 7 * STEP - GAP + 30
    total = stats["total"]
    footer = (
        f'{total:,} contributions in the last year'
        f'   ·   current streak {stats["current_streak"]}d'
        f'   ·   longest {stats["longest_streak"]}d'
    )
    parts.append(
        f'<text class="t" style="animation-delay:1.6s" x="{LEFT}" y="{fy}" '
        f'font-family="{FONT}" font-size="12" fill="{FG}">{footer}</text>'
    )
    legend_x = width - PAD - 6 * (CELL + 2) - 78
    parts.append(
        f'<text class="t" style="animation-delay:1.6s" x="{legend_x - 34}" y="{fy}" '
        f'font-family="{FONT}" font-size="11" fill="{DIM}">Less</text>'
    )
    for i, c in enumerate(PALETTE):
        parts.append(
            f'<rect class="t" style="animation-delay:{1.6 + i * 0.06:.2f}s" '
            f'x="{legend_x + i * (CELL + 2)}" y="{fy - CELL + 2}" width="{CELL}" '
            f'height="{CELL}" rx="3" fill="{c}"/>'
        )
    parts.append(
        f'<text class="t" style="animation-delay:1.9s" '
        f'x="{legend_x + 6 * (CELL + 2) + 6}" y="{fy}" font-family="{FONT}" '
        f'font-size="11" fill="{DIM}">More</text>'
    )

    parts.append("</svg>")
    out = ROOT / "contrib-heatmap.svg"
    out.write_text("\n".join(parts))
    print(f"wrote {out} ({n} weeks, {total} contributions, {width}x{height})")


if __name__ == "__main__":
    main()
