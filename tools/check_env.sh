#!/usr/bin/env bash
# check_env.sh — is this machine ready to build and playtest a GBC ROM?
#
#   ./tools/check_env.sh            # report
#   ./tools/check_env.sh --strict   # exit 1 if anything needed for a build is missing
#
# What matters:
#   lcc + GBDKDIR   -> GBDK-2020 (SDCC under the hood). This is the compiler that
#                      turns C into a .gbc ROM.
#   python3         -> runs tools/png2gbc.py, tools/playtest.py, tools/artfont.py
#   pillow, numpy   -> image work for png2gbc.py and playtest.py
#   pyboy           -> headless Game Boy emulator used by playtest.py
#   make            -> optional; build.sh works without it
set -u

strict=0
[ "${1:-}" = "--strict" ] && strict=1
fail=0
ok="\033[32m ok \033[0m"
bad="\033[31mFAIL\033[0m"
warn="\033[33mwarn\033[0m"

say() { printf "  [%b] %-22s %s\n" "$1" "$2" "${3:-}"; }

echo "GBDK-2020 (compiler)"
if [ -n "${GBDKDIR:-}" ] && [ -x "${GBDKDIR%/}/bin/lcc" ]; then
  say "$ok" "lcc" "${GBDKDIR%/}/bin/lcc"
elif command -v lcc >/dev/null 2>&1; then
  say "$ok" "lcc" "$(command -v lcc) (found on PATH; set GBDKDIR to its folder)"
else
  found=""
  for d in /opt/gbdk "$HOME/gbdk" "$HOME/opt/gbdk" /usr/local/gbdk /workspace/.tmp/gbdk ../gbdk; do
    if [ -x "$d/bin/lcc" ]; then found="$d"; break; fi
  done
  if [ -n "$found" ]; then
    say "$warn" "lcc" "found at $found — export GBDKDIR=$found"
  else
    say "$bad" "lcc" "install GBDK-2020 4.5.0: https://github.com/gbdk-2020/gbdk-2020/releases"
    fail=1
  fi
fi

echo "Python toolchain"
if command -v python3 >/dev/null 2>&1; then
  say "$ok" "python3" "$(python3 -V 2>&1)"
  py=python3
elif command -v python >/dev/null 2>&1; then
  say "$ok" "python" "$(python -V 2>&1)"
  py=python
else
  say "$bad" "python3" "needed by tools/*.py"
  py=""
  fail=1
fi

if [ -n "$py" ]; then
  for mod in PIL numpy pyboy; do
    if "$py" -c "import $mod" >/dev/null 2>&1; then
      say "$ok" "$mod" "$("$py" -c "import importlib.metadata as m;
name={'PIL':'pillow','numpy':'numpy','pyboy':'pyboy'}['$mod']
try: print(m.version(name))
except Exception: print('installed')" 2>/dev/null)"
    else
      if [ "$mod" = "pyboy" ]; then
        say "$warn" "$mod" "missing — only playtest.py needs it: python3 -m pip install pyboy"
      else
        say "$bad" "$mod" "missing — python3 -m pip install pillow numpy"
        fail=1
      fi
    fi
  done
fi

echo "Optional"
if command -v make >/dev/null 2>&1; then
  say "$ok" "make" "$(make --version 2>&1 | head -1)"
else
  say "$warn" "make" "not installed — use ./build.sh (it calls lcc directly)"
fi
if command -v git >/dev/null 2>&1; then say "$ok" "git" "$(git --version)"; else say "$warn" "git" "not installed"; fi

echo
if [ "$fail" -eq 0 ]; then
  echo "Ready. Try: ./templates/minimal-gbc/build.sh && python3 tools/playtest.py --rom build/tile-hop.gbc --script 'wait:60,press:start:4,wait:30,snap:play'"
  exit 0
fi
echo "Some required pieces are missing (see FAIL above)."
[ "$strict" -eq 1 ] && exit 1
exit 0
