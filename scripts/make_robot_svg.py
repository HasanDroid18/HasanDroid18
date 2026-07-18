"""Hand-authored Android robot ASCII art -> robot-ascii.svg (self-typing).

Run locally when the art changes:  python scripts/make_robot_svg.py
"""

import pathlib

from asciiart import typing_svg

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_SIZE = 13
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE + 2

ROBOT = r"""
         \      /
          \    /
       .##########.
     .##############.
     ################
     ###(o)####(o)###
     ################

.--. ################ .--.
|##| ################ |##|
|##| ################ |##|
|##| ################ |##|
|##| ################ |##|
'--' ################ '--'
     ################
     ################
      ##############
       ####    ####
       ####    ####
       ####    ####
       '##'    '##'
"""

FOOTER = [
    "",
    "   $ whoami",
    "   > hasandroid",
]


def main():
    lines = [ln.rstrip() for ln in ROBOT.strip("\n").split("\n")]
    width = max(len(ln) for ln in lines)
    # center the footer block under the robot
    lines += [ln.rstrip() for ln in FOOTER]

    svg = typing_svg(
        lines, font_size=FONT_SIZE, char_w=CHAR_W, line_h=LINE_H,
        pad_x=26, pad_y=22, row_dur=0.22, stagger=0.14,
        title_bar="hasandroid.txt",
    )
    out = ROOT / "robot-ascii.svg"
    out.write_text(svg)
    print(f"wrote {out} ({len(lines)} rows, {width} cols)")


if __name__ == "__main__":
    main()
