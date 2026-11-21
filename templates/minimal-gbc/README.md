# TILE HOP — the starter game

A complete little Game Boy Color game in one C file, meant to be copied and broken.

- **Title screen** with art logo and a blinking `PRESS START` (tile-aligned so it can blink)
- **Gameplay**: 8×8 hero, D-pad movement, tile collision against brick blocks, 6 stars to collect
- **HUD**: custom digit tiles on their own background palette (`SCORE 00  STAR 6`)
- **Sound**: an envelope-driven beep on channel 1 when you collect a star
- **End state**: `CLEAR!` box, then a fresh round with new star positions
- **`SELECT`** returns to the title screen

## Build

```bash
./build.sh                 # -> build/tile-hop.gbc
./build.sh --assets        # redraw art from assets/make_art.py first
./build.sh --playtest      # build + run a scripted playtest
make                       # same build via make, if you have make
```

Needs GBDK-2020 (`GBDKDIR=/path/to/gbdk/`, trailing slash). `build.sh` finds it for you.

## Files

```
build.sh              lcc build script (no make required)
Makefile              the same thing for people who have make
src/main.c            the game — read this first, it is commented
src/gen/*.c,.h        generated tile data + palettes (do not hand-edit)
assets/make_art.py    draws every PNG and converts it; holds the level layout
assets/*.png          the source art
```

## How the pieces fit

`assets/make_art.py` owns the level layout (`LEVEL_BLOCKS`, `STAR_SPOTS`) and writes it
**twice**: once into `assets/level.png` and once into `src/gen/layout.h`, which
`main.c` uses for collision and star spawns. Change a block in the script, re-run it,
rebuild — the pixels and the collision always agree.

Tile slots are assigned once at the top of `main.c`:

```
T_TITLE 0 → title 129 tiles → hud 10 → level 5 → digits 10 → banner 24 → blank 1
                                                          sprites start at 179
```

The build fails with `#error` if the total outgrows VRAM (384) or a background index
outgrows 255.

## Playtest it yourself

```bash
python3 ../../tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:8,snap:title,press:start:4,wait:16,snap:play,hold:right:36,release:right,snap:score" \
  --out build/strip.png
```

The example in the repo's README was made by walking right from the start tile, which
picks up the first star: `SCORE 00` → `SCORE 01`, `STAR 6` → `STAR 5`.

To test the `CLEAR!` path without collecting six stars by hand, build a one-star ROM:

```bash
GBDKDIR=/path/to/gbdk/ /path/to/gbdk/bin/lcc -DSTAR_TOTAL=1 \
  -Wm-yc -Wm-yt0x1B -Wm-yn"TILEHOP" -o build/one-star.gbc src/main.c src/gen/*.c
```
