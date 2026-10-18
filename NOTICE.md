# Notice

THPS3 64: Recompiled (THPS3-64Recomp) is an unofficial fan project. Copyright (c) 2026 the THPS3 64: Recompiled authors. SPDX-License-Identifier: GPL-3.0-only
for this project's own code, configuration and documentation (see [LICENSE](LICENSE)). The licence grants no rights in
the game. Third-party components and their licences are listed in [docs/THIRD_PARTY.md](docs/THIRD_PARTY.md).

## No game content

This repository and its releases contain no ROM data, game code or assets. The game's code is translated and compiled on
the player's machine from their own dump, and is never distributed. The docs and symbol files describe the game
(addresses, names, layouts) without copying it. RecompFrontend (no upstream licence) is not included.

## Code and names from other projects

Where a file holds adapted code, its header says so as well.

<!-- table-ok: credits and derivation list, not game data -->
| Source project (licence) | What we use | Where |
|---|---|---|
| [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) (GPL-3.0) | parts of the RT64 setup, the platform layer (window, DPI, timers, config folders, `portable.txt`), the Windows and Linux build settings, the stereo handling in `queue_samples`, and the settings menu's renderer, shaders and styles (not its fonts or artwork) | `decomp/common/host/src/`, `decomp/common/host/ui/`, `decomp/common/host/cmake/` |
| lab313ru's [rnc_propack_source](https://github.com/lab313ru/rnc_propack_source) | the packer for the game's compression format, fetched at build time, with a small patch of ours | `rnc_propack/lookahead.patch` in THPS64Host (`decomp/common/rnc_propack/` in a game repository) |
| shygoo's [n64sym](https://github.com/shygoo/n64sym) (MIT) | libultra and libmus function names | `decomp/thps3/symbols/` |
| The PS1 *Tony Hawk's Pro Skater 2* demo decompilation (emoluvjd) | function and class names, as a naming reference; no code, headers or data | `decomp/thps3/symbols/main.txt` |

No leaked source code was used.

## Trademarks

Tony Hawk's Pro Skater, Tony Hawk, Activision, Neversoft, Edge of Reality and Nintendo 64 are trademarks of their respective
owners. They are used only to identify the game and platform. This project is not affiliated with or endorsed by them.

## AI use

AI was used as a tool to assist development of the code, the docs and the testing; see the README.
