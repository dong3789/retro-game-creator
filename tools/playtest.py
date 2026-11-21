#!/usr/bin/env python3
"""
playtest.py — headless playtest for GBC ROMs (PyBoy) without a screen.

Feeds a scripted sequence of button presses into the emulator, grabs frames, and
writes one comparison strip image so a human — or an AI agent — can look at what
actually appeared on the 160x144 LCD.

    python3 tools/playtest.py --rom build/tile-hop.gbc \
        --script "wait:60,snap:title,press:START:5,wait:20,hold:RIGHT:30,snap:moved" \
        --out build/playtest_strip.png

Every run also captures "boot" (first frame after the ROM settles) and "final", and
warns when frames are blank, identical, or nearly colourless — the three ways a ROM
"runs" while showing nothing. --strict turns those warnings into a failure.
    wait:N            advance N frames with no new input
    press:BTN:N       press BTN, hold N frames, release
    hold:BTN:N        press BTN, hold N frames, leave it pressed
    release:BTN       release a held button
    snap[:LABEL]      capture the current frame (LABEL is cosmetic)

BTN: up down left right a b start select

Every run also captures "boot" (first frame after the ROM settles) and "final".
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("playtest.py needs pillow.\n  python3 -m pip install pillow numpy pyboy")

BTNS = {
    "up": "ARROW_UP",
    "down": "ARROW_DOWN",
    "left": "ARROW_LEFT",
    "right": "ARROW_RIGHT",
    "a": "BUTTON_A",
    "b": "BUTTON_B",
    "start": "BUTTON_START",
    "select": "BUTTON_SELECT",
}


def die(msg: str, code: int = 2):
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def load_pyboy():
    try:
        from pyboy import PyBoy
        from pyboy.utils import WindowEvent
    except ImportError as exc:
        die(
            "pyboy is not installed.\n"
            "  python3 -m pip install pyboy\n"
            "  (R36S owner? this tool only runs on your computer, the ROM itself runs on the handheld.)\n"
            f"  [{exc}]"
        )
    return PyBoy, WindowEvent


def parse_script(script: str):
    steps = []
    if not script:
        return steps
    for raw in script.split(","):
        token = raw.strip()
        if not token:
            continue
        parts = [p.strip() for p in token.split(":")]
        cmd = parts[0].lower()
        if cmd in ("wait", "sleep"):
            if len(parts) != 2 or not parts[1].isdigit():
                die(f"script error: '{token}' -> use wait:N")
            steps.append(("wait", None, int(parts[1])))
        elif cmd in ("press", "hold"):
            if len(parts) < 2 or parts[1].lower() not in BTNS:
                die(f"script error: '{token}' -> use {cmd}:BTN:N ({'/'.join(BTNS)})")
            frames = int(parts[2]) if len(parts) > 2 and parts[2] else 2
            steps.append((cmd, parts[1].lower(), frames))
        elif cmd == "release":
            if len(parts) != 2 or parts[1].lower() not in BTNS:
                die(f"script error: '{token}' -> use release:BTN")
            steps.append(("release", parts[1].lower(), 0))
        elif cmd == "snap":
            label = parts[1] if len(parts) > 1 and parts[1] else None
            steps.append(("snap", label, 0))
        else:
            die(f"script error: unknown command '{cmd}' in '{token}'")
    return steps


class Runner:
    def __init__(self, rom, boot_frames=90, speed=0, sound=False, verbose=True):
        PyBoy, WindowEvent = load_pyboy()
        self.WindowEvent = WindowEvent
        self.pb = PyBoy(rom, window="null", sound=sound)
        if speed is not None:
            self.pb.set_emulation_speed(speed)
        self.shots = []
        self.verbose = verbose
        self.boot_frames = boot_frames
        self._boot()

    # -- emulator plumbing ------------------------------------------------
    def _boot(self):
        for _ in range(self.boot_frames):
            self.pb.tick(1, True, False)
        self.capture("boot")

    def tick(self, frames):
        for _ in range(max(0, frames)):
            self.pb.tick(1, True, False)

    def _send(self, btn, down):
        name = getattr(self.WindowEvent, ("PRESS_" if down else "RELEASE_") + BTNS[btn])
        self.pb.send_input(name)

    def capture(self, label):
        img = self.pb.screen.image.convert("RGB")
        frame = int(self.pb.frame_count)
        digest = hashlib.md5(img.tobytes()).hexdigest()[:8]
        colors = len(img.getcolors(4096) or [])
        self.shots.append(
            {"label": label or f"snap{len(self.shots)}", "frame": frame, "image": img,
             "hash": digest, "colors": colors}
        )
        if self.verbose:
            print(f"  snap [{label or '-':<12}] frame={frame:<6} colors={colors:<3} md5={digest}")
        return img

    # -- script execution -------------------------------------------------
    def run(self, steps):
        for kind, arg, frames in steps:
            if kind == "wait":
                self.tick(frames)
            elif kind == "press":
                self._send(arg, True)
                self.tick(frames)
                self._send(arg, False)
                self.tick(1)
            elif kind == "hold":
                self._send(arg, True)
                self.tick(frames)
            elif kind == "release":
                self._send(arg, False)
                self.tick(1)
            elif kind == "snap":
                self.capture(arg)
        # a frame after the last input, so the strip always ends on the live screen
        self.capture("final")

    def close(self):
        try:
            self.pb.stop()
        except Exception:
            pass


# ---------------------------------------------------------------- strip image


def _font(size=12):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def build_strip(shots, out_path, scale=2, cols=4):
    if not shots:
        return None
    pad, label_h = 8, 22
    cw, ch = 160 * scale, 144 * scale
    rows = (len(shots) + cols - 1) // cols
    W = cols * (cw + pad) + pad
    H = rows * (ch + label_h + pad) + pad
    canvas = Image.new("RGB", (W, H), (26, 26, 30))
    d = ImageDraw.Draw(canvas)
    f = _font(13)
    fs = _font(11)
    for i, shot in enumerate(shots):
        r, c = divmod(i, cols)
        x = pad + c * (cw + pad)
        y = pad + r * (ch + label_h + pad)
        d.rectangle([x, y, x + cw - 1, y + label_h - 1], fill=(40, 40, 48))
        d.text((x + 4, y + 4), f"{i}: {shot['label']}", fill=(235, 235, 235), font=f)
        d.text((x + cw - 96, y + 5), f"f{shot['frame']} {shot['colors']}c",
               fill=(150, 200, 150), font=fs)
        img = shot["image"].resize((cw, ch), Image.NEAREST)
        canvas.paste(img, (x, y + label_h))
        d.rectangle([x, y + label_h, x + cw - 1, y + label_h + ch - 1], outline=(70, 70, 80))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    canvas.save(out_path)
    return out_path


# ---------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(description="Headless PyBoy playtest with screenshot strips.")
    ap.add_argument("--rom", required=True, help=".gb / .gbc ROM to boot")
    ap.add_argument("--script", default="", help='e.g. "wait:60,press:START:5,snap:play"')
    ap.add_argument("--out", default="playtest_strip.png", help="strip image path")
    ap.add_argument("--frames-dir", help="also save every snapshot as its own PNG here")
    ap.add_argument("--boot", type=int, default=90, help="frames to run before the first snap (default 90)")
    ap.add_argument("--scale", type=int, default=2, help="strip zoom (default 2)")
    ap.add_argument("--cols", type=int, default=4, help="strip columns (default 4)")
    ap.add_argument("--real-time", action="store_true", help="run at 1x speed instead of as fast as possible")
    ap.add_argument("--json", action="store_true", help="print a machine-readable summary")
    ap.add_argument("--strict", action="store_true",
                    help="exit 3 when a sanity warning fires (CI use)")
    args = ap.parse_args(argv)

    if not os.path.isfile(args.rom):
        die(f"error: no such ROM: {args.rom}\n  build it first: make -C templates/minimal-gbc")

    steps = parse_script(args.script)
    runner = Runner(args.rom, boot_frames=args.boot,
                    speed=None if args.real_time else 0)
    print(f"booting {args.rom} ...")
    try:
        runner.run(steps)
    finally:
        runner.close()

    shots = runner.shots
    strip = build_strip(shots, args.out, scale=args.scale, cols=args.cols)

    if args.frames_dir:
        os.makedirs(args.frames_dir, exist_ok=True)
        for i, shot in enumerate(shots):
            safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in shot["label"])
            shot["image"].resize((160 * args.scale, 144 * args.scale), Image.NEAREST).save(
                os.path.join(args.frames_dir, f"{i:02d}_{safe}.png"))

    # ---- sanity analysis: catch the two classic failures early
    warnings = []
    if shots:
        if max(s["colors"] for s in shots) <= 2:
            warnings.append("every frame has <=2 colors: is the display on and the palette set?")
        named = [s for s in shots if s["label"] not in ("boot", "final")]
        uniq = {s["hash"] for s in named}
        if len(named) >= 2 and len(uniq) == 1:
            warnings.append("all captured frames are identical: input may not be reaching the game "
                            "(check the joypad loop / vsync ordering).")
        blank = [s["label"] for s in shots if s["colors"] <= 1]
        if blank:
            warnings.append(f"blank frames: {', '.join(blank)}")

    summary = {
        "rom": os.path.abspath(args.rom),
        "frames": shots[-1]["frame"] if shots else 0,
        "strip": os.path.abspath(strip) if strip else None,
        "snapshots": [{k: s[k] for k in ("label", "frame", "colors", "hash")} for s in shots],
        "warnings": warnings,
    }
    if args.strict and warnings:
        for w in warnings:
            print(f"WARNING: {w}")
        print("\nplaytest FAILED: fix the warnings above before trusting this ROM.")
        return 3
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"\nframes run: {summary['frames']}")
        print(f"strip: {summary['strip']}")
        for w in warnings:
            print(f"WARNING: {w}")
        print("\nopen the strip and check by eye: text legible? palette right? "
              "sprite on screen? collisions sane?")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
