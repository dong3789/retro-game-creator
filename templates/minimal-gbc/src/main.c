/*
 * TILE HOP — a tiny, complete Game Boy Color game (GBDK-2020).
 *
 * It exists to be read and copied. Everything is in one file on purpose:
 *
 *   screen_title()  title art + a blinking PRESS START, waits for the START key
 *   play_init()     loads the playfield, builds the collision grid, spawns stars
 *   main loop       vsync-paced, reads the joypad, moves, collides, scores, beeps
 *   show_banner()   "CLEAR!" box, then a new round with fresh stars
 *
 * Hardware facts this file is built around (see SKILL.md for the whole list):
 *   - 160x144 screen = 20x18 tiles of 8x8 pixels. Level rows start at row 2
 *     because the HUD owns rows 0..1.
 *   - 8x8 tiles, 2 bits per pixel, so 4 colours per tile. Background and sprite
 *     tiles share the same 384-tile VRAM: the #define block below keeps the
 *     totals inside it, and the compiler stops you if they do not fit.
 *   - Background palette attributes are per map cell: write them with
 *     VBK_REG = VBK_ATTRIBUTES, then put it back.
 *   - Sprite Y is offset by 16 and X by 8 in OAM coordinates.
 *   - CGB-only registers are guarded with DEVICE_SUPPORTS_COLOR so the same ROM
 *     still boots (in four shades of grey) on a DMG.
 */
#include <gbdk/platform.h>
#include <gb/cgb.h>
#include <gb/gb.h>
#include <stdint.h>
#include <string.h>

#include "gen/title.h"
#include "gen/hud.h"
#include "gen/level.h"
#include "gen/digits.h"
#include "gen/banner.h"
#include "gen/blank.h"
#include "gen/player.h"
#include "gen/coin.h"
#include "gen/layout.h"

/* SDCC is noisy about tile index arithmetic that is deliberately uint8_t:
   158 = overflow in implicit constant conversion, 110 = the optimizer
   reshaping a conditional. Both are expected in GB tile code. */
#pragma disable_warning 158
#pragma disable_warning 110

/* ------------------------------------------------------------------ budget */
/* Background tile slots, handed out once at the top so nothing overlaps.     */
#define T_TITLE  0
#define T_HUD    (T_TITLE + TITLE_TILE_COUNT)
#define T_LEVEL  (T_HUD + HUD_TILE_COUNT)
#define T_DIGIT  (T_LEVEL + LEVEL_TILE_COUNT)
#define T_BANNER (T_DIGIT + DIGITS_TILE_COUNT)
#define T_BLANK  (T_BANNER + BANNER_TILE_COUNT)
#define T_SPR    (T_BLANK + BLANK_TILE_COUNT)     /* sprites live in the same VRAM */
#define T_COIN   (T_SPR + PLAYER_TILE_COUNT)

#define BG_TILES    (T_SPR)
#define ALL_TILES   (T_COIN + COIN_TILE_COUNT)

#if BG_TILES > 256
#error "background tiles must fit in a 0..255 map index"
#endif
#if ALL_TILES > 384
#error "too many tiles for the 384-tile VRAM: dedup your art or drop an asset"
#endif

/* Background palettes */
#define PAL_TITLE  0
#define PAL_LEVEL  1
#define PAL_DIGIT  2
#define PAL_HUD    3
#define PAL_BANNER 4

/* Sprite palettes */
#define SPAL_HERO  0
#define SPAL_COIN  1

/* ------------------------------------------------------------------ state */
#ifndef STAR_TOTAL
#define STAR_TOTAL   6        /* -DSTAR_TOTAL=1 gives a one-star ROM for testing the CLEAR path */
#endif
#define NUM_SPRITES  (1 + STAR_TOTAL)   /* 0 = hero, 1..N = stars (max 40 OAM) */
#define MOVE_SPEED   1                  /* pixels per frame */

static uint8_t solid[LEVEL_H][LEVEL_W];
static uint8_t px, py;                       /* hero, level pixel coords */
static uint8_t score, remaining;
static uint8_t star_spot[STAR_TOTAL];        /* index into STAR_SPOTS */
static uint8_t next_spot;
static uint16_t frame;

/* ------------------------------------------------------------------ helpers */
static void put_attr_rect(uint8_t x, uint8_t y, uint8_t w, uint8_t h, uint8_t pal) {
    uint8_t row[LEVEL_W];
    uint8_t i;
    for (i = 0; i < w; i++) row[i] = pal;
    VBK_REG = VBK_ATTRIBUTES;
    for (i = 0; i < h; i++) set_bkg_tiles(x, y + i, w, 1, row);
    VBK_REG = VBK_TILES;
}

static void draw_digit(uint8_t cx, uint8_t cy, uint8_t n) {
    uint8_t tile = T_DIGIT + (n > 9 ? 9 : n);
    set_bkg_tiles(cx, cy, 1, 1, &tile);
}

static void draw_score(void) {
    draw_digit(5, 0, score / 10);
    draw_digit(6, 0, score % 10);
    draw_digit(17, 0, remaining);
}

