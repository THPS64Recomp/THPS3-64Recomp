# Building THPS3 64: Recompiled

You need your own dump of *Tony Hawk's Pro Skater 3* (USA, the only dump we have) to build a playable game. Everything made from it (the code
image, the generated C, the game library, test pictures) is written under git-ignored `build/` folders. Never commit or
share any of it.

## Get the code

The shared host, [THPS64Host](https://github.com/THPS64Recomp/THPS64Host), is a git submodule mounted at `decomp/common`; its host sources are in
`decomp/common/host/`. Clone with `--recursive`:

```sh
git clone --recursive https://github.com/THPS64Recomp/THPS3-64Recomp.git
cd THPS3-64Recomp
```

If you cloned without it, run `git submodule update --init --recursive`. The submodule is pinned to a host release tag.

## Dependencies

All systems need git, Python 3.11 or newer, CMake 3.20 or newer, and Ninja.

- **macOS:** Xcode or the Command Line Tools (with the Metal toolchain), plus `brew install cmake ninja sdl2 pkgconf`.
- **Windows:** Visual Studio 2022 with the "C++ Clang Compiler for Windows" and "C++ CMake tools" components. The build
  uses clang-cl and finds Visual Studio itself. Clone to a short path (RT64 nests deeply) and turn on long paths first:
  `git config --global core.longpaths true`.
- **Linux:** clang or gcc and the SDL2, Vulkan, X11 and GTK 3 development packages (on Debian or Ubuntu:
  `ninja-build clang libsdl2-dev libvulkan-dev libx11-dev libgtk-3-dev`). Linux builds in CI but hasn't been run on a desktop.

## Build

No game dump? Build with `--stub` (what CI does), then run `tools/check.sh`:

```sh
python3 -I decomp/thps3/recomp-host/tools/build_host.py --stub
tools/check.sh
```

The stub build has empty stand-in game functions: it checks your toolchain and your change, but it can't play.

With your dump, one command does everything:

```sh
python3 -I decomp/thps3/recomp-host/tools/build_host.py --rom /path/to/your/dump.z64
```

It runs these steps, and skips any whose output already exists (`--clean` starts over):
1. fetch the pinned N64ModernRuntime and RT64 and apply our patches (`decomp/common/host/tools/setup_runtime.py`, below);
2. build N64Recomp and RSPRecomp at their pinned commit;
3. make a Python venv with `rabbitizer`;
4. unpack the code from your dump and generate the C;
5. configure and build the host with CMake and Ninja.

The build prints about 230 compiler warnings from RT64 and imgui. They are expected; only errors stop it.

The result is `decomp/thps3/recomp-host/build/cmake/thps3_recomp`. Start it with `--rom /path/to/your/dump.z64` the first time; it keeps a
copy, so later starts need no flag.
On Windows, run the same command with `python` in a normal command prompt, or use
`powershell -ExecutionPolicy Bypass -File decomp/thps3/recomp-host\tools\build_windows.ps1 -Rom <your dump>`. The binary is then
`thps3_recomp.exe`; the release package names it `THPS3-64Recomp.exe`.

Building more than one game? Share one runtime: `--runtime ~/thps64-runtime`. The first build sets it up (about 850 MB),
and the other games reuse it. `tools/check.sh` uses the folder in `THPS_RUNTIME_DIR` the same way.

### Other builds

| Command | What it builds |
|---|---|
| `build_host.py --split` | the engine with no game code (`build/cmake-split`), as in a release: its first start builds the game from your dump |
| `build_host.py --split --own-sdl2` | the same, linked against our pinned SDL2 build, as the release app is |
| `build_host.py --stub` | the host with empty stand-in game functions, no dump needed: a toolchain check (it can't play) |

Releases are packaged from the split build with `decomp/common/host/tools/package_split.py`. The release workflow in
`.github/workflows/release.yml` shows the exact steps.

## Runtime setup

`setup_runtime.py` fetches the pinned upstream sources into a folder of your choice and applies our patches in a fixed
order:

```sh
python3 -I decomp/common/host/tools/setup_runtime.py /path/to/runtime
```

It fetches N64ModernRuntime and RT64, the settings menu's libraries and fonts (RmlUi, lunasvg, FreeType), and on Windows
Microsoft's DXC DLLs. Every download is checked against a pinned commit or SHA-256. Always make a fresh folder when a pin
changes; don't patch an existing tree by hand. The patches, why we carry them, and the test that guards each one are listed
in the host's patch register, [host/patches/README.md](https://github.com/THPS64Recomp/THPS64Host/blob/main/host/patches/README.md) (in this
repository: `decomp/common/host/patches/README.md`).

To build by hand once the runtime folder exists:

```sh
cmake -S decomp/thps3/recomp-host -B build/cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DRECOMP_RUNTIME_DIR=/path/to/runtime -DTHPS_STUB_FUNCS=ON
cmake --build build/cmake --target thps3_recomp
```

Use `-DTHPS_SPLIT_GAME_LIB=ON` instead of `-DTHPS_STUB_FUNCS=ON` for the split engine. The full manual route, with the
generated C, is in [decomp/thps3/recomp-host/README.md](decomp/thps3/recomp-host/README.md).

## Check before a pull request

```sh
tools/check.sh
```

It needs no dump. It runs the checks CI runs on a pull request: the host pin, the version tables, a build with stand-in
game functions (in its own folder, so your real build is left alone), and the binary's ROM-free checks. Each failure
prints a `Fix:` line, and a clean run ends with "Ready for a PR." On Windows, run it from Git Bash.

`tools/check.sh --maintainer` adds the steps that need your dumps (a real build, the full suite, the first-run test, the
push guard). Contributors don't need it. [MAINTAINING.md](https://github.com/THPS64Recomp/THPS64Host/blob/main/MAINTAINING.md) in THPS64Host
lists every check.

## Tests

The regression suite starts the game and plays it by pad input, checking each screen against reference pictures. It needs
your dump, and the reference pictures are made from it, so each machine records its own and they are never committed.

```sh
decomp/thps3/recomp-host/tools/test.sh --record    # the first time on a machine: record the reference pictures
decomp/thps3/recomp-host/tools/test.sh             # the whole suite; exit code 1 on any failure
decomp/thps3/recomp-host/tools/test.sh --first-run # the first-start flow of the split build
```

The suite finds your dump through `$THPS3_ROM`, or `--rom`. Only one copy of the game may run at a time, so close
it before running tests. On Windows, run `test.sh` from Git Bash.

Some checks need no dump: `test.sh --controls-cfg`, `test.sh --gfx-cfg`, and
`python3 -I decomp/thps3/recomp-host/tools/gen_versions.py check` (the version tables).

**What CI can and can't do.** CI (GitHub Actions) never has a ROM. It checks that our patches apply to the pinned upstream, validates the version tables, builds the host with stand-in game functions on Linux, Windows and macOS,
and runs the checks that need no dump. It can't play the game, so it can't test graphics, sound or input. Maintainers run
the full suite locally before merging a change that affects the game.

## Changing the shared host

Code under `decomp/common/host/` belongs to [THPS64Host](https://github.com/THPS64Recomp/THPS64Host). Change it there, in its own pull request; this
repository only moves the submodule to a new host tag. [CONTRIBUTING.md](CONTRIBUTING.md) has the details.

## The decompilation

`decomp/thps3/` holds the disassembly setup that rebuilds the retail ROM byte for byte. It's not needed to build the
port. See [decomp/thps3/README.md](decomp/thps3/README.md).
