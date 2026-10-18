# Verification

What has been checked, how to repeat it, and what has not. Numbers are from the maintainer's machine (Apple M2 Pro, 10 cores,
macOS 26) unless stated. Labels: **[machine]** a script decides pass or fail; **[hand]** a person looked.

## 1. The decompilation rebuilds the retail ROM byte for byte [machine]

`cd decomp/thps3 && make setup && make extract ROM_SRC=your.z64 && make` prints three `OK` lines:

| Target | Result |
|---|---|
| The main code image rebuilt from disassembly with GNU as and ld | identical to the image inflated from the dump (SHA-1 in `decomp/thps3/checksums/build.main.sha1`) |
| The ROM rebuilt from the boot disassembly plus the original compressed chunks | identical (`decomp/thps3/checksums/build.rom.sha1`) |
| The ROM with the main image **recompressed** by the patched packer | identical (`decomp/thps3/checksums/build.rom_recompressed.sha1`) |

The compression format (RNC ProPack under another magic) is reproduced exactly: 1,120 compressed pieces recompress identically (15 further pieces are stored raw and one has a known quirk, with no
mismatch) (`decomp/common/repack_check.py`). An exact recompression is evidence that the decoder, the format description and the
packer settings are right. This check runs on the USA dump.

## 2. N64Recomp translates the whole program without warnings [machine]

`make recomp N64RECOMP=...` on the function list (`decomp/thps3/recomp/thps3.syms.toml`): 3,394 functions, **0 warnings**; the nine
leftover PlayStation coprocessor-2 instructions are turned into no-ops. The 16 front-end screens are translated as relocatable
sections (3,937 functions with them, 0 warnings), see [docs/internals/overlays.md](internals/overlays.md).
`decomp/common/recomp_check.py` confirms every word of the code ranges lies in a listed function or in padding.

## 3. The regression suite plays the real game [machine]

