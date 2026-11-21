#!/usr/bin/env python3
"""
make_art.py — draw every PNG the starter game needs, then convert it to C.

This is the "asset stage" of the AI workflow in SKILL.md:

    python3 assets/make_art.py             # draw PNGs into assets/ and run png2gbc.py
    python3 assets/make_art.py --png-only   # just the PNGs, look at them, re-run later

Why a script and not hand-painted files? Two reasons:
  * the level layout lives in ONE place (LEVEL_BLOCKS / STAR_SPOTS below) and is
    emitted twice: once into level.png, once into src/gen/layout.h, which the C
    code reads for collision and scoring. Art and collision cannot drift apart.
  * the art is drawn from a small, reusable tileset the way real Game Boy games
    are: 3 grass tiles and a brick tile repeat across the 320-cell playfield, so
    the level costs ~6 tiles of VRAM instead of 320. Randomly scattered 1-pixel
    stars would make every 8x8 cell unique and blow the 384-tile budget — that is
    exactly the mistake SKILL.md warns about.

Outputs
    assets/*.png          the source art (commit these)
    src/gen/*.c, *.h      tile data + palettes for the compiler (commit these)
    src/gen/layout.h      block rects, star spawns, screen regions used by main.c
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEN = os.path.join(ROOT, "src", "gen")
TOOLS = os.path.abspath(os.path.join(ROOT, "..", "..", "tools"))
PNG2GBC = os.path.join(TOOLS, "png2gbc.py")

sys.path.insert(0, TOOLS)
from artfont import draw_text, text_size  # noqa: E402

# ---------------------------------------------------------------- palettes
# One 4-colour palette per asset. The GBC has 8 background + 8 sprite palettes,
# so this stays well inside the hardware budget.

UI = dict(ink="#0B1026", cream="#FFEBC2", amber="#F2A33C", blue="#5C8AC9")
WORLD = dict(lite="#B8E986", grass="#4FA83C", soil="#8A5A2E", dark="#14210F")
HERO = dict(lite="#FFD9A0", red="#E8503A", dark="#101828")
GOLD = dict(lite="#FFF0A8", gold="#F2B33C", brown="#8A5B1E")

TILE = 8
SCREEN_W, SCREEN_H = 160, 144
LEVEL_W, LEVEL_H = 20, 16          # playfield in tiles, drawn at screen row 2

# --- the level layout: (tile_x, tile_y, width, height), solid blocks ---------
LEVEL_BLOCKS = [
    (3, 2, 2, 1),
    (15, 2, 2, 1),
    (8, 4, 1, 2),
    (2, 8, 1, 3),
    (17, 8, 1, 3),
    (6, 10, 2, 1),
    (12, 10, 2, 1),
    (9, 6, 2, 2),
]

# --- where a star may spawn (tile_x, tile_y), tried in this order ------------
STAR_SPOTS = [
    (4, 13),
    (10, 1),
    (1, 1),
    (18, 5),
    (1, 6),
    (10, 9),
    (5, 5),
    (15, 13),
    (3, 13),
    (10, 13),
    (18, 10),
    (8, 14),
]

PLAYER_START = (2, 13)  # tile coords

# --- screen regions main.c pokes at runtime (all tile aligned) --------------
PRESS_REGION = (1, 12, 18, 2)   # x, y, w, h  — the blinking PRESS START band
BANNER_REGION = (4, 8, 12, 2)   # where the CLEAR box is stamped over the level


def rgb(hex_str: str):
    h = hex_str.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def cell(img, tx, ty, fn, *a):
    """Run fn(draw, px, py, *a) clipped to one 8x8 tile."""
    d = ImageDraw.Draw(img)
    fn(d, tx * TILE, ty * TILE, *a)


# ---------------------------------------------------------------- title

# star shapes, each drawn at a fixed offset inside its tile so tiles stay reusable
STAR_CELLS = [
    (1, 1, 0), (4, 0, 1), (6, 2, 2), (9, 1, 0), (12, 0, 1), (16, 2, 0),
    (18, 1, 1), (2, 3, 1), (7, 4, 0), (13, 3, 2), (17, 4, 1), (0, 5, 1),
    (5, 6, 0), (11, 5, 1), (15, 6, 0), (2, 7, 2), (18, 7, 1), (8, 8, 1),
]

HILL_HEIGHTS = [2, 4, 6, 8, 8, 6, 4, 2, 1, 0, 0, 1, 3, 5, 8, 8, 8, 6, 4, 2]


def _star(d, px, py, kind):
    c = UI
    if kind == 0:  # single pixel
        d.point((px + 3, py + 3), fill=rgb(c["cream"]))
    elif kind == 1:  # small plus
        for dx, dy in ((3, 2), (2, 3), (3, 3), (4, 3), (3, 4)):
            d.point((px + dx, py + dy), fill=rgb(c["cream"]))
    else:  # amber twinkle
        for dx, dy in ((3, 3), (4, 3), (3, 4), (5, 4), (4, 5)):
            d.point((px + dx, py + dy), fill=rgb(c["amber"]))


def _hill(d, px, py, h):
    c = UI
    if h <= 0:
        return
    top = py + (TILE - h)
    d.rectangle([px, top, px + 7, py + 7], fill=rgb(c["blue"]))
    d.line([px, top, px + 7, top], fill=rgb(c["cream"]))


def make_title(path):
    c = UI
    img = Image.new("RGB", (SCREEN_W, SCREEN_H), rgb(c["ink"]))
    d = ImageDraw.Draw(img)

    # sky: star tiles
    for tx, ty, kind in STAR_CELLS:
        _star(d, tx * TILE, ty * TILE, kind)

    # moon (4x4 tiles, upper right)
    d.ellipse([110, 6, 142, 38], fill=rgb(c["amber"]))
    for cx, cy, r in ((118, 15, 2), (129, 23, 3), (116, 27, 1), (125, 11, 1), (134, 16, 1), (122, 20, 2)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb(c["ink"]))

    # logo: scale 3, 1px drop shadow (a 3px shadow at scale 3 reads as a smear)
    tw, _ = text_size("TILE HOP", 3)
    lx, ly = (SCREEN_W - tw) // 2, 40
    draw_text(img, lx + 1, ly + 1, "TILE HOP", rgb(c["blue"]), scale=3)
    draw_text(img, lx, ly, "TILE HOP", rgb(c["cream"]), scale=3)

    tw, _ = text_size("GBC STARTER KIT", 1)
    draw_text(img, (SCREEN_W - tw) // 2, 68, "GBC STARTER KIT", rgb(c["blue"]), scale=1)

    # separator + dark band that "PRESS START" blinks inside of.
    # The blink region must be pure ink so hiding the text leaves no hole.
    d.line([0, 95, 159, 95], fill=rgb(c["blue"]))

    # hills: tile-quantised so a handful of tiles cover the whole band
    for tx, h in enumerate(HILL_HEIGHTS):
        _hill(d, tx * TILE, 14 * TILE, h)
    d.rectangle([0, 15 * TILE, 159, SCREEN_H - 1], fill=rgb(c["blue"]))

    # "PRESS START", scale 2, inside PRESS_REGION (tiles 1..18 x 12..13)
    px, py, pw, ph = PRESS_REGION
    tw, _ = text_size("PRESS START", 2)
    draw_text(img, px * TILE + (pw * TILE - tw) // 2, py * TILE + 1,
              "PRESS START", rgb(c["cream"]), scale=2)

    img.save(path)
    return path


# ---------------------------------------------------------------- hud

def make_hud(path):
    c = UI
    img = Image.new("RGB", (160, 16), rgb(c["ink"]))
    d = ImageDraw.Draw(img)
    d.line([0, 14, 159, 14], fill=rgb(c["blue"]))
    d.line([0, 15, 159, 15], fill=rgb(c["amber"]))
    draw_text(img, 4, 1, "SCORE", rgb(c["cream"]), scale=1)
    draw_text(img, 104, 1, "STAR", rgb(c["cream"]), scale=1)
    img.save(path)
    return path


# ---------------------------------------------------------------- level

def _grass(d, px, py, variant):
    c = WORLD
    d.rectangle([px, py, px + 7, py + 7], fill=rgb(c["grass"]))
    if variant == 0:
        for x, y in ((2, 3), (2, 1), (5, 4), (5, 2), (6, 6)):
            d.point((px + x, py + y), fill=rgb(c["lite"]))
        d.point((px + 4, py + 6), fill=rgb(c["dark"]))
    elif variant == 1:
        for x, y in ((1, 5), (1, 3), (3, 2), (6, 5), (4, 7)):
            d.point((px + x, py + y), fill=rgb(c["lite"]))
        d.point((px + 6, py + 1), fill=rgb(c["dark"]))
    else:
        for x, y in ((2, 6), (2, 4), (6, 2), (7, 3), (4, 0)):
            d.point((px + x, py + y), fill=rgb(c["lite"]))
        d.point((px + 0, py + 1), fill=rgb(c["dark"]))


def _brick(d, px, py, top):
    c = WORLD
    d.rectangle([px, py, px + 7, py + 7], fill=rgb(c["soil"]), outline=rgb(c["dark"]))
    d.line([px + 1, py + 3, px + 6, py + 3], fill=rgb(c["dark"]))
    d.line([px + 4, py, px + 4, py + 3], fill=rgb(c["dark"]))
    d.line([px + 2, py + 3, px + 2, py + 7], fill=rgb(c["dark"]))
    d.line([px + 6, py + 3, px + 6, py + 7], fill=rgb(c["dark"]))
    if top:  # lit top edge, "cap" row of a block
        d.line([px + 1, py + 1, px + 6, py + 1], fill=rgb(c["lite"]))
    else:
        d.line([px + 1, py + 1, px + 3, py + 1], fill=rgb(c["lite"]))


def solid_cells():
    cells = set()
    for x, y, w, h in LEVEL_BLOCKS:
        for ty in range(y, y + h):
            for tx in range(x, x + w):
                cells.add((tx, ty))
    return cells


def make_level(path):
    img = Image.new("RGB", (LEVEL_W * TILE, LEVEL_H * TILE), rgb(WORLD["grass"]))
    solid = solid_cells()
    for ty in range(LEVEL_H):
        for tx in range(LEVEL_W):
            variant = (tx * 7 + ty * 13) % 3
            cell(img, tx, ty, _grass, variant)
    for tx, ty in sorted(solid):
        cell(img, tx, ty, _brick, (tx, ty - 1) not in solid)  # cap rows get a lit top
    img.save(path)
    return path


# ---------------------------------------------------------------- sprites

HERO_FRAME = [
    "..3333..",
    ".333333.",
    "31111113",
    "31311313",
    "31111113",
    ".311113.",
    ".222222.",
    ".22..22.",
]

COIN_FRAMES = [
    [
        "..3333..",
        ".322223.",
        "32111223",
        "32111223",
        "32222223",
        "32222223",
        ".322223.",
        "..3333..",
    ],
    [
        "...33...",
        "...32...",
        "..321...",
        "..321...",
        "..321...",
        "..321...",
        "...32...",
        "...33...",
    ],
]


def sprite_png(grid, path, colors):
    img = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch != ".":
                d.point((x, y), fill=rgb(colors[int(ch) - 1]))
    img.save(path)
    return path


def make_player(path):
    return sprite_png(HERO_FRAME, path, [HERO["lite"], HERO["red"], HERO["dark"]])


def make_coin(path):
    img = Image.new("RGBA", (16, 8), (0, 0, 0, 0))
    cols = [GOLD["lite"], GOLD["gold"], GOLD["brown"]]
    for i, grid in enumerate(COIN_FRAMES):
        sub = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
        d = ImageDraw.Draw(sub)
        for y, row in enumerate(grid):
            for x, ch in enumerate(row):
                if ch != ".":
                    d.point((x, y), fill=rgb(cols[int(ch) - 1]))
        img.paste(sub, (i * 8, 0))
    img.save(path)
    return path


# ---------------------------------------------------------------- banner / blank

def make_banner(path):
    c = UI
    img = Image.new("RGB", (96, 16), rgb(c["ink"]))
    d = ImageDraw.Draw(img)
    tw, _ = text_size("CLEAR!", 2)
    draw_text(img, (96 - tw) // 2 + 1, 2, "CLEAR!", rgb(c["blue"]), scale=2)
    draw_text(img, (96 - tw) // 2, 1, "CLEAR!", rgb(c["cream"]), scale=2)
    d.rectangle([0, 0, 95, 15], outline=rgb(c["amber"]))
    img.save(path)
    return path


def make_blank(path):
    Image.new("RGB", (8, 8), rgb(UI["ink"])).save(path)
    return path


# ---------------------------------------------------------------- digits

def make_digits(path):
    img = Image.new("RGB", (80, 8), rgb(UI["ink"]))
    for n in range(10):
        draw_text(img, n * 8 + 1, 1, str(n), rgb(UI["cream"]), scale=1)
    img.save(path)
    return path


# ---------------------------------------------------------------- layout emit

def write_layout(path):
    """Emit the same numbers the art used, so C collision matches the pixels."""
    lines = [
        "/* Auto-generated by assets/make_art.py — edit the layout there, not here. */",
        "#ifndef LAYOUT_H",
        "#define LAYOUT_H",
        "",
        "#include <stdint.h>",
        "",
        f"#define LEVEL_W {LEVEL_W}",
        f"#define LEVEL_H {LEVEL_H}",
        f"#define LEVEL_SCREEN_Y 2   /* playfield starts on screen tile row 2 */",
        "",
        "/* solid blocks inside the playfield, in tiles: x, y, w, h */",
        "static const uint8_t BLOCK_RECTS[][4] = {",
    ]
    for bx, by, bw, bh in LEVEL_BLOCKS:
        lines.append(f"    {{{bx}, {by}, {bw}, {bh}}},")
    lines += [
        "};",
        f"#define BLOCK_COUNT {len(LEVEL_BLOCKS)}",
        "",
        "/* star spawn points in tiles, tried in this order */",
        "static const uint8_t STAR_SPOTS[][2] = {",
    ]
    for sx, sy in STAR_SPOTS:
        lines.append(f"    {{{sx}, {sy}}},")
    lines += [
        "};",
        f"#define STAR_SPOT_COUNT {len(STAR_SPOTS)}",
        "",
        f"#define PLAYER_START_X {PLAYER_START[0]}",
        f"#define PLAYER_START_Y {PLAYER_START[1]}",
        "",
        f"#define PRESS_X {PRESS_REGION[0]}",
        f"#define PRESS_Y {PRESS_REGION[1]}",
        f"#define PRESS_W {PRESS_REGION[2]}",
        f"#define PRESS_H {PRESS_REGION[3]}",
        "",
        f"#define BANNER_X {BANNER_REGION[0]}",
        f"#define BANNER_Y {BANNER_REGION[1]}",
        f"#define BANNER_W {BANNER_REGION[2]}",
        f"#define BANNER_H {BANNER_REGION[3]}",
        "",
        "#endif /* LAYOUT_H */",
        "",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


# ---------------------------------------------------------------- convert

CONVERSIONS = [
    # (png, name, mode, extra png2gbc args)
    ("title.png", "title", "bg", ["--map", "--dedup"]),
    ("hud.png", "hud", "bg", ["--map", "--dedup"]),
    ("level.png", "level", "bg", ["--map", "--dedup"]),
    ("digits.png", "digits", "bg", []),
    ("banner.png", "banner", "bg", ["--map", "--dedup"]),
    ("blank.png", "blank", "bg", []),
    ("player.png", "player", "sprite", []),
    ("coin.png", "coin", "sprite", []),
]


def convert(png_name, name, mode, extra):
    cmd = [sys.executable, PNG2GBC, os.path.join(HERE, png_name), "--mode", mode,
           "--name", name, "-o", os.path.join(GEN, name), "--no-preview", *extra]
    subprocess.run(cmd, check=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Draw the starter game's art and convert it to C.")
    ap.add_argument("--png-only", action="store_true", help="draw PNGs, skip the C conversion")
    args = ap.parse_args(argv)

    os.makedirs(GEN, exist_ok=True)
    jobs = [
        ("title.png", make_title),
        ("hud.png", make_hud),
        ("level.png", make_level),
        ("digits.png", make_digits),
        ("banner.png", make_banner),
        ("blank.png", make_blank),
        ("player.png", make_player),
        ("coin.png", make_coin),
    ]
    for name, fn in jobs:
        fn(os.path.join(HERE, name))
        print(f"drew {name}")
    print(f"wrote {write_layout(os.path.join(GEN, 'layout.h'))}")

    if args.png_only:
        return 0
    for png_name, name, mode, extra in CONVERSIONS:
        convert(png_name, name, mode, extra)

    # one sheet with every asset, for a quick eyeball pass
    sheet = Image.new("RGB", (SCREEN_W + 8 + 160, 300), (30, 30, 36))
    sheet.paste(Image.open(os.path.join(HERE, "title.png")), (0, 0))
    y = 150
    for name in ("hud.png", "digits.png", "banner.png", "blank.png"):
        im = Image.open(os.path.join(HERE, name)).convert("RGB")
        sheet.paste(im, (0, y))
        y += im.height + 4
    sheet.paste(Image.open(os.path.join(HERE, "level.png")), (SCREEN_W + 8, 0))
    x, y = SCREEN_W + 8, 132
    for name in ("player.png", "coin.png"):
        im = Image.open(os.path.join(HERE, name)).convert("RGBA")
        plate = Image.new("RGB", im.size, (40, 40, 48))
        plate.paste(im, (0, 0), im)
        sheet.paste(plate.resize((im.width * 3, im.height * 3), Image.NEAREST), (x, y))
        x += im.width * 3 + 8
    sheet.save(os.path.join(HERE, "sheet.png"))
    print("wrote assets/sheet.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
