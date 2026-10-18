# THPS3 recomp host (N64: USA)

The native macOS (arm64) host for Tony Hawk's Pro Skater 3 for N64, made with
[N64Recomp](https://github.com/N64Recomp/N64Recomp) and run on N64ModernRuntime + RT64 (Metal). It shares its host with THPS1 and THPS2 (`decomp/common/host`); the
explanations of frame pacing, audio pacing, the edge fix and the high-frame-rate code are the same as THPS1's and are in
[docs/internals/recomp.md](../../../docs/internals/recomp.md). This is the developer README. Users want the top-level
[README](../../../README.md) and [docs/MANUAL.md](../../../docs/MANUAL.md).

> **No ROM data is in this directory.** The recompiled C, the code blob, dumps, reference frames and build output are all
> generated locally from your own dump and are git-ignored (`build/`, `*.png`, `*.bin`). `versions/us/overlay_table.inc` and `recipes/us/` hold offsets,
> names and hashes only.

What has been verified: [docs/VERIFICATION.md](../../../docs/VERIFICATION.md). The front-end screens:
[docs/internals/overlays.md](../../../docs/internals/overlays.md).

## Layout

The host (sources, CMake file, Python tools, test harness, RT64 patches) is shared by THPS1-3 and lives in `../../common/host/` (ADR 0006); this
directory is the game's profile. `tools/` and `tests/` here hold small wrappers with the shared tools' names, so the commands below run from this
directory. Where this README says `src/x.cpp`, it is `../../common/host/src/x.cpp`.

```
CMakeLists.txt            9 lines: project(), THPS_FAMILY, THPS_SKIP_INTRO overlay, include(../../common/host/cmake/thps_host.cmake)
game/game.toml            the game profile: names, config folder, wording, flags (-> thps::game in build/gen/thps_versions.h)
game/game_hooks.def       the hook functions only this game's N64Recomp config calls
config/thps3.hooks.toml   N64Recomp [[patches.hook]] blocks (loader, PI, events, widescreen, skip intro), by function name
config/thps3.aspMain.toml RSPRecomp config template for the audio microcode
versions/                 classes.toml, host_syms.toml (the names the host needs), us/{host_force,data_syms}.toml and overlay_table.inc
recipes/<class>/          committed ROM-free first-run inputs: `thps3.host.syms.toml`, `blob.txt`, `overlays.txt` (the 16 front-end screens' layout and function map)
tools/gen.py              wrapper -> ../../common/host/tools/gen.py: per class syms -> overlays -> N64Recomp -> namespace; RSPRecomp (build/gen/, local)
tools/gen_versions.py     validates the version tables; writes build/gen/thps_versions.h, per-class N64Recomp configs
tools/build_host.py, test.sh, package_split.py, scan_bundle.py, setup_runtime.py ...   wrappers of the shared tools
tests/scenarios.py        this game's checkpoints and input scripts (the shared runner and harness are in ../../common/host/tests/)
../../common/host/src/    main, hooks, input, audio, pak, widescreen, interpolation, rom_check, versions, the first-run flow, the split build, the menu ...
../../common/host/patches/   our RT64 patches (applied by tools/setup_runtime.py)
../../common/overlay_recomp.py   front-end overlays as relocatable sections (static build); ../../common/firstrun/ the same from the user's ROM (first run)
```

## Build

The one-command route (macOS, Windows, Linux):

```sh
python3 -I tools/build_host.py --rom /path/to/thps3-usa.z64
```

It fetches the pinned N64ModernRuntime and RT64 and applies our patches (`tools/setup_runtime.py`), builds N64Recomp and RSPRecomp at the
pinned commit, makes a Python venv with `rabbitizer`, inflates the ROM's code and generates the C, then configures and builds the host
with CMake and Ninja. `--stub` builds with ROM-free stand-in functions to check the toolchain.

By hand, once the runtime tree is in `<runtime-dir>`:

```sh
cd decomp/thps3
make setup && make extract ROM_SRC=/path/to/thps3-usa.z64 && make recomp-inputs
cd recomp-host
python3 -I tools/gen.py /path/to/N64Recomp      # 3,937 functions (3,394 + 543 in the 16 overlays), 0 warnings
cmake -S . -B build/cmake -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DRECOMP_RUNTIME_DIR=<runtime-dir>
cmake --build build/cmake
```

Prerequisites on macOS: Xcode (or the Command Line Tools) with the Metal toolchain, Homebrew `cmake ninja sdl2 pkgconf`.

## Split build: no game code in the app

`-DTHPS_SPLIT_GAME_LIB=ON` builds the engine without any recompiled game code. On first run the app translates the user's ROM with the bundled
N64Recomp and RSPRecomp, compiles the C with the system compiler and loads `<config>/game/thps3_game_<class>.<dylib|so|dll>`. This is how releases
are built. `recipes/us` serves the USA dump, the only one we have. The front-end screens are read from the user's ROM with the recipe's layout
([docs/internals/overlays.md](../../../docs/internals/overlays.md#at-first-run-the-split-build)). The design, shared with THPS1, is in the THPS1
repository's `docs/internals/recomp.md`. Files: `src/game_split.cpp`, `src/firstrun.cpp`, `../../common/firstrun/overlay_rom.cpp`, `game-lib/`,
`tools/package_split.py` (assembles the `.app`; one zip per game with all its recipes), `tools/scan_bundle.py` (the ROM-byte scan).
`tests/firstrun_test.py` builds from a dump on a clean config folder and then plays.

## In-game settings menu

Esc (controller: Back) opens an RmlUi menu over the game (General, Controls, Graphics, Sound) that edits `general.cfg`, `graphics.cfg` and
`controls.cfg`. The code is shared by all three games;
its libraries and fonts are fetched by `tools/setup_runtime.py` at pinned hashes, never stored. `-DTHPS_MENU=OFF` builds without it.

## Run

```sh
build/cmake/thps3_recomp --rom /path/to/thps3-usa.z64
```

The ROM is checked (XXH3-64 `0x4A295D7A2D8E9C55` of the 16 MiB big-endian ROM, SHA-1 `7b9438120c67214afaea09f4b106c54ef8f366c5` as
`.z64`; `.n64` and `.v64` are accepted) and a copy is kept in the config folder (`~/Library/Application Support/THPS3-64Recomp`, or
the folder holding a `portable.txt`; `--config DIR` overrides), so later runs need no `--rom`. Controller Pak saves go to
`<config>/saves/thps3_pak1.mpk` (a standard 32 KiB `.mpk`). Flags: `--mute --wav --no-pads --windowed/--fullscreen --aspect --window
--res-scale --msaa --refresh --skip-intro --show-fps --volume --controls-preset --verbose --control --hidden`, the dump flags, and
`--unlock-levels` (a test aid); see the header of `src/main.cpp`. Graphics defaults: 16:9, a 1280x720 window, auto resolution
scale, 4x MSAA, interpolation to the display rate. The settings tables are in [docs/MANUAL.md](../../../docs/MANUAL.md).

### Controls

THPS3's pad layer (PlayStation-style, `0x800EF794`) takes N64 buttons like this:

| N64 button | pad record | THPS3 action |
|---|---|---|
| C-down / C-left / C-right / C-up | 3 / 1 / 2 / 0 | ollie / flip / grab / grind |
| **A** | 3 | ollie too (and menu accept) |
| **B** | 1 | flip too (and menu back) |
| L | 4 + 5 | spin left + nollie |
| R | 6 + 7 | spin right + switch, **and revert** |
| START | 14 | pause |

Manuals need no button: tap the stick or D-pad up then down (nose manual: down then up). OPTIONS > CONTROLLER ONE only swaps which of
L and R does "spin right and switch" and "spin left and nollie", and sets AUTOKICK and RUMBLE. The default `thps-xbox` preset
puts south = ollie, west = flip, east = grab, north = grind, LB = L, RB or RT = R (revert). The host drops the B that the east button
sends while the skater is under control, because the game reads N64 B as flip, and drops C-right instead on every other screen: east is back in every menu (the pause menu resumes).
`--controls-preset n64` is the plain N64 layout. Bindings are in `<config>/controls.cfg`.

### Skip Intro, Show FPS, crash log

`--skip-intro` (or `skip_intro = 1` in `general.cfg`) presses B on the "EXPANSION PAK FOUND." box and skips the legal text (a hook on the
intro overlay), so the logos appear after about half a second. Do not press START on the logo screen: it keeps the screen up
longer; the logos end in the attract demo, and START in the demo opens the main menu. `--show-fps` puts the counter in the window
title. A crash writes `<config>/crash.log` with the recompiled game function names.

### Graphics

`--aspect original|16:9|21:9|expand`, `--window WxH`, `--res-scale N` (0 = auto), `--msaa 0|2|4` (Apple GPUs have no 8x), `--refresh
original|display|N` (60 Hz interpolation; the game stays at 30 fps), `--windowed`/`--fullscreen`; saved to `<config>/graphics.cfg`.
Widescreen widens the culling and RT64 widens the projection; menus and loading screens stay 4:3 and centred, and the in-level HUD is moved to the screen edges by default (`--hud original|16:9|expand`, `graphics.cfg` `hud=`). The suite
checks that 21:9 shows the same native frame as 4:3.

## Tests

```sh
tools/test.sh --record   # first time on a machine: capture reference frames (ROM-derived, build/tests/refs)
tools/test.sh            # controls.cfg test + the whole suite
tools/test.sh --only pak_save --session pak   # one scenario (+ the ones before it in its session)
tools/test.sh --check-refs
```

One `thps3_recomp` at a time (`--no-pads --mute`, `uptime` in every log). The scenarios are the ones of THPS2's suite, with THPS3's constants
(pad layer `0x800EF794`, skater pointer `0x800EF3AC`, pad pointer `+0x1780`, air flag `+0x1B94`) in `tests/scenarios.py`, plus the six scenarios of
the in-game settings menu (`menu` and `menu-reload` sessions, skipped when `--features` says `menu=0`); the first career level is the Foundry.
The `level_grab` air check only warns here.

Full run on the static build, 2026-10-12: 31 pass, 1 warn (the `level_grab` air flag), 0 fail, 4 skipped (launcher-only scenarios). The split-built
library passed the full suite (25 pass, 1 warn, 4 skipped) before the menu scenarios were added, and `tests/firstrun_test.py` passes.

## Windows and Linux (ported, not yet run on either)

The same host code and platform seams as THPS1 and THPS2, the same flags (`--api`, Alt+Enter) and the same tools:
`tools/build_host.py`, `tools/build_windows.ps1`, `tools/setup_runtime.py`, and `-DTHPS_STUB_FUNCS=ON` with `tools/gen_stub.py`.
`tools/mingw_check.py` cross-compiles the whole host, menu included, with MinGW, and the manual CI (`.github/workflows/ci.yml`) builds the stub
host on Linux, Windows and macOS; both pass. No real Windows run has been done yet. Test kit: [docs/WINDOWS-TEST.md](docs/WINDOWS-TEST.md).
Config folder: `%LOCALAPPDATA%\THPS3-64Recomp`.

## Not done

- No in-game pak swapping; the in-game pak manager is not exercised by the tests; Rumble Pak output is untested on a real pad.
- Widescreen: menus and loading screens are 4:3 and centred; the in-level HUD is anchored to the screen edges by default (`--hud expand`; `--hud original` keeps it centred).
- Two intermittent crashes were seen once each in about 60 launches (see [docs/KNOWN-ISSUES.md](../../../docs/KNOWN-ISSUES.md)).
- Texture packs: not attempted. The settings menu has no rebinding of single keys or buttons yet (edit `controls.cfg`).
