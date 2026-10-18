# Testing THPS3 64: Recompiled

**THPS3 64: Recompiled is an early preview** (v0.1.0-preview). Here is what that means:

- It uses the same shared host as THPS1 64: Recompiled v0.1 and passes its own automated test suite on macOS.
- It has had much less hand play than THPS1: a few sessions, on one Windows PC and one Mac. Whole parts of the
  game (the park editor, split-screen play, replays, most competitions) have never been played through by a person on this build.
- Expect bugs we have not seen. A crash, a freeze, a wrong picture or a lost save are all possible, so back up
  `saves/` before you rely on a career.
- It is labelled a preview so that players can help test it now.
  Your reports decide what gets fixed before a v0.1 of this game.

Please read [KNOWN-ISSUES](KNOWN-ISSUES.md) first, so you can skip what we already know about.

## The quick way to every level

Most of the game is locked behind career progress. To test a late level without playing a career first, open the in-game settings
menu (**Esc**, or **Back** on a controller), go to the **Cheats** tab and turn on **Unlock All Levels**, or start the app once
with `--unlock-levels`. Cheats are test aids and are off by default. They aren't stored in your save, but progress you make
with a cheat on is saved as usual, so a career you test with one on is a normal career save. See [Cheats](MANUAL.md#cheats).

When you report a problem with a career, a save or a level unlock, say whether a cheat was on. If you can, check whether the problem
also happens with every cheat off.

## What to try

You don't have to do all of this. Even one item, with a good report, helps. About 20 to 30 minutes covers the main path.

1. **Install and first launch.** Unzip, get past Gatekeeper or SmartScreen ([README](../README.md#install)), choose your dump and let the
   game build. Note how long the build took and anything unclear on the way.
2. **Front end.** The intro and logos, the main menu, OPTIONS. Turn on **Skip Intro** in the settings menu, quit, and start again.
3. **Settings menu.** Open it with Esc (Back on a controller) and try each tab: aspect ratio (4:3, 16:9, 21:9), HUD placement,
   frame rate (`display` and `original`), resolution, MSAA, window mode and full screen, volume. Quit and restart: the settings
   should still be there.
4. **A career.** Start a career and play a level for a few minutes: ollie, flip, grab, grind, manuals, reverts (R in a halfpipe), the special meter and a special trick. Pause,
   **Retry** a few times, then **End Run**.
5. **Saves.** Save the career to the Controller Pak, quit the app, start it again and load the career. Try Create-a-Skater, and
   save and load a created skater.
6. **Every level.** With Unlock All Levels on, start each level in Free Skate (or Single Session), skate for a minute, pause and
   quit to the menu. Look for a level that does not load, a crash, or missing scenery.
7. **Controllers.** Try a controller and the keyboard; the two layouts in the Controls tab (Xbox-style and N64). With two
   controllers, try a 2-player game. With one controller, check that the player-2 menus can still be left. Unplug and replug a
   controller while playing.

**Things nobody has tried yet** (reports are especially welcome):
- a **Rumble Pak** (`--rumble-pak`) on a real controller;
- the game's own **Controller Pak manager** (deleting or repairing notes);
- **`--tv pal`** (experimental: a PAL-sized picture, still at 60 Hz pacing; real 50 Hz is not implemented);
- **split screen in a level**, the **park editor** and **replays**;
- **an Intel Mac** (the macOS app is universal, but its Intel half has only been run on Apple Silicon, under Rosetta);
- **Windows** with an NVIDIA or Intel GPU, on Windows 10, or with display scaling other than 150 %.

## What to look for

- **Crashes:** the app closes or disappears. It writes `crash.log` to the config folder (see below).
- **Freezes:** the picture stops, or the game stops answering input, for more than a few seconds.
- **Stutter:** a short freeze when a level starts (100 to 150 ms) and small stalls during the attract demo are known. Anything
  longer or more often, in normal play, is worth a report.
- **Picture:** missing or flickering scenery, a one-frame pop or flash, stray bars at the screen edges, HUD parts out of place or
  cut off, wrong colours. Say which aspect ratio, HUD placement and frame rate you were using.
- **Sound:** missing, distorted or out of step.
- **Input:** a button that does the wrong thing, a menu you cannot leave, a stuck input.
- **Saves:** a career, a setting or a created skater that is not there after a restart.

## How to report a bug

Use the [bug report form](https://github.com/THPS64Recomp/THPS3-64Recomp/issues/new/choose); it asks for each of these. Questions and general
play-testing notes go to [Discussions](https://github.com/THPS64Recomp/THPS3-64Recomp/discussions). Please include:

1. **The game and release**: for example "Tony Hawk's Pro Skater 3, USA". Run the app with `--check-rom FILE` if you are not sure which dump you have.
2. **The app version**: this one is early preview, v0.1.0-preview; say which zip you downloaded (macOS or Windows).
3. **Your system**: macOS version and Mac model, or Windows version, CPU and GPU. The display's refresh rate (60 Hz, 120 Hz...).
4. **Your settings**: attach `general.cfg`, `graphics.cfg` and `controls.cfg` from the config folder (plain text, no game data),
   or name the settings you changed. Controller or keyboard, and which controller.
5. **Cheats on or off**: which ones, if any. `cheats.cfg` in the config folder holds what the Cheats tab saved; a flag such as
   `--unlock-levels` is for one run only, so say if you used one. While a cheat is on, the log names it at start, and `crash.log` names it too.
6. **`crash.log`** if the app crashed. It is in the config folder: `~/Library/Application Support/THPS3-64Recomp/` on macOS,
   `%LOCALAPPDATA%\THPS3-64Recomp\` on Windows (or the folder with `portable.txt`). If the first-run build failed, attach
   `first-run.log` and the `game/work-*/logs/` folder instead.
7. **What you did**, what you expected, what happened, and how often (every time, once in an hour...).
8. **A screenshot or a short video** of the problem, if it shows on screen. Keep it to the problem itself.
9. **The log**, if you can: start the app from a terminal with `--verbose` and save the output. On macOS:
   `"/path/to/THPS3 64 Recompiled.app/Contents/MacOS/thps3_recomp" --verbose 2>&1 | tee run.log`. On Windows, in PowerShell in the app's
   folder: `.\THPS3-64Recomp.exe --verbose | Out-File run.log` (the program has no console window of its own, so its output has to be piped).

**Never attach your ROM, the generated game library (`game/`), the stored copy of your dump, or long recordings of the game's
music.** We cannot accept them, and we don't need them.
