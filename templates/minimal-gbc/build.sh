#!/usr/bin/env bash
# build.sh — compile the starter ROM without needing make.
#
#   ./build.sh              build -> build/tile-hop.gbc
#   ./build.sh --assets     redraw + re-convert the art first (needs pillow/numpy)
#   ./build.sh --playtest   build, then run the scripted playtest and open a strip
#   ./build.sh --clean      remove build output
#
# GBDK is found via $GBDKDIR first, then a few usual places. Get it from
# https://github.com/gbdk-2020/gbdk-2020/releases (4.5.0 is what this was tested on).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"
OUT="build/tile-hop.gbc"
TITLE="TILEHOP"

do_assets=0
do_play=0
for arg in "$@"; do
  case "$arg" in
    --assets)   do_assets=1 ;;
    --playtest) do_play=1 ;;
    --clean)    rm -rf build; echo "cleaned"; exit 0 ;;
    -h|--help)  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $arg (try --help)" >&2; exit 2 ;;
  esac
done

# lcc expects GBDKDIR to end with a slash (it appends "bin/sdcc" literally).
find_gbdk() {
  if [ -n "${GBDKDIR:-}" ] && [ -x "${GBDKDIR%/}/bin/lcc" ]; then
    echo "$(cd "${GBDKDIR%/}" && pwd -P)/"; return
  fi
  for d in /opt/gbdk "$HOME/gbdk" "$HOME/opt/gbdk" /usr/local/gbdk \
           "$HERE/../../.tmp/gbdk" "$HERE/../../../.tmp/gbdk" \
           "$HERE/../../../../.tmp/gbdk" "$HERE/../../.tmp-demo/gbdk"; do
    if [ -x "$d/bin/lcc" ]; then echo "$(cd "$d" && pwd -P)/"; return; fi
  done
  if command -v lcc >/dev/null 2>&1; then
    d="$(dirname "$(dirname "$(command -v lcc)")")"; echo "$(cd "$d" && pwd -P)/"; return
  fi
  echo ""
}

GBDKDIR="$(find_gbdk)"
if [ -z "$GBDKDIR" ]; then
  cat >&2 <<'EOF'
error: GBDK-2020 not found.

  Download gbdk-linux64.tar.gz (or the macOS build) from
  https://github.com/gbdk-2020/gbdk-2020/releases
  unpack it, then either

    export GBDKDIR=/path/to/gbdk
    ./build.sh

  or drop the folder at /opt/gbdk (Homebrew: brew install gbdk).
EOF
  exit 1
fi
export GBDKDIR
LCC="$GBDKDIR/bin/lcc"
echo "GBDKDIR = $GBDKDIR"

if [ "$do_assets" = "1" ]; then
  echo "== regenerating art =="
  python3 assets/make_art.py
fi

mkdir -p build
echo "== compiling =="
# -Wm-yc     CGB compatible: header 0x80, so the ROM also boots on a DMG
#            (note the case: -Wm-yC is CGB-ONLY, header 0xC0)
# -Wm-yt0x1B MBC5 + RAM + battery (saves work if you add SRAM later)
# -Wm-yn"..." ROM title shown in flash carts / emulators
"$LCC" -Wm-yc -Wm-yt0x1B -Wm-yn"$TITLE" -o "$OUT" src/main.c src/gen/*.c

echo "built $OUT ($(wc -c < "$OUT") bytes)"
if [ -f ../../tools/playtest.py ]; then
  echo "  playtest: python3 ../../tools/playtest.py --rom $OUT --script 'wait:40,press:start:4,snap:play'"
else
  echo "  run it in an emulator (sameboy, mgba, or copy the .gbc to the handheld)"
fi

if [ "$do_play" = "1" ]; then
  echo "== playtest =="
  python3 ../../tools/playtest.py --rom "$OUT" \
    --script "wait:40,snap:title,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:moved" \
    --out build/playtest-strip.png
fi