`decomp/thps3/recomp-host/tools/test.sh` starts the host once per session and drives the game by pad input, waiting for
checkpoints (recognised screens) instead of sleeping. The four launcher scenarios need the optional launcher build, which is not part
of this repository, and are skipped. Results on the developer (static) build, macOS, 2026-10-15 (the release candidate's full gate):

| Pass | Fail | Skipped | Notes |
|---|---|---|---|
| 55 | 0 | 4 | the air checks of `level_ollie` / `level_grab` only warn ([KNOWN-ISSUES](KNOWN-ISSUES.md#tests)) |

The first-run tests (`decomp/common/host/tests/firstrun_test.py`: build from a dump, then play) pass with 0 failures. The suite includes the
in-game settings menu (the first-start hint; Esc opens and closes it; it blocks the pad while open; mouse clicks change
options; pad navigation; the settings persist in a new process), the player-2 screens with one or two controllers, and the
cheats.

<!-- table-ok: the regression scenarios by group, described by what they check -->
| Group | What they check |
|---|---|
| Front end | boot to the logos, main menu, a new career to the Foundry (at least 500 triangles per graphics task), level audio level, median fps of at least 28, that the pad buttons press the game's ollie, flip, grab and grind records, an ollie leaves the ground, the border bands do not flicker, pause and resume |
| Widescreen | menus keep the 4:3 frames; in the level the presented frames are filled |
| Controller Pak | an empty pak lists nothing; SAVE DATA writes a note and the `.mpk` changes; a new process lists and loads it |
| Settings | skip intro, fps counter, pad bindings, crash report, bindings persistence, volume zero |
| Settings menu | 6 scenarios: the hint shows once; Esc opens and closes the menu, drawn in the presented frame; it blocks the pad; clicked options reach `general.cfg` and `graphics.cfg`; pad navigation and the layout pick; settings persist across a restart |
| Camera / aspect | 4:3 border and 21:9 side bands |
| High frame rate | input latency; motion smoothness at 60 Hz |
| Course cycle | four courses back to back (pause, END RUN, back to the select screen): each course's song loads only after the old song's channels have stopped reading the shared song buffer (`src/music.cpp`; without it this game crashed after a few courses); the last course has music |

Reference pictures are ROM-derived, so each machine records its own (`test.sh --record`); they are never committed. The suite
records `uptime` with its timings. Only one host runs at a time.
The air checks only warn (see [KNOWN-ISSUES](KNOWN-ISSUES.md#tests)). The 60 Hz pairing, low in earlier builds, is now 97 % or more of the transforms
(`hfr_motion` requires at least 85 %).

**Windows** (2026-10-14, Windows 11 x64, Intel Core i7-8809G, AMD Radeon RX Vega M, D3D12, 3840x2160 at 60 Hz, 150 %, on the head
before the last fixes): the static build passes 39 passed, 1 warn (`level_ollie`, as on
macOS) and 2 failures that were test faults fixed since (`e169_menus`: a settle time; `cam_ref_43`: a reference picture that depended on the
tick the pause landed on); the first-run tests pass (18 checks plus one macOS-only skip); and an install test of
the Windows zip (unzip, first run builds the game in about 15 s, 30 s of play, exit 0, a relaunch builds nothing; 2026-10-13) passes.
**Windows, release candidate** (2026-10-17, the same PC, the release line with the course-cycle fix): the static build passes
**56 passed, 1 warn, 0 failed, 4 skipped** (the warn is
`level_ollie`, which passed its rerun), including `course-cycle`; the first-run tests pass; the zip passes the bundle check
and the full ROM scan; the install test passes.

## 4. Small checks that need no ROM [machine]

- `tools/test.sh --controls-cfg`: the controls file migration and presets.
- CI (`.github/workflows`): the pinned RT64 and our patches apply cleanly; the host, N64ModernRuntime and RT64 build and link on
  macOS, Linux and Windows against **ROM-free stand-in game functions**. CI never sees a ROM and cannot test rendering, audio or input.
  In the public repositories it runs on GitHub's standard runners.
  Locally, `decomp/common/host/tools/mingw_check.py` cross-compiles the whole host (menu included) for Windows with MinGW.
- `erz_selftest`: the host's native decompressor reproduces the decomp's main image for every chunk (needs your dump).

## 5. The release bundle contains no game bytes [machine]

`python3 -I decomp/thps3/recomp-host/tools/scan_bundle.py YOUR.z64 BLOB.bin DIR --sanity` indexes every fourth 32-byte window of the dump
and of the decompressed code image, then looks every byte offset of every file in `DIR` up. Any copy of 35 or more consecutive game
bytes contains an indexed window. A planted 64-byte copy must be found first (the scanner proves it detects).
**The release candidate's zips:**

Built on 2026-10-18 from one frozen commit: macOS by the release workflow on GitHub, Windows on the test PC. In every scan the
planted bytes were found, and the only runs of 64 or more matching bytes were 16-bit counting tables (the same bytes are in
SDL2, LLVM and the fonts). The release's own `SHA256SUMS` lists the published assets, which are scanned again before publishing.

| Zip | Files, size | ROM-window scan (USA) | ROM-free gate | SHA-256 |
|---|---|---|---|---|
| `THPS3-64Recomp-v0.1.0-preview-macOS-universal.zip` | 43 files, 13.1 MB | clean | passed | `ae2c66a999437b10dc8fe6f5ada4968b168f022fb07183d1d54c0e9973497d7e` |
| `THPS3-64Recomp-v0.1.0-preview-Windows-x64.zip` | 5,703 files, 149.0 MB | clean | passed | `86054c77c936af0aa38425a70d80600a3e1c487eab997546f01df2ffe69a9586` |
Earlier builds, for comparison: on the first-run (split) macOS bundle of 43 files, 18.7 MB (arm64, our own SDL2 2.32.10; checked 2026-10-12 against USA, each with all of this game's code images):
**no run of 64 bytes or more is a copy**. Three runs of 64-194 bytes match, and all of them are 16-bit counting tables (the UTF-16 alphabet 0x20 ... 0x7E and similar: three in the engine),
the same bytes that SDL2, LLVM and FreeType carry; a table is not game content, and the scanner lists them as such. A planted 64-byte copy was found each time.
The ROM-free gate (`scan_bundle.py --no-rom`, layered checks: package inventory, allowlist, symbols, size budget) passes on the same bundle: the engine is 12.7 MB (budget 14.25 MB) and defines no game function.
On the **Windows zip** (5,703 files, 527 MB, most of it the bundled compiler; 2026-10-13, the same dumps and code images):
no copy either; the 379 runs of 64 bytes or more are all such counting tables (in the compiler's libraries, SDL2, LLVM and
the fonts). The ROM-free gate passes there too: the engine is 12.9 MB (Windows budget 14.3 MB).
The generated game library is derived, but is not a byte copy, and stays on the user's machine.

The **source tree** is checked by the exporter that makes this repository (`tools/export_public.py`, private side). The primary
control is a reviewed inventory of every file, so a new file is published only after a maintainer has confirmed it is our own
work. On top of that, as supplementary layers: the same window scan against every dump the maintainer has (all three games),
numeric arrays (hex or decimal, bytes or words) and base64 decoded from text, long game strings, and a documentation linter (no code fence over four instruction-like lines, no table over eight game-sourced rows outside `docs/game-facts/`).

## 6. Performance measurements [machine]

The Foundry, 16:9, 60 Hz interpolation, M2 Pro: the game held 30.0 fps and the display 60.0 presents per second;
Level audio measured -13 dBFS RMS and menu music
about -21.5 dBFS, with 0 audio microcode errors.

## What has NOT been verified

- **Human play** [hand]: a few sessions on Windows and on macOS (two rounds on 2026-10-15). Their findings (a freeze
  after RETRY, a flashing strip at the left edge, B not going back in menus that draw a 3D scene) are fixed. This is an early
  preview: most of the game has not been played by hand on this build. The release build was played on Windows on 2026-10-18
  from a fresh install: no problems found.
- **Windows beyond one machine**: one Windows 11 PC (AMD GPU, 150 % display scaling). Not yet: a controller on Windows, NVIDIA and
  Intel GPUs, Windows 10, other display scaling, SmartScreen's Run anyway on a downloaded copy.
- **Linux**: never run on a real machine; it compiles in CI.
- **A clean Mac without developer tools.**
- **Audio fidelity** against hardware or another emulator: only level, tempo and spectrum measurements.
- **Other machines' performance**: all numbers are one M2 Pro.
- **Levels other than the Foundry** for frame interpolation, and every level for gameplay completeness.
- **Notarization.** **Intel Macs**: the universal app's Intel half has run only under Rosetta, on THPS1's build of the same host.
