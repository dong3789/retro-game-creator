#!/usr/bin/env python3
"""
png2gbc.py — turn a PNG into Game Boy Color tile data (2bpp) + CGB palettes.

Output is plain C that drops straight into a GBDK-2020 project:

    png2gbc.py assets/player.png --mode sprite --name player
        -> player.c / player.h : player_tiles[] (16 bytes/tile), player_palette[4]
    png2gbc.py assets/title.png  --mode bg --map --name title
        -> title.c / title.h   : title_tiles[], title_map[] (8x8 chars), title_palette[4]

Every run also writes a <name>_preview.png at 4x zoom with a tile grid and tile
index labels, so a human (or an AI agent) can eyeball exactly what the ROM will
show before compiling.

Pass --palette "0B1026,FFEBC2,E8A03C,5C8AC9" when several assets must share one look:
the palette is written out exactly as given and every pixel snaps to its nearest entry.

Rules the GBC imposes (this tool enforces them):
  * 8x8 pixel tiles, 2 bits per pixel -> 4 colors per tile.
  * BG tiles: 4 opaque colors, index 0 is just another color.
  * Sprite tiles: index 0 = transparent, so only 3 drawable colors per sprite tile.
  * Colors are converted to BGR555 (15-bit), the format set_bkg_palette() wants.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass

try:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover - dependency guard
    sys.exit(
        "png2gbc.py needs numpy and pillow.\n"
        "  python3 -m pip install pillow numpy\n"
        f"(import error: {exc})"
    )

TILE = 8


# ---------------------------------------------------------------- helpers


def c_ident(text: str) -> str:
    ident = re.sub(r"[^0-9A-Za-z_]", "_", text).strip("_").lower()
    if not ident:
        ident = "asset"
    if ident[0].isdigit():
        ident = "a_" + ident
    return ident


def bgr555(rgb) -> int:
    """GBC palette entry: 0b0BBBBBGGGGGRRRRR"""
    r, g, b = (int(v) for v in rgb)
    return ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3)


def luminance(rgb) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


@dataclass
class Palette:
    colors: list  # list[tuple[int,int,int]]
    exact: bool   # True when the art fit the budget without quantization

    def rgb_array(self):
        return np.array(self.colors, dtype=np.int32)


def collect_opaque_colors(rgba: np.ndarray):
    """Return {rgb: pixel_count} for pixels that are not transparent."""
    alpha = rgba[:, :, 3]
    opaque = alpha >= 128
    rgb = rgba[:, :, :3]
    flat = rgb[opaque].reshape(-1, 3)
    if flat.size == 0:
        return {}
    keys, counts = np.unique(flat, axis=0, return_counts=True)
    return {tuple(int(v) for v in k): int(c) for k, c in zip(keys, counts)}


def quantize_to(rgba: np.ndarray, n: int) -> list:
    """Median-cut the opaque pixels down to n colors, deterministic order."""
    alpha = rgba[:, :, 3]
    rgb = rgba[:, :, :3].copy()
    opaque = alpha >= 128
    if not opaque.any():
        return [(0, 0, 0)] * n

    # Replace transparent pixels with the dominant opaque color so the
    # quantizer is not influenced by them.
    counts = collect_opaque_colors(rgba)
    dominant = max(counts.items(), key=lambda kv: (kv[1], kv[0]))[0]
    work = rgb.copy()
    work[~opaque] = dominant

    img = Image.fromarray(work.astype(np.uint8), mode="RGB")
    q = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[: n * 3]
    colors = [tuple(pal[i : i + 3]) for i in range(0, len(pal), 3)]
    while len(colors) < n:
        colors.append(colors[-1] if colors else (0, 0, 0))
    return colors


def parse_palette_spec(spec: str):
    """'#0B1026,#FFEBC2,...' -> [(11,16,38), ...]"""
    colors = []
    for chunk in spec.replace("[", "").replace("]", "").split(","):
        chunk = chunk.strip().lstrip("#")
        if not chunk:
            continue
        if len(chunk) == 3:
            chunk = "".join(c * 2 for c in chunk)
        if len(chunk) != 6:
            sys.exit(f"error: bad colour '{chunk}' in --palette (want RRGGBB hex values)")
        colors.append(tuple(int(chunk[i : i + 2], 16) for i in (0, 2, 4)))
    if not colors:
        sys.exit("error: --palette needs at least one colour")
    return colors


def build_palette(rgba: np.ndarray, mode: str, allow_quantize: bool, forced=None):
    counts = collect_opaque_colors(rgba)
    budget = 3 if mode == "sprite" else 4
    # For bg, transparent pixels still count as a color we must map somewhere.
    if mode == "bg" and (rgba[:, :, 3] < 128).any():
        counts.setdefault((0, 0, 0), 1)

    if forced:
        entries = list(forced)
        if mode == "sprite":
            # entry 0 is the transparent index and is never drawn
            draw = entries[:3]
            palette = [(0, 0, 0)] + draw
        else:
            palette = entries[:4]
        while len(palette) < 4:
            palette.append((0, 0, 0))
        pal_arr = np.array(palette, dtype=np.int32)
        start = 1 if mode == "sprite" else 0
        worst = 0
        for rgb in counts:
            d = ((pal_arr[start:] - np.array(rgb, dtype=np.int32)) ** 2).sum(axis=1)
            worst = max(worst, int(d.min()))
        if worst > 3 * 32 * 32:
            print("warning: some art colours are far from the forced palette "
                  "(each pixel snaps to its nearest entry, so the art may look off).")
        return Palette(palette, exact=worst == 0)

    if len(counts) <= budget:
        ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        colors = [c for c, _ in ordered]
        exact = True
    else:
        if not allow_quantize:
            names = ", ".join("#%02X%02X%02X" % c for c in list(counts)[:8])
            hint = (
                "Sprites reserve color index 0 for transparency, so a sprite tile "
                "has 3 drawable colors."
                if mode == "sprite"
                else "A background tile has 4 colors."
            )
            sys.exit(
                f"error: {len(counts)} distinct colors found, budget is {budget}.\n"
                f"  {hint}\n"
                f"  found: {names}{' ...' if len(counts) > 8 else ''}\n"
                "  fix the art palette, or pass --quantize to auto-reduce "
                "(nearest color is kept, dithering off)."
            )
        colors = quantize_to(rgba, budget)
        exact = False

    if mode == "sprite":
        # index 0 is transparent: keep it as pure black, never used for drawing
        palette = [(0, 0, 0)] + colors[:3]
        while len(palette) < 4:
            palette.append((0, 0, 0))
    else:
        palette = colors[:4]
        while len(palette) < 4:
            palette.append((0, 0, 0))
    return Palette(palette, exact)


def map_pixels(rgba: np.ndarray, palette: Palette, mode: str) -> np.ndarray:
    """RGB(A) image -> per-pixel color index image (uint8)."""
    h, w, _ = rgba.shape
    idx = np.zeros((h, w), dtype=np.uint8)
    alpha = rgba[:, :, 3]
    rgb = rgba[:, :, :3].astype(np.int32)

    pal = palette.rgb_array()
    start = 1 if mode == "sprite" else 0
    cand = pal[start:]
    # nearest palette entry for every pixel (vectorized, small n)
    d = ((rgb[:, :, None, :] - cand[None, None, :, :]) ** 2).sum(axis=3)
    nearest = d.argmin(axis=2).astype(np.uint8) + start
    idx[...] = nearest

    if mode == "sprite":
        idx[alpha < 128] = 0
    else:
        idx[alpha < 128] = 0
    return idx


def encode_tile(block: np.ndarray) -> bytes:
    """8x8 color indices -> 16 bytes, GB 2bpp (interleaved bitplanes per row)."""
    out = bytearray()
    for y in range(TILE):
        row = block[y]
        lo = hi = 0
        for x in range(TILE):
            v = int(row[x]) & 0x03
            lo |= (v & 1) << (7 - x)
            hi |= ((v >> 1) & 1) << (7 - x)
        out.append(lo)
        out.append(hi)
    return bytes(out)


def tiles_from_indices(idx: np.ndarray):
    h, w = idx.shape
    tw, th = w // TILE, h // TILE
    tiles = []
    for ty in range(th):
        for tx in range(tw):
            block = idx[ty * TILE : (ty + 1) * TILE, tx * TILE : (tx + 1) * TILE]
            tiles.append(encode_tile(block))
    return tiles, tw, th


def dedupe(tiles):
    seen = {}
    order = []
    remap = []
    for t in tiles:
        if t not in seen:
            seen[t] = len(order)
            order.append(t)
        remap.append(seen[t])
    return order, remap


# ---------------------------------------------------------------- preview


def _font(size=9):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10
        return ImageFont.load_default()


def render_preview(idx: np.ndarray, palette: Palette, mode: str, scale: int, out_path: str):
    h, w = idx.shape
    pal_rgb = np.array(palette.colors, dtype=np.uint8)
    if mode == "sprite":
        alpha = np.where(idx == 0, 0, 255).astype(np.uint8)
        rgb = pal_rgb[idx]
        img = Image.fromarray(np.dstack([rgb, alpha]), mode="RGBA")
    else:
        img = Image.fromarray(pal_rgb[idx], mode="RGB")

    big = img.resize((w * scale, h * scale), Image.NEAREST)
    header = 30
    canvas = Image.new("RGBA", (big.width, big.height + header), (24, 24, 28, 255))
    # checkerboard so transparency is visible
    if mode == "sprite":
        checker = Image.new("RGBA", big.size, (60, 60, 66, 255))
        d = ImageDraw.Draw(checker)
        for y in range(0, big.height, 8):
            for x in range(0, big.width, 8):
                if (x // 8 + y // 8) % 2:
                    d.rectangle([x, y, x + 7, y + 7], fill=(44, 44, 50, 255))
        checker.alpha_composite(big)
        big = checker
    canvas.paste(big, (0, header))

    d = ImageDraw.Draw(canvas)
    f = _font(12)
    fs = _font(9)
    # header: palette swatches + summary
    x = 6
    for i, c in enumerate(palette.colors):
        d.rectangle([x, 6, x + 16, 22], fill=tuple(c) + (255,), outline=(90, 90, 90, 255))
        label = "T" if (mode == "sprite" and i == 0) else str(i)
        d.text((x + 5, 8), label, fill=(255, 255, 255, 255) if luminance(c) < 140 else (0, 0, 0, 255), font=fs)
        x += 22
    d.text((x + 8, 8), f"{w}x{h}px  {w // 8}x{h // 8} tiles  {'sprite' if mode == 'sprite' else 'bg'}  "
                      f"{'exact' if palette.exact else 'QUANTIZED'}", fill=(220, 220, 220, 255), font=f)

    # tile grid + indices
    for ty in range(h // TILE):
        for tx in range(w // TILE):
            x0, y0 = tx * TILE * scale, header + ty * TILE * scale
            d.rectangle([x0, y0, x0 + TILE * scale - 1, y0 + TILE * scale - 1],
                        outline=(255, 0, 160, 90))
            n = ty * (w // TILE) + tx
            d.text((x0 + 1, y0), str(n), fill=(255, 0, 160, 220), font=fs)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    canvas.save(out_path)
    return out_path


# ---------------------------------------------------------------- code emit


def hex_lines(data, per_line=16):
    parts = ["0x%02X" % b for b in data]
    lines = []
    for i in range(0, len(parts), per_line):
        lines.append("    " + ", ".join(parts[i : i + per_line]))
    return ",\n".join(lines)


def write_outputs(name: str, tiles, palette: Palette, map_data, map_dims, expr_mode: str):
    guard = f"_{name.upper()}_H"
    h_lines = [
        f"/* Auto-generated by tools/png2gbc.py — edit the PNG, not this file. */",
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        "#include <stdint.h>",
        "#include <gb/cgb.h>",
        "",
        f"#define {name.upper()}_TILE_COUNT {len(tiles)}",
        f"#define {name.upper()}_TILE_BYTES {len(tiles) * 16}",
        f"#define {name.upper()}_TILE_W {map_dims[0] if map_data else 1}",
        f"#define {name.upper()}_TILE_H {map_dims[1] if map_data else len(tiles)}",
    ]
    h_lines += [
        "",
        f"extern const uint8_t {name}_tiles[{len(tiles) * 16}];",
        f"extern const palette_color_t {name}_palette[4];",
    ]
    if map_data:
        mw, mh = map_dims
        h_lines += [
            f"#define {name.upper()}_MAP_W {mw}",
            f"#define {name.upper()}_MAP_H {mh}",
            f"extern const uint8_t {name}_map[{mw * mh}];",
        ]
    h_lines += ["", f"#endif /* {guard} */", ""]

    c_lines = [
        f'/* Auto-generated by tools/png2gbc.py from the "{name}" PNG — do not edit. */',
        f'#include "{name}.h"',
        "",
        f"/* 2bpp tile data, {len(tiles)} tiles x 16 bytes ({expr_mode}) */",
        f"const uint8_t {name}_tiles[{len(tiles) * 16}] = {{",
        hex_lines(b"".join(tiles)),
        "};",
        "",
        f"/* BGR555 palette: " + ", ".join("#%02X%02X%02X" % c for c in palette.colors) + " */",
        f"const palette_color_t {name}_palette[4] = {{",
        "    " + ", ".join("0x%04X" % bgr555(c) for c in palette.colors),
        "};",
    ]
    if map_data:
        mw, mh = map_dims
        c_lines += [
            "",
            f"/* {mw}x{mh} tile map (row-major, relative indices — use set_bkg_based_tiles) */",
            f"const uint8_t {name}_map[{mw * mh}] = {{",
            hex_lines(map_data, 20),
            "};",
        ]
    c_lines.append("")
    return "\n".join(h_lines), "\n".join(c_lines)


# ---------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Convert PNG art into GBC 2bpp tiles + BGR555 palettes (+ optional tile map).",
        epilog="Example: png2gbc.py assets/player.png --mode sprite --name player",
    )
    ap.add_argument("input", help="source PNG (any size; padded to a multiple of 8)")
    ap.add_argument("-o", "--out", help="output directory or basename (default: next to the PNG)")
    ap.add_argument("--name", help="C symbol prefix (default: input file stem)")
    ap.add_argument("--mode", choices=("bg", "sprite"), default="bg",
                    help="bg = 4 colors, sprite = 3 colors + transparency (default: bg)")
    ap.add_argument("--map", action="store_true",
                    help="also emit a tile map for background art (use with set_bkg_based_tiles)")
    ap.add_argument("--quantize", action="store_true",
                    help="auto-reduce to the 4-color budget instead of failing")
    ap.add_argument("--palette",
                    help="force the palette: 'RRGGBB,RRGGBB,...' (bg: up to 4, sprite: up to 3 "
                         "drawable colours; pixels snap to the nearest entry)")
    ap.add_argument("--dedup", action="store_true",
                    help="merge identical tiles and remap the map (saves VRAM)")
    ap.add_argument("--preview", help="preview PNG path (default: <name>_preview.png)")
    ap.add_argument("--no-preview", action="store_true", help="skip the preview image")
    ap.add_argument("--scale", type=int, default=4, help="preview zoom (default 4)")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.input):
        sys.exit(f"error: no such file: {args.input}")

    name = c_ident(args.name or os.path.splitext(os.path.basename(args.input))[0])

    src = Image.open(args.input).convert("RGBA")
    w, h = src.size
    pad_w = (-w) % TILE
    pad_h = (-h) % TILE
    if pad_w or pad_h:
        print(f"note: padding {w}x{h} to {w + pad_w}x{h + pad_h} (tiles are 8x8)")
        padded = Image.new("RGBA", (w + pad_w, h + pad_h), (0, 0, 0, 0))
        padded.paste(src, (0, 0))
        src = padded
    rgba = np.array(src, dtype=np.uint8)
    if rgba.shape[0] < TILE or rgba.shape[1] < TILE:
        sys.exit("error: art must be at least 8x8 pixels.")

    forced = parse_palette_spec(args.palette) if args.palette else None
    if forced and len(forced) > (3 if args.mode == "sprite" else 4):
        sys.exit(f"error: --palette has {len(forced)} colours; a {args.mode} has "
                 f"{'3' if args.mode == 'sprite' else '4'}.")
    palette = build_palette(rgba, args.mode, args.quantize, forced)
    idx = map_pixels(rgba, palette, args.mode)

    tiles, tw, th = tiles_from_indices(idx)
    map_data = None
    map_dims = None
    if args.dedup:
        before = len(tiles)
        tiles, remap = dedupe(tiles)
        print(f"dedup: {before} -> {len(tiles)} tiles")
    if args.map:
        if args.mode == "sprite":
            sys.exit("error: --map is for background art; sprites are placed with move_sprite().")
        map_data = remap if args.dedup else list(range(tw * th))
        map_dims = (tw, th)
        # sanity: map values must address the tiles we emitted
        if max(map_data) >= len(tiles):
            sys.exit("internal error: map references missing tiles")
        if tw > 32 or th > 32:
            print(f"warning: {tw}x{th} tiles exceeds one screen (20x18) — "
                  "use set_bkg_based_submap() with MAP_W when scrolling.")

    if len(tiles) > 256:
        print(f"warning: {len(tiles)} tiles -> VRAM holds only 384 total "
              "(shared with sprites and the font). Consider --dedup.")

    out_base = args.out or os.path.join(os.path.dirname(os.path.abspath(args.input)), name)
    out_dir = os.path.dirname(os.path.abspath(out_base))
    stem = os.path.basename(out_base)
    os.makedirs(out_dir, exist_ok=True)
    h_path = os.path.join(out_dir, stem + ".h")
    c_path = os.path.join(out_dir, stem + ".c")
    header, source = write_outputs(name, tiles, palette, map_data, map_dims, args.mode)
    with open(h_path, "w", encoding="utf-8") as fh:
        fh.write(header)
    with open(c_path, "w", encoding="utf-8") as fh:
        fh.write(source)

    preview_path = None
    if not args.no_preview:
        preview_path = args.preview or os.path.join(out_dir, stem + "_preview.png")
        render_preview(idx, palette, args.mode, args.scale, preview_path)

    print(f"{name}: {args.mode}, {tw}x{th} tiles, {len(tiles)} unique, "
          f"{len(tiles) * 16} bytes of tile data"
          + (f", map {map_dims[0]}x{map_dims[1]} ({len(map_data)} bytes)" if map_data else ""))
    print("palette: " + ", ".join("#%02X%02X%02X" % c for c in palette.colors) + " (BGR555)")
    print(f"wrote: {c_path}")
    print(f"wrote: {h_path}")
    if preview_path:
        print(f"wrote: {preview_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
