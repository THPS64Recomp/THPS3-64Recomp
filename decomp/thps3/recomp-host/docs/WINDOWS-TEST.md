# Windows test kit (THPS3 recomp host)

What to do on a real Windows machine to find out whether the Windows port works. Nothing in this host has ever run on
Windows: macOS is the only platform it has been played on. What *has* been checked without Windows is listed at the end.
Budget: about 45 minutes of testing after a build of about 30-60 minutes (first build; the generated C is 17 MB and RT64
has about 1,600 files).

## 1. What you need

<!-- table-ok: tester requirements list, not game data -->
| | |
|---|---|
| OS | Windows 10 22H2 or Windows 11, **x64** (Windows on ARM would run the x64 exe under emulation: untested, not a goal) |
| GPU | Any NVIDIA / AMD / Intel GPU from about 2016 on with a current driver (Direct3D 12, Shader Model 6.0). Note the GPU and driver version. |
| Controller | An Xbox pad is the baseline (a DualShock/DualSense/Switch Pro pad is a bonus). Keyboard also works. |
| Monitor | 60 Hz is enough; a 144 Hz monitor is useful for the high-frame-rate check. |
| Disk / RAM | About 10 GB free, 8 GB RAM or more. |
| Visual Studio 2022 | Community is fine. Workloads/components: **Desktop development with C++**, plus **C++ Clang Compiler for Windows** and **C++ CMake tools for Windows** (they bring clang-cl, CMake and Ninja). |
| Git | `winget install Git.Git` |
| Python 3.11+ | `winget install Python.Python.3.12` (tick "Add to PATH" if you use the installer from python.org) |
| Your ROM | THPS3 USA (SHA-1 `7b9438120c67214afaea09f4b106c54ef8f366c5`), `.z64`, `.n64` or `.v64`. Never copy a ROM into the repository; never upload one. |

Do **not** accept anything on the build machine you would not accept anyway: the script only downloads from GitHub
(upstream sources at pinned commits) and PyPI (`rabbitizer`); it accepts no licences and installs nothing system-wide.

## 2. Get the code

```powershell
git config --global core.longpaths true
git clone <repo-url> C:\g\THPS3-64Recomp   # a short path: RT64 nests deeply
cd C:\g\THPS3-64Recomp
git switch -c windows-fixes        # commit Windows fixes here
cd decomp\thps3\recomp-host
```

If the build stops with "path too long" or "file name too long" errors, enable long paths (`git config --system core.longpaths true`
as administrator; Windows setting `LongPathsEnabled`) or move the checkout closer to the drive root. Windows Defender
real-time scanning slows the build a lot: excluding the checkout folder is up to you.

## 3. Build (one command)

```powershell
powershell -ExecutionPolicy Bypass -File tools\build_windows.ps1 -Rom "C:\path\to\your-dump.z64"
```

It does, in order (each step is skipped when its output exists): fetches the pinned N64ModernRuntime and RT64 and applies
our patches; builds N64Recomp/RSPRecomp; makes a Python venv with `rabbitizer`; converts the ROM to the right byte order,
checks its SHA-1, and generates the code blob and the recompiled C (`build\gen`, **ROM-derived, stays on this machine**);
configures with CMake/Ninja/clang-cl; builds. The result is
`build\cmake\thps3_recomp.exe` with `dxil.dll`, `dxcompiler.dll` and `SDL2.dll` next to it.

Toolchain check without a ROM (about 30 min, builds the host with stub functions; the exe cannot play):
`tools\build_windows.ps1 -Stub`.

**If the build fails:** copy the first error. Windows-only compile and link errors are the most likely finding of this
whole exercise. Send the first error, or a patch, as an issue or pull request.

## 4. Test checklist (about 45 minutes)

Record for every run: Windows build number (`winver`), GPU + driver version, monitor Hz and display scale, the console
output, `crash.log` if any (in the config folder, see below), and which API RT64 chose.

