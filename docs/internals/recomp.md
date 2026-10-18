# How the THPS3 recomp works

The internals of the native port of Tony Hawk's Pro Skater 3 (N64, USA): what the translator needs, how the host boots the game, and
what differs from the THPS2 port, which it was made from. Addresses are for the USA release. For the front-end screens see
[overlays.md](overlays.md). Labels: **[V]** verified by a script, test or by reading the code; **[I]** inference.
Since ADR 0006 the host sources are shared by THPS1-3: `src/x.cpp` in this page is `decomp/common/host/src/x.cpp`, and the game's own files are its
profile in `decomp/thps3/recomp-host/` (`game/game.toml`, `versions/`, `config/`). The first-run (split) build reads the front-end screens from the
user's ROM with a ROM-free recipe ([overlays.md](overlays.md#at-first-run-the-split-build)); the shared design is in the THPS1 repository's `recomp.md`, section 5.

## 1. Pipeline

```
your dump (.z64/.n64/.v64) --hash check--> inflate the 15 code chunks (native ERZ decoder, method 2)
   --> code blob: ROM[0:0x1000] | boot segment | inflated main image | the 16 pre-linked overlays   (stays on your machine)
   --> N64Recomp + the function list (recomp/thps3.syms.toml, our hooks)    --> 3,937 functions of C
   --> RSPRecomp + config/thps3.aspMain.toml                                --> the audio microcode as C++
   --> system compiler                                                      --> the game code
engine (host + N64ModernRuntime + RT64 + SDL) runs it.
```

- **N64Recomp** (`ffb39cd`, the same pin as THPS1 and THPS2) reports **0 warnings**: 3,394 functions in the main program
  (253 boot, 3,141 main) plus 543 in the overlays. 338 indirect-call sites use the runtime's function lookup, 71 of 75 indirect
  jumps become `switch` statements (the other 4 are libultra's), and 529 `do_break` calls come from division checks. [V]
- The recompiler's config has entry point `0x80000400` and nine instruction patches: the PlayStation coprocessor-2 leftovers, in one
  function at `0x80045B00` (six `mtc2` at `0x80045D38` and three `mfc2` at `0x80045D64`), turned into no-ops. The audio microcode is
  byte-identical to THPS2's, at blob offset `0xAC9A0`.
- N64Recomp's symbol-file mode needs the entry function at ROM `0x1000`, so the code blob is `ROM[0:0x1000]`, the boot segment, then
  the inflated main image at blob `0x13B70` (vram `0x80016B20`, size `0xEBC30`). [V]
- Stubs the host must provide (`recomp/runtime_stubs.txt`): the same 16 libultra internals as THPS2.
- The generated C is ROM-derived. It is never committed and never shipped.

## 2. Boot

The boot segment is THPS2's, three words apart. As in THPS2: `load_overlays(0x13B70, 0x80016B20, 0xEBC30)` re-registers the main
image after librecomp's IPL3 step; `Boot_Main` runs recompiled with `Boot_PioCopy` (`0x80000AB4`) and `Erz_Unpack*` hooked; the last
chunk (0x522 bytes) is completed from the ROM because the original copy rounds down to whole words. The game's DMA thread
(`Pi_DmaThread`, `0x800D3F04`) uses `osPiRawStartDma`, hooked to copy from the ROM and post the registered message. `GameEntry` is
`0x800BACB8`. [V]

## 3. The rest of the host

The host is THPS2's, renamed: frame pacing, audio pacing, the scissor edge fix and the high-frame-rate code work as in THPS1.
THPS3-specific:

- **Widescreen**: `View_ComputeCullPlanes` `0x800C6078` and `View_SetFrustum` `0x800C557C` (the view struct is THPS2's); RT64 widens
  the projection; menus and loading screens stay 4:3 and centred; the in-level HUD goes to the screen edges by default (`src/hud_anchor.cpp`; `--hud original` keeps it centred).
- **Controls** (pad layer at `0x800EF794`): C-down, C-left, C-right and C-up are pad records 3, 1, 2 and 0 (ollie, flip, grab, grind); N64
  A is ollie too and N64 B is flip too; L is spin left and nollie; **R is spin right and switch, and revert** out of a halfpipe. The
  Xbox-style layout drops the B that the east button sends while the skater is under control (the game's run flag `gRunActive`), because the game reads N64 B as flip; on every other screen it drops C-right instead.
- **Controller Pak**: a career save is a note of 5,920 bytes in a standard `.mpk`.
- **Skip Intro**: a hook on the intro screen's update, which lives in an overlay (`ovl_intro_0018C`).
- **Level select aid** (`--unlock-levels`, a test aid): a hook on the level-availability test that the level-select screen calls, which
  makes levels 0 to 9 selectable in a fresh career. Nine levels were each loaded and skated briefly this way with no lookup misses
  or crashes.
- **Overlays**: 16 screens ([overlays.md](overlays.md)), registered when the game's loader DMAs them.

Symbol bugs found while bringing the host up (fixed in `symbols/main.txt`): a name suffix read as an address cut a function to one
instruction, and `Trick_Bail` was sized `0xFC` instead of `0x104`.

## 4. Platforms

macOS (Metal) is the only system the game has been played on. The Windows and Linux support is written and built in CI with
ROM-free stand-in functions: OS seams in `src/platform.{h,cpp}`, `src/crash.cpp`, `create_window()` in `src/main.cpp` and the CMake
file, structured after Zelda64Recomp's `main.cpp` (credits in [NOTICE](../../NOTICE.md)). Config folders: macOS
`~/Library/Application Support/THPS3-64Recomp`, Windows `%LOCALAPPDATA%\THPS3-64Recomp`, Linux `$XDG_CONFIG_HOME` or
`~/.config/THPS3-64Recomp`; a `portable.txt` beside the executable overrides them.

## 5. Building the host from source

`python3 -I decomp/thps3/recomp-host/tools/build_host.py --rom USA.z64` does everything: the pinned runtime and RT64 plus our patches,
N64Recomp and RSPRecomp at the pin, a venv with rabbitizer, the code blob, the generated C, then CMake and Ninja. By hand and
per-option details: [the host README](../../decomp/thps3/recomp-host/README.md).

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived
from analysis of a retail cartridge dump. No game data is reproduced beyond names, addresses and individual values. See the README.
