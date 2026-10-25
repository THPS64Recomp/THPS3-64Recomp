# Changelog

All notable changes to THPS3 64: Recompiled are listed here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Changes to the shared host are listed in the
[THPS64Host changelog](https://github.com/THPS64Recomp/THPS64Host/blob/main/CHANGELOG.md).

## [Unreleased]

### Added
- Graphics > Picture Border (`border = fill`, `--border fill`): the 3D picture reaches the edges of the window, without the
  thin black frame the game leaves for a TV's overscan. It shows a little more of the scene at the same size (no zoom). Off by
  default; menus and loading screens keep their own frame. In a two-player split screen, both views reach the edges
  too and meet at the game's thin divider line in the middle.
- Rebinding in the settings menu: the Controls tab has a row per N64 input with two controller slots and two keyboard
  slots. Choose a slot and press the new button or key; a button another action uses trades places with it, and
  Default puts a row back. A slot that differs from the layout shows in yellow, and Reset all to default (it asks first)
  puts every binding back. Changes work at once and are saved to `controls.cfg` ([MANUAL](docs/MANUAL.md#controls)).
- A Controllers list in the Controls tab: which controller is player 1 or 2, what it is pressing right now, and buttons
  to swap players or give a controller either player. One controller on player 2 with the keyboard alone on player 1
  makes a two-player game with one controller. The choice lasts until you quit.
- Test sessions `menu-controls`, `menu-controls-reload` and `menu-ports` (virtual pads).

### Changed
- Built on THPS64Host v0.2.0.
- Removed the known issue "at 21:9, a far wall can drop out at the right edge". It was reported in THPS1, where it
  doesn't happen in v0.1.0, and the widescreen code involved is shared by all three games.
- Two-player split screen fills the picture in widescreen (16:9, 21:9, following the window): each player's view is widened
  to its half, and each player's HUD sits at its own view's edge (also with HUD Placement `original`). 4:3 is unchanged.
  It's on by default; Graphics > Two-Player Split Screen (`split`, `--split original`) keeps both views in the 4:3 area,
  each with its HUD inside it, and black bands at the sides.
- Level starts freeze the picture for about 0.16 s instead of 0.2 s: the shared host unpacks the game's data twice as
  fast and runs the game's `memset` and `memcpy` natively.

### Fixed
- With a `controls.cfg` that matches no preset (edited by hand), Xbox B flipped and grabbed at once while skating. The
  east button's split between flip and back now follows the bindings, not the preset name.

## [0.1.0-preview] - 2026-10-18

An early preview, released next to THPS1 64: Recompiled v0.1.0 and built on THPS64Host v0.1.0. It runs
the USA release of the N64 game, on macOS (universal) and Windows x64. It has had much
less hand play than THPS1; see the README.

### Added
- A first start that builds the game from your own dump, on your machine: the main program and its 16 front-end screens.
  On macOS it offers Apple's installer if the Command Line Tools are missing; the Windows zip brings its own compiler.
- Native rendering through RT64 (Metal, Direct3D 12), scaled to the window, with MSAA 4x.
- Widescreen: 16:9 by default, 21:9, or following the window. The in-level HUD moves to the screen edges
  (`hud = expand`); `original` keeps it in the centred 4:3 area.
- Frame interpolation to the display's rate (60 Hz, 120 Hz on ProMotion) over the game's 30 fps.
- The in-game settings menu (Esc, or Back on a controller): general, controls, graphics, sound and cheats.
- An Xbox-style controller layout (tricks on the face buttons; B is grab while skating and back in menus) and the N64
  layout; keyboard and SDL controllers, two players, hot-plugging; every binding in `controls.cfg`.
- Controller Pak saves as a standard 32 KiB `.mpk` file.
- Cheats for testing: Unlock All Levels, Perfect Balance, Slow Motion, Skip to Restart and Always Special. They're off by
  default and named in the log and `crash.log` while on. The cheats aren't stored in the save; progress made with one on is
  saved as usual.
- Portable mode: a `portable.txt` beside the app keeps settings and saves next to it.

### Fixed
- The game froze after PAUSE > RETRY (a message-queue deadlock in the Controller Pak path).
- A strip at the left edge of the widescreen picture flashed with stale 3D.
- At 60 Hz the skater moved in 30 Hz steps against a smooth background (too few transforms were paired).
- Short pops in the sound when the audio output ran dry for a moment (found in THPS1; the fix is in the shared host). The
  output now fades out and back in instead of cutting.
- A crash in RT64's display-list parser: the runtime told the game the graphics task was done before RT64 had read it
  (an N64ModernRuntime patch).
- With one controller, the 2 PLAYER screens that wait for player 2 (choose skater, continue, handicap) locked up.
- B didn't go back in menus that draw a 3D scene (Create-a-Skater, the pause menu, the screens over a level).
- Windows: the settings migration was never saved, and the frame-interpolation time budget never applied.

[Unreleased]: https://github.com/THPS64Recomp/THPS3-64Recomp/compare/v0.1.0-preview...HEAD
[0.1.0-preview]: https://github.com/THPS64Recomp/THPS3-64Recomp/releases/tag/v0.1.0-preview
