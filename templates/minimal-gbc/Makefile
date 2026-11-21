# tiny Makefile for the starter game — build.sh does the same thing without make.
#
#   make            build build/tile-hop.gbc
#   make assets     redraw + re-convert the art, then build
#   make playtest   build, then run the scripted PyBoy playtest
#   make clean      remove build/
#
# GBDKDIR must end with a slash for lcc (it appends "bin/sdcc"), so we normalise it.

GBDKDIR ?= $(firstword $(wildcard /opt/gbdk/ $(HOME)/gbdk/ /usr/local/gbdk/ \
                        $(CURDIR)/../../.tmp/gbdk/ $(CURDIR)/../../../.tmp/gbdk/))
GBDKDIR := $(patsubst %/,%,$(GBDKDIR))/
export GBDKDIR
LCC      := $(GBDKDIR)bin/lcc

TARGET   := build/tile-hop.gbc
SRC      := src/main.c $(wildcard src/gen/*.c)
HDR      := $(wildcard src/gen/*.h)
CFLAGS   := -Wm-yc -Wm-yt0x1B -Wm-yn"TILEHOP"

.PHONY: all assets playtest clean check

all: $(TARGET)

$(TARGET): $(SRC) $(HDR) | build
	@test -x $(LCC) || { echo "GBDK not found at $(GBDKDIR) — set GBDKDIR=/path/to/gbdk/ or run ./build.sh"; exit 1; }
	$(LCC) $(CFLAGS) -o $@ $(SRC)
	@echo "built $@"

build:
	@mkdir -p build

assets:
	python3 assets/make_art.py
	@$(MAKE) $(TARGET)

playtest: $(TARGET)
	python3 ../../tools/playtest.py --rom $(TARGET) \
		--script "wait:8,snap:title,press:start:4,wait:16,snap:play,hold:right:36,release:right,wait:4,snap:score" \
		--out build/playtest-strip.png

check:
	../../tools/check_env.sh --strict

clean:
	rm -rf build