/* ------------------------------------------------------------------ sound */
/* Channel 1, square wave, hardware volume envelope so it fades on its own.
   You only have to start it; the sound CPU does the rest.                    */
static void sfx_init(void) {
    NR52_REG = 0x80;   /* sound on */
    NR51_REG = 0x11;   /* channel 1 -> left + right */
    NR50_REG = 0x77;   /* master volume 7/7 */
}

static void sfx_tone(uint8_t freq_lo, uint8_t freq_hi) {
    NR10_REG = 0x00;              /* no sweep */
    NR11_REG = 0x80;              /* 50% duty, length unused */
    NR12_REG = 0xF7;              /* volume 15, envelope decreasing, pace 7 */
    NR13_REG = freq_lo;
    NR14_REG = 0x80 | (freq_hi & 0x07); /* trigger */
}

static void sfx_star(void) { sfx_tone(0x40, 0x86); }
static void sfx_clear(void) { sfx_tone(0x00, 0x87); }

/* ------------------------------------------------------------------ title */
static void press_start_visible(uint8_t on) {
    uint8_t buf[PRESS_W * PRESS_H];
    uint8_t r, c;
    if (on) {
        for (r = 0; r < PRESS_H; r++)
            for (c = 0; c < PRESS_W; c++)
                buf[r * PRESS_W + c] =
                    T_TITLE + title_map[(PRESS_Y + r) * TITLE_MAP_W + (PRESS_X + c)];
    } else {
        for (r = 0; r < PRESS_W * PRESS_H; r++) buf[r] = T_BLANK;
    }
    set_bkg_tiles(PRESS_X, PRESS_Y, PRESS_W, PRESS_H, buf);
}

static void screen_title(void) {
    uint16_t i;

    set_bkg_data(T_TITLE, TITLE_TILE_COUNT, title_tiles);
    set_bkg_based_tiles(0, 0, 20, 18, title_map, T_TITLE);
    put_attr_rect(0, 0, 20, 18, PAL_TITLE);

    for (i = 0; i < 40; i++) move_sprite(i, 0, 0);   /* park every OAM entry */
    HIDE_SPRITES;

    while (!(joypad() & J_START)) {
        if ((frame & 0x1F) == 0) press_start_visible((frame >> 5) & 1);
        frame++;
        vsync();
    }
    waitpadup();
    press_start_visible(1);
    sfx_star();
    vsync();
}

/* ------------------------------------------------------------------ level */
static void build_collision(void) {
    uint8_t i, tx, ty;
    memset(solid, 0, sizeof(solid));
    for (i = 0; i < BLOCK_COUNT; i++) {
        uint8_t bx = BLOCK_RECTS[i][0], by = BLOCK_RECTS[i][1];
        uint8_t bw = BLOCK_RECTS[i][2], bh = BLOCK_RECTS[i][3];
        for (ty = by; ty < by + bh; ty++)
            for (tx = bx; tx < bx + bw; tx++) solid[ty][tx] = 1;
    }
}

/* Can the 8x8 hero box sit with its top-left corner at (x, y)? */
static uint8_t is_free(uint8_t x, uint8_t y) {
    uint8_t x0 = x >> 3, x1 = (x + 7) >> 3;
    uint8_t y0 = y >> 3, y1 = (y + 7) >> 3;
    uint8_t tx, ty;
    if (x > (LEVEL_W * 8 - 8) || y > (LEVEL_H * 8 - 8)) return 0;
    for (ty = y0; ty <= y1; ty++)
        for (tx = x0; tx <= x1; tx++)
            if (solid[ty][tx]) return 0;
    return 1;
}

static uint8_t spot_taken(uint8_t s, uint8_t upto) {
    uint8_t i;
    for (i = 0; i < upto; i++) if (star_spot[i] == s) return 1;
    return 0;
}

static uint8_t pick_spot(uint8_t live) {
    uint8_t tries = 0, s;
    do {
        s = next_spot;
        next_spot = (next_spot + 1) % STAR_SPOT_COUNT;
        tries++;
    } while (spot_taken(s, live) && tries < STAR_SPOT_COUNT);
    return s;
}

static void place_star_sprite(uint8_t i) {
    uint8_t s = star_spot[i];
    move_sprite(1 + i, STAR_SPOTS[s][0] * 8 + 8, STAR_SPOTS[s][1] * 8 + 16 + 16);
}

static void respawn_stars(void) {
    uint8_t i;
    for (i = 0; i < STAR_TOTAL; i++) {
        star_spot[i] = pick_spot(i);
        set_sprite_tile(1 + i, T_COIN);
        set_sprite_prop(1 + i, S_PALETTE | SPAL_COIN);
        place_star_sprite(i);
    }
    remaining = STAR_TOTAL;
}

