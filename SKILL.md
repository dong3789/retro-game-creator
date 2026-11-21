---
name: gameboy-color-games
description: Make, modify, debug and playtest real Game Boy Color games (.gbc) in C with GBDK-2020, then run them on an R36S/Anbernic-class handheld or any emulator. Use when the task is drawing GB tile art, writing or fixing GBDK C code, compiling a ROM with lcc, verifying a ROM headlessly (PyBoy screenshot strips), or preparing a ROM for a handheld's SD card.
---

# Game Boy Color game creation

You are building a game that runs on **real Game Boy Color hardware and its clones**,
not on a phone or in a browser. That single fact drives everything below: tiny art,
hard memory budgets, a 4 MHz CPU, and no OS — just a loop and a screen.

The pipeline in this repo exists so an AI agent can go all the way from an idea to a
ROM it has *seen running*:

```
plan → art PNG + tiles (tools/png2gbc.py) → C code → build (lcc) → playtest (tools/playtest.py)
     → LOOK AT THE FRAMES → fix → repeat → docs/images/*.png + .gbc to the SD card
```

Never claim a game works because it compiled. A ROM that compiles and shows a blank
screen is the normal failure mode. Build it, run the playtest, and look at the pixels.

---

## 1. The hardware, in numbers

| Thing | Value | What it means for you |
| --- | --- | --- |
| Resolution | 160 × 144 px | 20 × 18 tiles. That is the whole canvas. |
| Tile | 8 × 8 px, 2 bits per pixel | 4 colours per tile, 16 bytes of tile data. |
| Tile storage | 384 tiles, 8 KiB VRAM (`0x8000`–`0x9FFF`) | Background *and* sprites share it. |
| Tile map index | one byte per cell | BG tiles must live in slots 0–255. |
| Background map | 32 × 32 tiles (256 × 256 px) | Visible 20 × 18 window can scroll over it. |
| Palettes | 8 BG + 8 OBJ, 4 colours each | Colour is per palette; per-cell palette index is a map attribute. |
| Palette format | 15-bit BGR555, `0b0BBBBBGGGGGRRRRR` | 32 levels per channel; `RGB8()` converts 8-bit values. |
| Sprites | 8 × 8 or 8 × 16, max 40 in OAM | Max **10 per scanline** — more than that silently vanish. |
| Sprite coords | OAM Y = screen Y + 16, X = screen X + 8 | `move_sprite()` takes OAM coords, so add the offsets. |
| Frame | 59.7 fps, ~70 224 cycles | One frame is your whole budget. |
| CPU | 4.19 MHz (CGB double speed 8.38) | No floats in hot code; use `uint8_t`/fixed point. |
| RAM | 8 KiB WRAM (CGB: 32 KiB in 4 KiB banks) | Big arrays must be `const` (ROM) not RAM. |
| Sound | 4 channels: 2 square, 1 wave, 1 noise | Registers `NR10_REG`–`NR52_REG`. |
| ROM | MBC5, up to 512 KiB | You will not run out for a jam-sized game. |

Colour depth is the thing people get wrong first. It is **4 colours per tile**, not 4
colours per screen: you can put the HUD on one palette and the world on another, and
that is exactly how CGB games look colourful.

## 2. Toolchain

**GBDK-2020 4.5.0** (SDCC under the hood) is the compiler. Get it from
<https://github.com/gbdk-2020/gbdk-2020/releases> (`gbdk-linux64.tar.gz`, or the
macOS/Windows build), unpack anywhere, and point `GBDKDIR` at it.

Two gotchas that cost real time:

1. **`GBDKDIR` must end with a slash.** `lcc` appends `bin/sdcc` literally, so
   `GBDKDIR=/opt/gbdk` turns into `/opt/gbdkbin/sdcc`. Use `/opt/gbdk/`.
2. **`-Wm-yc` and `-Wm-yC` are not the same flag.** Lowercase `yc` = CGB-compatible
   (header byte `0x143 = 0x80`, also boots on a DMG). Capital `yC` = CGB-*only*
   (`0xC0`). Check with:
   `python3 -c "d=open('build/game.gbc','rb').read(); print(hex(d[0x143]))"`

Build flags that matter:

| Flag | Effect |
| --- | --- |
| `-Wm-yc` | CGB compatible ROM (works on DMG too, in grey) |
| `-Wm-yC` | CGB-only ROM |
| `-Wm-yt0x1B` | MBC5 + RAM + battery (save data later) |
| `-Wm-yn"NAME"` | ROM title, ≤ 11 chars, uppercase |
| `-Wm-ys` | Super Game Boy compatible |

Helper tools in `tools/` (all need Python 3 + pillow + numpy; playtest also needs pyboy):

