"""Convert assets/logo.png (the HASANDROID wordmark avatar) into a wide
self-typing ASCII banner: hasandroid-banner.svg.

Run locally whenever the avatar changes:  python scripts/make_banner_svg.py
"""

import pathlib

import numpy as np
from PIL import Image

from asciiart import RAMP, typing_svg

ROOT = pathlib.Path(__file__).resolve().parent.parent
COLS = 168
FONT_SIZE = 11
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE + 1


def main():
    img = Image.open(ROOT / "assets" / "logo.png").convert("L")
    g = np.asarray(img, dtype=np.float32)

    # the wordmark is a bright strip on black: crop to its bounding box
    ys, xs = np.where(g > 40)
    pad = 6
    g = g[max(ys.min() - pad, 0):ys.max() + pad, max(xs.min() - pad, 0):xs.max() + pad]

    h, w = g.shape
    rows_n = max(1, round(COLS * (h / w) * (CHAR_W / LINE_H)))
    small = np.asarray(
        Image.fromarray(g.astype(np.uint8)).resize((COLS, rows_n), Image.LANCZOS),
        dtype=np.float32,
    ) / 255.0

    # light-on-dark logo: bright wordmark pixels print dense glyphs, the
    # black background falls to blank. The mark is flat-colored, so a hard
    # quantization keeps the letterforms crisp instead of mushy.
    small = small / max(small.max(), 1e-6)  # stretch to full range

    def glyph(v):
        if v < 0.20:
            return " "
        if v < 0.45:
            return "."
        if v < 0.72:
            return "+"
        return RAMP[-1]

    lines = []
    for r in small:
        lines.append("".join(glyph(v) for v in r).rstrip())
    # drop blank top/bottom rows
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    svg = typing_svg(
        lines, font_size=FONT_SIZE, char_w=CHAR_W, line_h=LINE_H,
        pad_x=24, pad_y=18, row_dur=0.30, stagger=0.20,
    )
    out = ROOT / "hasandroid-banner.svg"
    out.write_text(svg)
    print(f"wrote {out} ({len(lines)} rows x {COLS} cols)")


if __name__ == "__main__":
    main()
