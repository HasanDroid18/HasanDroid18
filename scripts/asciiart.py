"""Shared helpers for the self-typing ASCII SVG generators."""

from xml.sax.saxutils import escape

FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
GREEN = "#3ddc84"
BG = "#0d1117"
BORDER = "#30363d"

# bright (sparse) -> dark (dense); leading space blanks the background
RAMP = " .`:-=+*cs#%@"


def typing_svg(rows, *, font_size, char_w, line_h, fill=GREEN,
               pad_x=22, pad_y=20, row_dur=0.28, stagger=0.16, t0=0.3,
               title_bar=None):
    """Build an SVG where each text row wipes in left-to-right with a
    block cursor riding the edge (SMIL, plays once, freezes)."""
    n_cols = max(len(r) for r in rows) if rows else 0
    text_w = n_cols * char_w
    top = pad_y + (30 if title_bar else 0)
    width = round(text_w + 2 * pad_x)
    height = round(top + len(rows) * line_h + pad_y)

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'rx="8" fill="{BG}" stroke="{BORDER}"/>'
    )
    if title_bar:
        parts.append('<circle cx="20" cy="19" r="5" fill="#ff5f56"/>')
        parts.append('<circle cx="38" cy="19" r="5" fill="#ffbd2e"/>')
        parts.append('<circle cx="56" cy="19" r="5" fill="#27c93f"/>')
        parts.append(
            f'<text x="{width / 2:.0f}" y="23" text-anchor="middle" '
            f'font-family="{FONT}" font-size="12" fill="#8b949e">{escape(title_bar)}</text>'
        )
        parts.append(f'<line x1="1" y1="34" x2="{width - 1}" y2="34" stroke="{BORDER}"/>')
        # keep glyph rows clear of the bar
        top = pad_y + 30

    for i, row in enumerate(rows):
        begin = t0 + i * stagger
        end = begin + row_dur
        y = top + i * line_h + font_size  # baseline
        row_w = len(row) * char_w
        clip_id = f"c{i}"
        parts.append(
            f'<clipPath id="{clip_id}"><rect x="{pad_x}" y="{y - font_size - 2:.2f}" '
            f'width="0" height="{line_h + 4}">'
            f'<animate attributeName="width" from="0" to="{row_w:.1f}" '
            f'begin="{begin:.2f}s" dur="{row_dur}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(
            f'<text x="{pad_x}" y="{y:.2f}" xml:space="preserve" font-family="{FONT}" '
            f'font-size="{font_size}" fill="{fill}" clip-path="url(#{clip_id})" '
            f'textLength="{row_w:.1f}" lengthAdjust="spacingAndGlyphs">{escape(row)}</text>'
        )
        if row.strip():
            # block cursor riding the wipe edge of this row
            parts.append(
                f'<rect x="{pad_x}" y="{y - font_size + 1:.2f}" width="{char_w:.2f}" '
                f'height="{font_size + 2}" fill="{fill}" opacity="0">'
                f'<set attributeName="opacity" to="0.9" begin="{begin:.2f}s"/>'
                f'<animate attributeName="x" from="{pad_x}" to="{pad_x + row_w:.1f}" '
                f'begin="{begin:.2f}s" dur="{row_dur}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0" begin="{end:.2f}s"/></rect>'
            )

    # final resting cursor blinking under the art
    total = t0 + (len(rows) - 1) * stagger + row_dur
    parts.append(
        f'<rect x="{pad_x}" y="{top + len(rows) * line_h - font_size + 1:.2f}" '
        f'width="{char_w * 1.4:.1f}" height="{font_size + 2}" fill="{fill}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.9;0.9;0;0" keyTimes="0;0.01;0.5;0.51;1" '
        f'begin="{total:.2f}s" dur="1.2s" repeatCount="indefinite"/></rect>'
    )
    parts.append("</svg>")
    return "\n".join(parts)