```
./tools/check_env.sh          # what is installed, what is missing
python3 tools/png2gbc.py      # PNG -> tile data + palette C files (+ preview)
python3 tools/artfont.py      # 5x7 pixel text drawn into a PNG
python3 tools/playtest.py     # headless PyBoy run + screenshot strip
```

## 3. The loop, step by step

### 3.1 Plan the game in one paragraph plus one acceptance test

Write down the smallest thing that is still a game (title → play → score → end) and
the exact input sequence that proves it works:

> Hold RIGHT for 40 frames: the hero walks right, picks up a star, HUD score goes 0 → 1.

That sentence becomes the playtest script later. Games without a testable sentence
tend to end up as a title screen with nothing behind it.

### 3.2 Art first, as PNG, and look at it before writing C

Draw at 1:1, then convert. **Align anything that changes at runtime to tile
boundaries** (8 px), because the ROM can only poke whole tiles.

```
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/title.png  --mode bg --map --dedup --name title -o src/gen/title
```

- `--mode bg` → 4 colours; `--mode sprite` → 3 colours + index 0 transparent.
- `--map` emits a tile map (pair with `set_bkg_based_tiles`).
- `--dedup` merges identical tiles and remaps the map. **Use it on backgrounds.**
- `--palette "0B1026,FFEBC2,E2A33C,5C8AC9"` forces the palette instead of
  deriving it (needed when two assets must share one look).
- Every run writes a 4× preview PNG with a tile grid — open it and check the art
  before compiling. `--quantize` exists but a hand-fixed palette looks better.

For text baked into art (logos, "PRESS START"), use `tools/artfont.py`
(`draw_text()` in library mode) — it renders a 5×7 font at any integer scale.

**Tile economy is the skill.** A background where every 8×8 cell is unique costs one
tile per cell: a 20×18 screen = 360 tiles, and the whole VRAM is 384. Real GB games
draw a small tileset (3 grass tiles, 1 brick tile …) and repeat it through the map,
which is why a level can cost 5 tiles. Random per-pixel noise (stars, dust, gradients)
destroys this — place decorative pixels at repeatable in-tile offsets instead.

### 3.3 Write the C

Start from `templates/minimal-gbc/` — a complete title → play → score → clear game
in one file. Copy it and change things; do not start from a blank file.

### 3.4 Build

```
cd templates/minimal-gbc
./build.sh                 # lcc directly, no make needed
./build.sh --assets        # redraw art + re-convert + build
make                       # same thing via the Makefile if make is installed
```

`build.sh` searches `$GBDKDIR`, `/opt/gbdk`, `~/gbdk`, `/usr/local/gbdk` and a local
`.tmp/gbdk`, so it usually works with no setup.

### 3.5 Playtest and **look**

```
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,snap:title,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/playtest-strip.png
```

Script grammar: `wait:N`, `press:BTN:N` (down, N frames, up), `hold:BTN:N`
(leave held), `release:BTN`, `snap[:LABEL]`. Buttons: `up down left right a b start select`.
`--frames-dir DIR` also writes every snapshot as its own PNG; `--json` prints a
machine-readable summary.

Then **read the strip image**. Judge these, in this order:

1. Is anything on screen at all? (blank = LCDC/display or palette problem)
2. Is the palette right? (washed out / all one colour = palette not set, or
   attribute map wrote 0 everywhere)
3. Is the text/glyph art legible? (off-by-one tile, missing tile index)
4. Did the input change anything? (frozen game = your loop never reads `joypad()`
   or `vsync()` is not called)
5. Are the sprites where the score says they should be? (collision box ≠ sprite box)

The tool prints warnings for the classic ones (all frames identical, ≤ 2 colours,
blank frames). Treat a warning as a bug until proven otherwise.

### 3.6 Ship the evidence

Keep one strip and one title screenshot in `docs/images/` and link them from the
README. That is the difference between "an AI wrote a game" and "here is the game".

## 4. GBDK-2020 C cookbook

### Skeleton

```c
#include <gbdk/platform.h>
#include <gb/cgb.h>
#include <stdint.h>

void main(void) {
    DISPLAY_OFF;
    SPRITES_8x8;
    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    while (1) {
        vsync();                 /* wait for VBlank: this is your frame clock */
        if (joypad() & J_A) { /* ... */ }
    }
}
```

`vsync()` is not optional — it is what keeps you at 59.7 fps and stops tearing.
Everything that writes VRAM outside VBlank is free to happen at any time on modern
hardware, but OAM/palette changes are safest right after `vsync()`.

### Joypad

```c
uint8_t joy = joypad();               /* J_LEFT J_RIGHT J_UP J_DOWN J_A J_B J_START J_SELECT */
if (joy & J_START) { ... }            /* held */
waitpadup();                          /* wait for release — use after a menu confirm */
```

