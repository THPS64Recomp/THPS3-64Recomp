# THPS3 (N64) decompilation and recomp groundwork

Tony Hawk's Pro Skater 3 (N64, USA), ported by Edge of Reality. This directory turns your own ROM dump into a byte-identical
rebuild from disassembly. It also produces the function list and code blob that N64Recomp needs. The native host that runs the result
is in [recomp-host/](recomp-host/README.md). The pipeline is the same as THPS1's and THPS2's, driven by the shared tools in
[../common/](https://github.com/THPS64Recomp/THPS64Host/blob/main/TOOLS.md) (the per-game table `games.toml`, row `thps3`).

> **No ROM data is included or committed.** `baserom*`, `asm/`, `assets/`, `build/`, `linker_scripts/` and `include/` are
> generated locally from your dump and are git-ignored. The repository holds only configs, tools, symbol lists (addresses and
> names) and docs.

| Field | Value |
|---|---|
| ROM | 16 MiB big-endian z64, SHA-1 `7b9438120c67214afaea09f4b106c54ef8f366c5`, header `THPS3` / `N3TE` / rev 0 |
| Main image | `0x80016B20-0x80102750`, 15 ERZ method-2 chunks, inflated size `0xEBC30`, SHA-1 `903e3f47035a23886720289739fa78f2cd03f9a1` |
| Front-end overlays | 16 relocatable screens in the ROM tail `0xF0E6B6-0xF5DBDE` ([overlays](../../docs/internals/overlays.md)) |

Only the USA release is supported: it is the only dump we have.

## Build

Requirements:
- macOS or Linux
- `uv`
- GNU binutils for MIPS (`mips-linux-gnu-*` from Homebrew, or set `CROSS=mips64-elf-`)
- a C compiler
- git

```sh
make setup                                   # venv (splat64 0.50.0) + .deps/rnc_propack_source @499e812
make extract ROM_SRC=/path/to/thps3-usa.z64  # sha1 7b9438120c67214afaea09f4b106c54ef8f366c5
make                                         # build + verify (prints 3x OK)
make recomp N64RECOMP=/path/to/N64Recomp     # -> build/recomp/funcs, prints "warnings: 0"
make rsp RSPRECOMP=/path/to/RSPRecomp        # the audio microcode as C++
make recomp-ovl N64RECOMP=...                # main + the 16 front-end overlays as relocatable sections
make recomp-check                            # static completeness checks
```

`make extract` checks the ROM's SHA-1, inflates the main image into `baserom.main.bin` (15 ERZ chunks), runs splat on both
configs, and fixes up the asm. Regenerate the splat configs with `python3 -I ../common/gen_splat_cfg.py --game thps3 ROM config`.

## Status

| Target | Result |
|---|---|
| Main image, ROM, and ROM with the recompressed main image | **byte-identical** (`checksums/`; `make` prints 3x OK) |
| ERZ recompression of every compressed chunk in the ROM | 1,120 identical, 15 stored raw, 1 known quirk, 0 mismatches (`decomp/common/repack_check.py`) |
| Function list (boot + main) | 3,394 functions (253 boot, 3,141 main), `recomp/thps3.syms.toml` |
| Named functions | boot 233/253; main 220/3,141 (82 `_maybe`) |
| N64Recomp (`ffb39cd`) | **0 warnings**; 9 coprocessor-2 words patched to no-ops; the audio microcode is byte-identical to THPS2's |
| Main plus the 16 overlays through N64Recomp | 3,937 functions, 0 warnings |
| Matching C | none |

## Layout

```
config/thps3.{boot,main}.yaml   generated splat configs (offsets only)
symbols/{boot,main}.txt         names (splat symbol_addrs format)
recomp/                         N64Recomp and RSPRecomp configs, generated syms.toml (addresses only), runtime_stubs.txt
recomp-host/                    the native host (README inside)
../common/                      shared per-game tools, games.toml, host_force/thps3.toml
```

Documentation: [recomp](../../docs/internals/recomp.md), [versions](../../docs/internals/versions.md),
[overlays](../../docs/internals/overlays.md), [symbols](../../docs/internals/symbols.md), the data policy in
[game-facts](../../docs/game-facts/README.md).

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. See the top-level README.