Config folder: `%LOCALAPPDATA%\THPS3-64Recomp` (settings files, stored ROM copy, `saves\`, `crash.log`), or the folder
holding a file named `portable.txt` (next to the exe, or the current directory).

Run from a terminal (PowerShell) in `build\cmake`:

### 4.1 Start-up (10 min)
- [ ] Copy the folder to a path with a space and an apostrophe (e.g. `C:\Users\you\My Games\Tony's test`) and run
      `.\thps3_recomp.exe --features` (prints `frontend=0`, exits 0).
- [ ] `.\thps3_recomp.exe --check-rom "<your ROM>"` reports the right release (exit 0).
- [ ] `.\thps3_recomp.exe --rom "<your ROM>" --verbose`: a window appears. The log line `RT64 setup result=0 chosen API=...`
      should say **D3D12**. Intro and menus draw correctly; no error spam.
- [ ] The config folder was created in `%LOCALAPPDATA%\THPS3-64Recomp` (or beside the exe with `portable.txt`).
- [ ] Close with the window button, then again with Alt+F4: exit code 0 (`echo $LASTEXITCODE`), no hang, no crash dialog.
- [ ] Try `--api vulkan` once: does it run? (Needs a Vulkan driver; report either way.)

### 4.2 Gameplay (15 min)
- [ ] Skip the intro, enter a level and skate for several minutes.
- [ ] Video: no black bars at 16:9 or ultrawide (`--aspect 21:9`), no magenta edge columns with MSAA on, correct colours,
      readable text. Compare with the Mac if you can.
- [ ] Audio: music and effects present, no crackle or drift over 5 minutes, volume setting works, nothing left playing after
      exit. (This is the first time the RSP audio code runs through x64 SSE.)
- [ ] Save a Controller Pak file (career), quit, relaunch, load it.

### 4.3 Controls (10 min)
- [ ] Keyboard: defaults work, all tricks; rebind a key in the settings menu's Controls tab (and one in `controls.cfg`, then restart).
- [ ] Xbox pad: sticks, triggers, d-pad; unplug and replug mid-game; rumble with `--rumble-pak`.
- [ ] Two pads: port assignment by first press; a Steam Input / DS4Windows setup if you have one.
- [ ] Input latency feels the same as on the Mac.

### 4.4 Display (10 min)
- [ ] Windowed to fullscreen with `--fullscreen` and with **Alt+Enter** (borderless); back again; window size restored.
- [ ] Resize the window; minimise and restore (the game should keep running, no stall, no crash).
- [ ] Display scaling 125 %, 150 %, 200 %: window size and sharpness (`--window 1280x720` means physical pixels).
- [ ] `--refresh display` on 60 Hz and 144 Hz (Show FPS: `--show-fps`) and a manual `--refresh 120`: watch for stutter, doubled
      frames, tearing. The game logic must stay at 30 Hz.
- [ ] MSAA 2x/4x/8x (`--msaa N`): works, or RT64 turns it off with a log line.

### 4.5 Failure paths (5 min)
- [ ] Wrong ROM, missing ROM, ROM path with accents (`--rom "C:\Pásta\x.z64"`): a clear message, exit 1.
- [ ] Crash log: `python -I tests\run.py --record --only crash_log` (runs the game, sends `--control crash`). The host must end
      with exit code 0xC0000005 and `crash.log` (config folder of the suite: `build\tests\...`) must contain
      `[game 0x........]` frames and an `innermost game function` line.
- [ ] Run two instances at once: the second one should fail cleanly.
- [ ] The regression suite (needs the references to be recorded on this machine, Metal frames are not valid references):
      `tools/test.sh --record`, then `tools/test.sh`, in Git Bash (BUILDING.md, "Tests"). Attach the summary table.
      Expected differences: anything pixel-compared may need `--rerecord`; the `crash_log` step accepts Windows exit codes.

### 4.6 Hardware matrix, if available
Intel integrated, an NVIDIA and an AMD GPU; D3D12 versus `--api vulkan`.

**Pass criterion for a first Windows release:** 4.1 to 4.4 pass on at least one NVIDIA or AMD GPU with an Xbox pad,
D3D12 chosen, no crash in a 20 minute session. Everything else becomes "known issues" text.

## 5. What to send back
`crash.log`, the console output of the failing run, GPU/driver/Windows build, the checklist with ticks. Never a ROM, a
generated `build\gen` file, a WAV or a screenshot of game assets.

## 6. What has been checked without Windows
- macOS: stub build, full build and the THPS3 regression suite pass with the platform seams in place.
- Windows target, cross-compiled on macOS with llvm-mingw (`x86_64-w64-mingw32`): all host source files compile, including the
  Windows branches of `main.cpp`, `platform.cpp`, `crash.cpp` and `rt64_context.cpp`. Linking was not possible there (mingw-w64's
  D3D12 headers are too old for plume).
- CI builds the host with ROM-free stand-in functions on Windows (clang-cl), Linux and macOS.

## 7. Known unproven on Windows
- D3D12 and Vulkan present capture (the `--control`/test tools): the plume copy fixes are written, compile-checked only.
- RT64 on D3D12: pacing, high refresh, MSAA, window resize; SDL2 2.26.3 (real SDL2, not the SDL3 compatibility layer the Mac
  used) for controllers, rumble and audio.
- The crash handler's frames have no function names (no PDB): `[game 0x........]` addresses map to names via
  `decomp/thps3/recomp/*.syms.toml`.
- Not done: preloading the exe to avoid page-fault stutter (Zelda64Recomp does it), a GUI-subsystem exe with message boxes,
  a file dialog or drag-and-drop for the ROM (use `--rom` once), SmartScreen/signing.

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. See the top-level README.