Edge-trigger (press *this* frame only) — keep the previous frame:

```c
static uint8_t prev;
uint8_t pressed = joy & ~prev;        /* newly pressed bits */
prev = joy;
```

### Background tiles

```c
set_bkg_data(TILE_BASE, TILE_COUNT, my_tiles);          /* upload tile pixels */
set_bkg_tiles(x, y, w, h, map);                          /* absolute tile indices */
set_bkg_based_tiles(x, y, w, h, map, TILE_BASE);         /* map + base offset */
set_bkg_submap(x, y, w, h, big_map, big_map_w);          /* cut a window out of a large map */
set_bkg_based_submap(x, y, w, h, big_map, big_map_w, TILE_BASE);
```

The `based_` variants are what generated art wants: a converted PNG's map contains
0-based indices, and the base slides it to wherever you loaded the tiles.

### CGB palettes and per-cell palette attributes

```c
if (DEVICE_SUPPORTS_COLOR) {                  /* CGB/GBA only; on DMG this is grey */
    set_bkg_palette(1, 1, my_bg_palette);     /* palette slot 1, 1 palette, 4 colours */
    set_sprite_palette(0, 1, my_obj_palette);
}

/* which palette a map cell uses: the attribute map, VRAM bank 1 */
VBK_REG = VBK_ATTRIBUTES;
set_bkg_tiles(x, y, w, 1, row_of_palette_numbers);   /* 0..7 */
VBK_REG = VBK_TILES;                                 /* ALWAYS switch back */
```

Attribute bits: `0–2` palette, `3` tile VRAM bank, `5` X flip, `6` Y flip,
`7` BG-over-OBJ priority. Forgetting to switch `VBK_REG` back writes your next
tile map into the attribute map and the screen turns into garbage.

### Sprites

```c
set_sprite_data(SPR_TILE, TILE_COUNT, my_tiles);   /* same VRAM as BG: pick free slots */
set_sprite_tile(0, SPR_TILE);                       /* slot 0 shows tile SPR_TILE */
set_sprite_prop(0, S_PALETTE | S_FLIPX | S_PRIORITY);
move_sprite(0, x + 8, y + 16);                      /* OAM offsets! */
```

GBDK keeps a `shadow_OAM[]` and DMA-copies it every VBlank, so `move_sprite()` is
cheap — but it is still one call per sprite per frame. Sprites with a lower index are
drawn on top. Hide one by moving it to `(0, 0)`.

### Sound

```c
NR52_REG = 0x80;          /* sound on */
NR51_REG = 0x11;          /* channel 1 to both outputs */
NR50_REG = 0x77;          /* master volume */
NR10_REG = 0x00; NR11_REG = 0x80;   /* sweep off, 50% duty */
NR12_REG = 0xF7;                    /* volume 15, envelope down, pace 7: it fades itself */
NR13_REG = 0x40; NR14_REG = 0x86;   /* frequency low, then trigger + freq high */
```

Sound is fire-and-forget: start a tone and let the envelope fade it. Do not block.

### Random numbers, speed

```c
#include <rand.h>
initrand(DIV_REG);          /* seed from the divider register: varies per power-on */
uint8_t n = rand() % 10;

if (DEVICE_SUPPORTS_COLOR) cpu_fast();   /* CGB double speed; doubles your frame budget */
```

## 5. Budgets you must not blow

| Budget | Limit | Check |
| --- | --- | --- |
| Tiles in VRAM | 384 | sum of every asset's `*_TILE_COUNT` |
| BG tile indices | 256 | BG must start below 256; sprites can share the rest |
| Sprites on screen | 40 total, 10 per scanline | count `move_sprite` calls |
| Frame time | 70 224 cycles | if it flickers/slows, profile the biggest loop |
| WRAM | 8 KiB (32 KiB on CGB) | big tables go in `const` (ROM) |

Give each asset an explicit base at the top of the file so nothing overlaps:

```c
#define T_TITLE  0
#define T_HUD    (T_TITLE + TITLE_TILE_COUNT)
#define T_LEVEL  (T_HUD   + HUD_TILE_COUNT)
/* ... */
#if ALL_TILES > 384
#error "too many tiles for VRAM"
#endif
```

That `#error` has saved more builds than any debugging session.

## 6. Text: the font, the BG map and the window trap

Everything shares one 20 × 18 character grid. Two ways to put text on screen:

- **Bake the glyphs into your tileset** (what the starter game does): digits drawn as
  tiles, stamped with `set_bkg_tiles`. Full palette control, no surprises.
