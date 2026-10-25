# Known issues

What isn't finished or hasn't been checked in v0.1.0-preview. "Untested" means the code exists but hasn't been run in that
setting. Problems fixed before this release are in the [CHANGELOG](../CHANGELOG.md). Found something that isn't here?
[TESTING](TESTING.md) says how to report it.

## Early preview

THPS3 64: Recompiled is an **early preview**. It shares its host with THPS1 64: Recompiled v0.1 and passes its own automated
suite, but it has had much less hand play than THPS1, so this list is likely incomplete. These parts of the game haven't
been played through by a person on this build: the park editor, split screen in a level, replays and most competitions.
[TESTING](TESTING.md) lists what we'd like you to try.

## Platforms

- **macOS (one universal app) and Windows x64 only.** Linux isn't in this release: its code builds in CI, with stand-in
  game code, but has never been run.
- **Intel Macs are untested.** The app's Intel half has only run under Rosetta on an Apple Silicon Mac. Which Intel GPUs
  RT64's Metal renderer supports hasn't been checked.
- **Windows has been tested on one PC:** Windows 11, an Intel Core i7-8809G with AMD Radeon RX Vega M, Direct3D 12, 150 %
  display scaling. Untested: other GPUs (NVIDIA, Intel), Windows 10, other display scaling, and a controller on Windows.
- **Windows: the first start of a new copy is slow to show a picture**, about 4.5 s on the test PC. Later starts are fast.
  It happens with each newly written program file, even with an existing config folder (probably the GPU driver's
  shader cache).
- **Windows: frame pacing is a little less even than on macOS.** Both hold 60 frames per second, but the slowest 1 % of
  frames take about 18.4 ms on the test PC against 16.9 ms on the Mac.
- **The app isn't notarized (macOS) or code-signed (Windows)**, so the first start needs the one-time Gatekeeper or
  SmartScreen step in the [README](../README.md#install).
- **The missing-compiler page** on macOS hasn't been tried on a Mac without the Command Line Tools.

## Game versions

- **Only USA is supported.** It's the only dump we have, so no other release (a European one, for example) is
  supported or tested.
- **Hand play:** a few sessions on macOS and Windows. The problems found there (a freeze after RETRY, a flashing strip at
  the left edge in widescreen) are fixed.

## Graphics

- **Widescreen:** the 3D view is widened and the in-level HUD moves to the screen edges (`hud = expand`; `original` keeps
  it in the centred 4:3 area). The HUD keeps its 4:3 size, and a few elements (the timer, trick lines, the pause menu,
  result pages) stay centred on purpose. Menus, loading screens and other 2D screens are pillarboxed 4:3.
- **Frame interpolation** at 60 Hz and up pairs 97 % or more of the moving parts between game frames in
  the Foundry (the first career level) and the menus. Other levels have cars and other moving objects
  whose pairing hasn't been checked. Replays and cutscenes are untested.
- **The special meter at `hud = original`** has a top line, a tall left tick, a short right stub and bars hanging below.
  The game itself draws it that way, at every aspect ratio and frame rate.
- **Each level start freezes the picture briefly** while the game loads the level, and the **attract demo** has short
  stalls every ten seconds or so. (Measured at 100 to 150 ms in THPS1, which loads levels the same way.)
- RT64 **compiles shaders the first time an effect appears**, which causes short hitches.
- With the window hidden or covered, the app stops presenting frames; the game keeps running.
- Apple GPUs have no 8x MSAA; asking for it turns MSAA off.

## Stability

- **A crash in the graphics layer** (inside RT64, seen in all three games under load) is fixed in this release.
  A 30-minute soak on macOS found no crash or hang.- **Two intermittent crashes** were each seen once in about 60 launches during development, on a loaded machine, and not in
  a later soak of 50 launches: a SIGBUS in the game's asset cache shortly after the start, and a SIGSEGV inside RT64
  (`processDisplayLists`). The second looks like the graphics-layer crash above and is probably fixed with it. If you see
  either, please attach `crash.log`.

## Input and saves

- **Player 2:** there's no screen for assigning controllers. The first controller to press a button is player 1 and the
  next is player 2; the keyboard is always player 1, so two players need two controllers ([MANUAL](MANUAL.md#controls)).
- OPTIONS > CONTROLLER TWO opens only for the second controller's A, as in the original game.
- **Single keys and buttons** can't be rebound in the settings menu yet; it picks a layout. Edit `controls.cfg` for the
  rest.
- **Cheats are test aids:** off by default. They aren't stored in the Controller Pak save, but progress you make with a
  cheat on (goals, scores, levels unlocked by playing) is saved as usual. While one is on, the log and `crash.log` name it ([MANUAL](MANUAL.md#cheats)).

## Audio

- Audio comes from the translated audio microcode. The test suite checks its level and spectrum; it isn't claimed to be
  bit-exact with the console.

## Tests

- One check of the skater's air state (`level_ollie` / `level_grab`) only warns: the value it reads isn't a real air flag.
  Ollies and grabs are checked by the pad-record test and by hand.

## Untested

- The **park editor**, **split screen in a level** (two players have only been run by a test script: both skaters picked,
  the level loads), **replays** and most **competitions**.
- The **Rumble Pak** on a real controller, and the game's own **Controller Pak manager** (deleting or repairing notes).

## Not in this release

Texture packs, mods, rebinding single keys in the menu, and a launcher beyond the first-start window.
