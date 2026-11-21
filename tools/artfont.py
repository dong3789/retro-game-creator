#!/usr/bin/env python3
"""
artfont.py — pixel text for GBC art, using a hand-made 5x7 bitmap font.

Why: the GBC font that GBDK prints with is fixed and colour-index bound. When you
want a title logo, a menu label or a big "GAME OVER", you draw the letters into
the art itself. This module draws crisp 5x7 glyphs at any integer scale so the
text survives the 4-colour, 8x8-tile budget.

Library use:
    from artfont import draw_text
    draw_text(img, 8, 16, "TILE HOP", (255,233,168), scale=3, shadow=(43,74,140))

CLI:
    python3 tools/artfont.py "TILE HOP" --scale 3 \\
        --color "#FFE9A8" --bg "#10182E" --shadow "#2B4A8C" --out title_text.png
"""

from __future__ import annotations

import argparse
import sys

GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    "<": ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "*": [".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
}

GLYPH_W, GLYPH_H = 5, 7
TRACKING = 1  # blank columns between glyphs, in font pixels


def text_size(text: str, scale: int = 1):
    if not text:
        return 0, 0
    w = len(text) * (GLYPH_W + TRACKING) - TRACKING
    return w * scale, GLYPH_H * scale


def draw_text(img, x, y, text, color, scale=1, shadow=None, shadow_offset=(1, 1)):
    """Draw `text` with its top-left at (x, y). Unknown characters draw as space."""
    px = img.load()
    w, h = img.size

    if shadow is not None:
        sx, sy = shadow_offset
        col = 0
        for ch in text.upper():
            glyph = GLYPHS.get(ch, GLYPHS[" "])
            for row, line in enumerate(glyph):
                for c, bit in enumerate(line):
                    if bit == "#":
                        gx = x + (col + c + sx) * scale
                        gy = y + (row + sy) * scale
                        for yy in range(scale):
                            for xx in range(scale):
                                if 0 <= gx + xx < w and 0 <= gy + yy < h:
                                    px[gx + xx, gy + yy] = shadow
            col += GLYPH_W + TRACKING

    col = 0
    for ch in text.upper():
        glyph = GLYPHS.get(ch, GLYPHS[" "])
        for row, line in enumerate(glyph):
            for c, bit in enumerate(line):
                if bit == "#":
                    gx = x + (col + c) * scale
                    gy = y + (row) * scale
                    for yy in range(scale):
                        for xx in range(scale):
                            if 0 <= gx + xx < w and 0 <= gy + yy < h:
                                px[gx + xx, gy + yy] = color
        col += GLYPH_W + TRACKING
    return img


def draw_text_centered(img, y, text, color, scale=1, shadow=None):
    tw, _ = text_size(text, scale)
    return draw_text(img, (img.size[0] - tw) // 2, y, text, color, scale, shadow)


def _rgb(text):
    t = text.strip().lstrip("#")
    if len(t) == 3:
        t = "".join(c * 2 for c in t)
    return tuple(int(t[i : i + 2], 16) for i in (0, 2, 4))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render 5x7 pixel text to a PNG (for GBC art).")
    ap.add_argument("text")
    ap.add_argument("--out", default="text.png")
    ap.add_argument("--scale", type=int, default=1)
    ap.add_argument("--color", default="#FFFFFF")
    ap.add_argument("--bg", default="#00000000", help="background colour, #RRGGBB or #RRGGBBAA (default transparent)")
    ap.add_argument("--shadow", help="shadow colour, e.g. #2B4A8C")
    ap.add_argument("--pad", type=int, default=1, help="padding around the text in pixels (default 1)")
    args = ap.parse_args(argv)

    from PIL import Image  # local import so the module stays importable without pillow for tests

    tw, th = text_size(args.text, args.scale)
    size = (tw + args.pad * 2, th + args.pad * 2)
    img = Image.new("RGBA", size, _rgba(args.bg))
    shadow = _rgb(args.shadow) if args.shadow else None
    draw_text(img, args.pad, args.pad, args.text, _rgb(args.color), args.scale, shadow)
    img.save(args.out)
    print(f"{size[0]}x{size[1]} -> {args.out}")
    return 0


def _rgba(text):
    t = text.strip().lstrip("#")
    if len(t) == 3:
        t = "".join(c * 2 for c in t)
    if len(t) == 6:
        t += "FF"
    return tuple(int(t[i : i + 2], 16) for i in (0, 2, 4, 6))


if __name__ == "__main__":
    raise SystemExit(main())