- **GBDK's console font**: verified in 4.5.0 —

  ```c
  #include <gbdk/console.h>
  #include <gbdk/font.h>
  font_init();
  font_set(font_load(font_ibm));   /* uploads the font, returns the first tile slot */
  gotoxy(0, 0);
  printf("SCORE %d", score);
  ```

  `printf()` writes **tile indices into the background map** at the `gotoxy()` position
  (not the window, despite older GBDK docs), so each character you print *replaces*
  whatever map cell was there — a score line over your level eats the tiles behind it.
  Print inside cells you reserved, or save/restore the map bytes.

The **window** is a separate layer with its own map (usually `0x9C00`), enabled with
`SHOW_WIN` and positioned with `move_win(x, y)` (`WX=7` is the left edge). The trap:
the window is always the *full height* of the screen from `WY` down, so it cannot be a
one-row HUD — the rows beneath the one you filled show whatever the window map holds
(usually blank tiles) and hide the game. Use it for a full text box or a menu, not a
strip. If `printf` output seems missing, check whether the window is enabled and
covering the BG you printed into.

## 7. Running it on the R36S (and friends)

The R36S is an RK3326 handheld with a **640 × 480** panel running ArkOS/dArkOS
(EmulationStation + RetroArch).

1. Build the `.gbc` (or take `templates/minimal-gbc/build/tile-hop.gbc`).
2. Copy it to the **EASYROMS** partition in the GBC folder: `EASYROMS/roms/gbc/`
   (some images show it as `EASYROMS/gbc/`). Folder names are lowercase and
   case-sensitive; if the game does not appear in the menu, you are in the wrong
   folder — not the wrong ROM.
3. Launch it. **Gambatte** is the default and the best all-round GBC core; **SameBoy**
   is the most accurate; mGBA also works.
4. Display: GBC is 160 × 144 = **exactly 10:9**, and the panel is 4:3, so
   `Settings → Video → Scaling`:
   - `Aspect Ratio: Core Provided` + `Integer Scale: ON` → **480 × 432 (3×)**.
     Perfect square pixels, black bars at the sides. This is the right answer.
   - 4× (640 × 576) does not fit in 480 px of height, so integer scaling silently
     falls back to 3× anyway.
   - "Stretch to fill" distorts the 10:9 image ~20 % wider — avoid it for pixel art.
5. Optional: `Core Options → Color Correction: GBC Only` for real-hardware colour,
   and an `lcd3x` shader if you want the LCD grid.

Same ROM, no changes: Miyoo Mini (Onion), Anbernic RG35XX, Retroid, a real GBC with
a flash cart, or `sameboy`/`mgba` on a desktop.

## 8. Pitfalls that actually happen

| Symptom | Cause | Fix |
| --- | --- | --- |
| Blank white/green screen | `DISPLAY_ON` missing, or palettes never set (all colours the same) | check `DISPLAY_ON`, `SHOW_BKG`, `set_bkg_palette` |
| Screen full of garbage tiles | wrote a map while `VBK_REG = VBK_ATTRIBUTES` | switch back to `VBK_TILES` |
| Game frozen, input ignored | no `joypad()` in the loop, or a `while(!(joypad() & J_A));` spin that never calls `vsync()` | put `vsync()` first in the loop |
| Sprites invisible | tile slot collides with BG tiles, `SHOW_SPRITES` off, or `move_sprite(x, y)` without the +8/+16 | reserve sprite slots, add offsets |
| Sprites flicker and drop out | more than 10 per scanline | spread them vertically or merge into 8×16 |
| Art looks melted / wrong colours | palette order changed (the tool sorts by pixel frequency) | use the generated `*_palette[]` array, or `--palette` |
| `.../gbdkbin/sdcc: No such file` | `GBDKDIR` has no trailing slash | `GBDKDIR=/opt/gbdk/` |
| ROM doesn't boot on a real DMG | built with `-Wm-yC` (CGB only) | use `-Wm-yc` |
| CGB colours fine in emulator, grey on DMG | CGB palette calls are ignored on DMG | expected; guard with `DEVICE_SUPPORTS_COLOR` |
| `error: 12 distinct colors found, budget is 4` | art has too many colours | reduce the art palette, or `--quantize` |
| ROM grows past 32 KiB and code stops running | data in bank 1 without `BANKED`/`SWITCH_ROM` | stay small, or learn banking (`BANKREF`, `SWITCH_ROM`) |

## 9. Definition of done

- [ ] `./build.sh` succeeds with no warnings, ROM under 512 KiB
- [ ] Header byte `0x143` is what you meant (`0x80` compatible / `0xC0` CGB-only)
- [ ] Playtest strip shows: title, play screen, one interaction that changes state
- [ ] You *looked* at the strip and the text is legible
- [ ] Score / lives / end state actually reachable (test it with a small constant —
      `-DSTAR_TOTAL=1` builds a one-star ROM that clears in one move)
- [ ] `docs/images/` has the strip, README links it
- [ ] `EASYROMS/roms/gbc/` copy boots on the handheld
