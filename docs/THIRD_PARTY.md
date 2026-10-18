# Third-party components

<!-- The list is compiled from the licence
files of the pinned upstream sources; regenerate and re-read it against the exact pins and the actual bundle at release time. -->

Everything below is **fetched at build time by `decomp/common/host/tools/setup_runtime.py` at pinned commits**, or
bundled into the release app as unmodified upstream builds. None of their source is stored in this repository; our changes
to RT64 and N64ModernRuntime are the patch files in `decomp/common/host/patches/`, applied by `setup_runtime.py` in a fixed order.

THPS3 64: Recompiled as a whole is GPL-3.0-only, because the built app links N64ModernRuntime (GPL-3.0).

The tables below were checked on 2026-10-12 against the real macOS bundles of all three games (THPS1, THPS2 and THPS3 are
built from the same shared host, runtime pins and menu): the engine's dynamic dependencies (`otool -L`: our SDL2 plus Apple system
frameworks), the symbols of the statically linked components, and the file list of the app (`scan_bundle.py --no-rom` lists the files it allows).

## Linked into the app

| Component | Pin | Licence | Notes |
|---|---|---|---|
| N64ModernRuntime (librecomp, ultramodern) | `cdf5abb` | **GPL-3.0** | linked; one patch of ours applied (`ultramodern-sp-complete-after-dl.patch`: the game is told "RSP done" after the display list is parsed, not before; a few lines in `events.cpp`; it fixes a crash in RT64's display-list parser). A second patch, `ultramodern-vi-rate.patch` (real 50 Hz PAL timing), is in the repository but **not applied** to any release build. Its vector-unit code (`rsp_vu_impl.hpp`) is adapted from the Ares emulator (ISC licence, notice in the file). Its `thirdparty/`: concurrentqueue (BSD-2-Clause, with a separate Boost-licensed semaphore header), nlohmann json (MIT), miniz (MIT), o1heap (MIT), sse2neon (MIT), xxHash (BSD-2-Clause) |
| RT64 | `4337374` (+ plume `d890ac8`) | MIT | linked; four patches of ours (`rt64-hlslpp-labs.patch`, `rt64-present-capture-widescreen.patch`, `rt64-hfr.patch`, `rt64-metal-clear-state.patch`; the first is a one-line include fix, the last a Metal-only state-cache fix) |
| RT64 `src/contrib/` | as RT64 | per directory: hlslpp, ddspp, plume, re-spirv, Dear ImGui, implot, im3d (MIT); nativefiledialog-extended (zlib); SPIRV-Cross (Apache-2.0; a build tool on macOS: its output, the Metal shaders, is compiled into the engine); stb (MIT or public domain); xxHash (BSD-2-Clause); zstd (BSD-3-Clause, dual with GPL-2.0; used under BSD); **mupen64plus-core API headers (GPL-2.0-or-later; compatible with GPL-3.0)**; Microsoft DirectX Shader Compiler (a build tool: RT64's copy is used at build time and is not in the app; the Windows zip ships `dxcompiler.dll` (the LLVM Release License, University of Illinois/NCSA) and `dxil.dll` (Microsoft Software License Terms for the DirectX Shader Compiler, whose "Distributable Code" section sets the terms for distributing it), both **from Microsoft's DXC release v1.8.2407** (`dxc_2024_07_31.zip`, SHA-256 `e2627f00...67b5`; downloaded at build time, not RT64's v1.7.2212 copies), with both texts from that release, unchanged, in `resources/licenses/DXC-*.txt`) | the exact list is generated at release time from the pin |
| SDL2 2.32.10 | built from the upstream release tarball (SHA-256 pinned in `decomp/common/host/tools/build_sdl2.py`); bundled as `libSDL2-2.0.0.dylib` in the macOS app and as `SDL2.dll` in the Windows zip | zlib | the only non-system library the macOS engine depends on |
| SDL's built-in controller mappings (SDL_GameControllerDB) | compiled into SDL2 | zlib | no separate `gamecontrollerdb.txt` is shipped |

### The DXC files in the Windows zip

`dxil.dll` and `dxcompiler.dll` are Microsoft's DirectX Shader Compiler v1.8.2407 files, unmodified, redistributed under
Microsoft's licence terms (included as `resources/licenses/DXC-*.txt`). The macOS app contains no DXC file.

## In-game settings menu (linked into the app, with its fonts)

| Component | Pin | Licence | Notes |
|---|---|---|---|
| In-game settings menu: code and styles derived from Zelda64Recomp | `b65c482` | **GPL-3.0** | `decomp/common/host/src/ui/ui_renderer.*`, the two `decomp/common/host/ui/shaders/*.hlsl`, `decomp/common/host/ui/menu/*.rcss` and the structure of `decomp/common/host/src/ui/ui_host.cpp`; the changes are listed in `NOTICE`. Not its Chiaro fonts or Majora's Mask artwork |
| RmlUi | `7a06f27` (6.0) | MIT | built from source into the app, with lunasvg for the icons |
| lunasvg (with its plutovg) | `4166d0c` | MIT | |
| FreeType | 2.13.3 (`42608f7`) | FreeType License (or GPL-2.0; we use the FTL) | built from source; "portions of this software are copyright The FreeType Project (www.freetype.org)" |
| Fonts of the settings menu: Lato (Latin subset), Noto Emoji, PromptFont | Zelda64Recomp `b65c482`, SHA-256 pinned in `decomp/common/host/tools/setup_runtime.py` | SIL OFL 1.1 | fetched at build time, unmodified, bundled in `Resources/ui/fonts` with the licence text (`decomp/common/host/ui/FONTS-LICENSE.txt`) |

## Bundled as tools (macOS app, `Resources/tools`)

| Component | Pin | Licence | Notes |
|---|---|---|---|
| N64Recomp (the `N64Recomp` and `RSPRecomp` executables) | `ffb39cd` | MIT | built from the pin, unmodified. Statically contains ELFIO (MIT), fmt (MIT), rabbitizer (MIT), tomlplusplus (MIT) and, for LiveRecomp, sljit (BSD-2-Clause) |
| N64Recomp's `recomp.h` and the runtime headers the generated C includes | as above | MIT / GPL-3.0 as in their directories | shipped as "SDK" headers so the first-run build can compile; they are headers of the runtime above |

## Used at development time, not shipped

| Component | Licence | Notes |
|---|---|---|
| splat64 `0.50.0`, spimdisasm `1.42.4`, rabbitizer `1.16.2` | MIT | decompilation tooling (`requirements.txt`) |
| n64sym (shygoo) | MIT | signature matching for libultra / libmus names |
| rnc_propack_source (lab313ru) | custom permissive: "you may use this source code in any commercial / non-commercial project", attribution requested; GitHub reports no licence | **not needed at run time and not bundled.** `make deps` fetches it for the ROM-rebuild path only; we keep a patch against it (`decomp/common/rnc_propack/lookahead.patch`). Credit given in README and NOTICE |
| GNU binutils for MIPS (`mips-linux-gnu-*`), mupen64plus (for the boot test) | GPL | external tools the developer installs |
| Python 3.11+, CMake, Ninja, LLVM/clang | PSF, BSD, Apache-2.0 with LLVM exception | |

## Not included

RecompFrontend (recompui, recompinput) has no licence upstream (N64Recomp/RecompFrontend issue #44) and is not part of
this repository or any release. Fonts and icons that its launcher uses are therefore not included either; the in-game menu above is a separate, licensed one.
