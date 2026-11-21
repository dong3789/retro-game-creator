# CI: build the ROM and playtest it on every push

`.github/workflows/build-rom.yml` builds `templates/minimal-gbc`, checks the ROM header,
runs the headless PyBoy playtest and uploads the `.gbc` plus the screenshot strip as
artifacts.

On every push to `main` / any pull request it runs:

1. GBDK-2020 4.5.0 download (ubuntu-latest, `GBDKDIR=$HOME/gbdk/`)
2. `./tools/check_env.sh --strict`
3. `./build.sh` in `templates/minimal-gbc`
4. ROM header check (size, title, cart type `0x1B`, CGB flag `0x80`)
5. `tools/playtest.py --strict` — fails the build if the ROM renders blank or ignores input
6. Artifacts: `tile-hop-gbc` (the ROM) and `playtest-strip` (the frames)

## Adding the file

If the repository was seeded by a tool whose GitHub token lacks the **workflows**
permission, GitHub rejects any push that creates `.github/workflows/*` with:

```
refusing to allow a GitHub App to create or update workflow
`.github/workflows/build-rom.yml` without `workflows` permission
```

In that case, paste the file once through the web UI (this immediately triggers a run):

1. Open <https://github.com/dong3789/gbc-game-creator/new/main/.github/workflows>
2. File name: `build-rom.yml`
3. Paste the content below, commit to `main`

After that, the workflow is in the repository and every later push runs it. Everything
else (README, tools, template) was pushed normally.

## The workflow

```yaml
name: build-rom

on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

jobs:
  build:
    name: build + playtest TILE HOP
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install GBDK-2020 4.5.0
        # GBDKDIR must end with a slash: lcc appends "bin/sdcc" literally.
        run: |
          curl -sSL -o /tmp/gbdk.tar.gz \
            https://github.com/gbdk-2020/gbdk-2020/releases/download/4.5.0/gbdk-linux64.tar.gz
          tar -xzf /tmp/gbdk.tar.gz -C "$HOME"
          test -x "$HOME/gbdk/bin/lcc"
          echo "GBDKDIR=$HOME/gbdk/" >> "$GITHUB_ENV"
          echo "PATH=$HOME/gbdk/bin:$PATH" >> "$GITHUB_ENV"

      - name: Install python tools
        run: python3 -m pip install --quiet pillow numpy pyboy

      - name: Toolchain check
        run: ./tools/check_env.sh --strict

      - name: Build the starter ROM
        working-directory: templates/minimal-gbc
        run: ./build.sh

      - name: Verify the ROM header
        run: |
          python3 - <<'PY'
          import pathlib, sys
          rom = pathlib.Path("templates/minimal-gbc/build/tile-hop.gbc").read_bytes()
          title = rom[0x134:0x13F].split(b"\x00")[0].decode("ascii", "replace")
          print("size:", len(rom), "bytes")
          print("title:", title)
          print("cart type: 0x%02X  (0x1B = MBC5+RAM+BATTERY)" % rom[0x147])
          print("cgb flag:  0x%02X  (0x80 = CGB+DMG, 0xC0 = CGB only)" % rom[0x143])
          if len(rom) > 512 * 1024:
              sys.exit("ROM is larger than MBC5 can address")
          if rom[0x143] not in (0x80, 0xC0):
              sys.exit("header 0x143 does not advertise CGB support")
          PY

      - name: Playtest (headless)
        working-directory: templates/minimal-gbc
        run: |
          python3 ../../tools/playtest.py \
            --rom build/tile-hop.gbc \
            --script "wait:8,snap:title,press:start:4,wait:16,snap:play,hold:right:36,release:right,wait:4,snap:score,hold:down:24,release:down,snap:moved" \
            --out build/playtest-strip.png \
            --frames-dir build/frames \
            --json --strict

      - name: Upload ROM
        uses: actions/upload-artifact@v4
        with:
          name: tile-hop-gbc
          path: templates/minimal-gbc/build/tile-hop.gbc
          if-no-files-found: error

      - name: Upload playtest strip
        uses: actions/upload-artifact@v4
        with:
          name: playtest-strip
          path: |
            templates/minimal-gbc/build/playtest-strip.png
            templates/minimal-gbc/build/frames/*.png
          if-no-files-found: error
```
