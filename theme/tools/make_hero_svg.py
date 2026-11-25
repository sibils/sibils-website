"""Regenerate theme/img/hero-annotations.svg, the decoration of the home page
hero (css/sibils.css, .hero__inner::before): lines of "text" (faint bars)
whose right ends are the coloured bars of the SIBiLS wordmark's "i" (its
stack of annotation bars), in the wordmark's hues made lighter for the dark
band.

Usage, from the repository root:

    ./venv/bin/python theme/tools/make_hero_svg.py theme/img/hero-annotations.svg

The script does not read the wordmark: the widths and hues of its bars (STACK
below) were read from theme/img/sibils-wordmark.png by hand, in wordmark
pixels, and are typed in. If the wordmark changes, measure them again. The
grey bars are drawn at random from a fixed seed, so the output is the same on
every run.
"""
import random
import sys

W, H = 560, 448
BAR_H = 16          # wordmark (read by hand): 21 px bars every 42 px -> 16 every 32
STEP = 32
SCALE = 16 / 21     # widths scaled like the heights
RIGHT = W - 8
GAP = 8             # space between words
TOP = 8

# Wordmark rows (top to bottom), widths in wordmark pixels, right-aligned at
# its axis (theme/img/sibils-wordmark.png, x 721-868), read by hand from the
# image; None is the empty row.
STACK = [
    [("#0000ff", 73)],
    [("#00ff00", 33), ("#ff0000", 48)],
    None,
    [("#ff00ff", 52)],
    [("#ff0000", 65), ("#ffff54", 60)],
    [("#00ffff", 57), ("#ff0000", 91)],
    [("#00ff00", 52)],
    [("#0000ff", 94)],
]
FIRST_STACK_ROW = 3
ROWS = 14

# The wordmark colours, a little lighter so that they read on the dark band.
SHOWN = {
    "#0000ff": "#5c76ff",
    "#00ff00": "#2ee66b",
    "#ff0000": "#ff4545",
    "#ff00ff": "#ff57ff",
    "#ffff54": "#ffe94d",
    "#00ffff": "#33e0ff",
}

rnd = random.Random(20261125)
out = []
for row in range(ROWS):
    y = TOP + row * STEP
    x = RIGHT
    i = row - FIRST_STACK_ROW
    coloured = STACK[i] if 0 <= i < len(STACK) and STACK[i] else []
    for colour, width in reversed(coloured):
        w = round(width * SCALE)
        x -= w
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{BAR_H}" fill="{SHOWN[colour]}"/>')
    if coloured:
        x -= GAP
    elif row % 3 != 0:
        x -= rnd.choice([0, 24, 40, 64])
    while x > 0:
        w = rnd.choice([28, 36, 44, 52, 60, 72, 88, 104])
        x0 = max(0, x - w)
        attrs = 'class="g"'
        if not coloured and rnd.random() < 0.09 and x0 > 140:
            attrs = f'fill="{SHOWN[rnd.choice(list(SHOWN))]}" fill-opacity="0.7"'
        out.append(f'<rect {attrs} x="{x0}" y="{y}" width="{x - x0}" height="{BAR_H}"/>')
        x = x0 - GAP

body = "\n".join(out)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<!-- Decorative (home page hero): lines of text whose right ends are the
     annotation bars of the SIBiLS wordmark (img/sibils-wordmark.png), at its
     proportions, in its hues made lighter for a dark ground. Fades out to
     the left. -->
<defs>
<linearGradient id="f" x1="0" x2="1" y1="0" y2="0">
<stop offset="0" stop-color="#fff" stop-opacity="0"/>
<stop offset="0.6" stop-color="#fff" stop-opacity="1"/>
</linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#f)"/></mask>
<style>.g{{fill:#fff;fill-opacity:.12}}</style>
</defs>
<g mask="url(#m)">
{body}
</g>
</svg>
'''
with open(sys.argv[1], "w") as fh:
    fh.write(svg)
print(len(svg), "bytes")