static void show_banner(uint8_t on) {
    uint8_t row = BANNER_Y - LEVEL_SCREEN_Y;
    if (on) {
        set_bkg_based_tiles(BANNER_X, BANNER_Y, BANNER_W, BANNER_H, banner_map, T_BANNER);
        put_attr_rect(BANNER_X, BANNER_Y, BANNER_W, BANNER_H, PAL_BANNER);
    } else {
        set_bkg_based_submap(BANNER_X, BANNER_Y, BANNER_W, BANNER_H,
                             level_map + (row * LEVEL_W + BANNER_X), LEVEL_W, T_LEVEL);
        put_attr_rect(BANNER_X, BANNER_Y, BANNER_W, BANNER_H, PAL_LEVEL);
    }
}

static void play_init(void) {
    build_collision();

    set_bkg_data(T_HUD, HUD_TILE_COUNT, hud_tiles);
    set_bkg_data(T_LEVEL, LEVEL_TILE_COUNT, level_tiles);
    set_bkg_data(T_DIGIT, DIGITS_TILE_COUNT, digits_tiles);
    set_bkg_data(T_BANNER, BANNER_TILE_COUNT, banner_tiles);
    set_bkg_data(T_BLANK, BLANK_TILE_COUNT, blank_tiles);

    set_bkg_based_tiles(0, 0, 20, 2, hud_map, T_HUD);
    set_bkg_based_tiles(0, LEVEL_SCREEN_Y, LEVEL_W, LEVEL_H, level_map, T_LEVEL);

    put_attr_rect(0, 0, 20, 2, PAL_HUD);
    put_attr_rect(0, LEVEL_SCREEN_Y, LEVEL_W, LEVEL_H, PAL_LEVEL);
    put_attr_rect(5, 0, 2, 1, PAL_DIGIT);
    put_attr_rect(17, 0, 1, 1, PAL_DIGIT);

    score = 0;
    next_spot = 0;
    px = PLAYER_START_X * 8;
    py = PLAYER_START_Y * 8;
    respawn_stars();
    draw_score();

    set_sprite_data(T_SPR, PLAYER_TILE_COUNT, player_tiles);
    set_sprite_data(T_COIN, COIN_TILE_COUNT, coin_tiles);
    set_sprite_tile(0, T_SPR);
    set_sprite_prop(0, SPAL_HERO);
    move_sprite(0, px + 8, py + 16);
    SHOW_SPRITES;
}

static void collect_at(uint8_t i) {
    uint8_t s = star_spot[i];
    uint8_t sx = STAR_SPOTS[s][0] * 8, sy = STAR_SPOTS[s][1] * 8;
    /* forgiving 6px overlap, not a strict pixel test */
    if (px + 6 > sx && sx + 6 > px && py + 6 > sy && sy + 6 > py) {
        sfx_star();
        score++;
        star_spot[i] = pick_spot(STAR_TOTAL);   /* move it somewhere else */
        place_star_sprite(i);
    }
}

static void play_loop(void) {
    uint8_t joy;
    uint16_t anim = 0;
    uint8_t i;

    while (1) {
        vsync();
        joy = joypad();
        frame++;

        if (joy & J_LEFT)  if (is_free(px - MOVE_SPEED, py)) px -= MOVE_SPEED;
        if (joy & J_RIGHT) if (is_free(px + MOVE_SPEED, py)) px += MOVE_SPEED;
        if (joy & J_UP)    if (is_free(px, py - MOVE_SPEED)) py -= MOVE_SPEED;
        if (joy & J_DOWN)  if (is_free(px, py + MOVE_SPEED)) py += MOVE_SPEED;
        move_sprite(0, px + 8, py + 16);

        /* 2-frame coin spin */
        if (++anim >= 8) {
            anim = 0;
            for (i = 0; i < STAR_TOTAL; i++)
                set_sprite_tile(1 + i, T_COIN + ((frame >> 3) & 1));
        }

        if (joy & J_SELECT) return;             /* back to the title screen */
        remaining = STAR_TOTAL - score;
        for (i = 0; i < STAR_TOTAL; i++) collect_at(i);
        draw_score();

        if (score >= STAR_TOTAL) {
            sfx_clear();
            remaining = 0;
            draw_digit(17, 0, 0);
            HIDE_SPRITES;
            show_banner(1);
            for (i = 0; i < 150; i++) vsync();
            show_banner(0);
            score = 0;
            respawn_stars();
            draw_score();
            SHOW_SPRITES;
        }
    }
}

/* ------------------------------------------------------------------ main */
void main(void) {
    DISPLAY_OFF;
    SPRITES_8x8;
    DISPLAY_ON;
    SHOW_BKG;

    if (DEVICE_SUPPORTS_COLOR) {
        set_bkg_palette(PAL_TITLE, 1, title_palette);
        set_bkg_palette(PAL_LEVEL, 1, level_palette);
        set_bkg_palette(PAL_DIGIT, 1, digits_palette);
        set_bkg_palette(PAL_HUD, 1, hud_palette);
        set_bkg_palette(PAL_BANNER, 1, banner_palette);
        set_sprite_palette(SPAL_HERO, 1, player_palette);
        set_sprite_palette(SPAL_COIN, 1, coin_palette);
    }
    sfx_init();

    while (1) {
        screen_title();
        play_init();
        play_loop();
    }
}
