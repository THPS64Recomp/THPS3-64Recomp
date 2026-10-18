# THPS3 front-end overlays

The menu screens of Tony Hawk's Pro Skater 3 are not in the main image. Each is a small relocatable MIPS program stored in the ROM
tail after the asset tree (`0xF0E6B6-0xF5DBDE`), with a relocation stream, loaded on demand by the game. The mechanism is the same
as THPS2's. This page records the format, the loader, and how the port translates and runs them. Facts only: addresses, sizes, names.
Labels: **[V]** verified by `decomp/common/overlay_table.py` and `overlay_relocs.py`, **[I]** inference.

## The 16 screens [V]

The table in main `.data` at `0x800F01C0` has 16 records of 28 bytes: `t3_mainmenu`, `t2_loadcareer`, `t2_equipsel`, `t2_buystatsmenu`,
`t2_tricked`, `t2_ingamesave`, `t2_options`, `t2_frontload`, `t2_displevelgoals`, `t2_createsktr`, `t2_2phandicap`, `t2_2playergamemenu`,
`t2_intro`, `t2_levelselect`, `t2_playerselmenu` and `edmod` (the park editor: a third of the overlay code, with 864 internal calls).
THPS2 has the same list with `t2_menuwheel` in place of `t3_mainmenu`.

A record is: name pointer, code ROM address and size, relocation-stream ROM address and size, and two zero words (cache-operation
ranges, zero in all 16). Totals: code blobs `0x4484C` bytes, relocation streams `0xACDC` bytes, together `0x4F528` bytes: the whole tail.
ROM addresses in the table are *link-time* ones, relative to `0xB00FF7A0` (the asset root when the tail was linked); the real ROM
offset is the value minus `0xB0083D6A`. The loader computes the same from the asset-root word that boot copies to `0x80011C7C`. [V]

## The loader [V]

| Role | THPS3 address | Notes |
|---|---|---|
| `Overlay_Load(name)` | `0x8009AAE0` | compares the name with the 16 table names, hashes it (CRC-32), skips a screen that is already loaded, else DMAs the blob and its stream, relocates, calls blob offset 0 |
| `Overlay_Reloc(base, stream)` | `0x8009AD20` | applies the relocation stream |
| `Overlay_Call(name, cmd, a, b)` | `0x8009AE54` | finds the loaded screen by hash and calls slot `cmd` of its descriptor; this is how a screen runs each frame |
| `Overlay_UnloadByHash` / `Overlay_Unload` | `0x8009AEE0` / `0x8009AFAC` | call the destructor slot, free the blob and descriptor, unlink |
| `Overlay_RomAddr(addr)` | `0x8009B070` | link-time ROM address to real ROM address |
| loaded list head | `0x800F0380` | doubly linked; a descriptor is `0x34` bytes (destructor, blob, name hash, method slots from `+0xC`, next, previous) |

Small stubs in the main image (`0x8002B760-0x8002E4A8`) load a screen by name: four small functions per screen (load; call with command
1, 3, 4 or 5; unload). The blob starts with an init function that stores the screen's methods into the descriptor, then the code;
strings and tables follow the code. **The load address is not fixed** (the heap moves), so a flat recompile at one address cannot work.

## The relocation stream [V]

Big-endian 32-bit words until `0xFFFFFFFF`; `type = word & 3`, `site = word & ~3` (a byte offset into the blob). Type 0 is a 32-bit
pointer (`+= base`), type 1 the high half of an address (with an addend word), type 2 the low half (with an addend word), type 3 a
26-bit jump (`+= (base & 0x0FFFFFFF) >> 2`). Every relocation targets the blob itself. The high and low halves are not adjacent in
general, because each carries its own addend. Absolute `jal`s into the main image are *not* relocated: all 334 distinct targets
(330 in main, 4 in boot) are function starts in `recomp/thps3.syms.toml`. About 87 main functions are reached from the overlays only.

## How the port runs them

N64Recomp's relocatable-section model has exactly these four relocation types. `decomp/common/overlay_recomp.py` (and
`overlay_syms.py`) writes one section per screen, pre-links the blobs at fake bases, and appends them to the code blob: main plus
overlays make **3,937 functions** (543 of them in the overlays; `edmod` 213, `t2_options` 62, `t2_createsktr` 57, `t2_equipsel` 31,
`t2_tricked` 30, ...) with 0 warnings. At run time the game's own loader relocates the words in RDRAM and the host's PI-DMA hook calls
`load_overlays(blob_offset, destination, size)` for the read that starts a blob. Overlay functions are named `ovl_<screen>_<offset>`;
the overlay area starts at ROM `0xF00000` for the hook, and `src/overlay_table.inc` holds the numbers (offsets and names only).
The mechanism and its findings are described in more detail for THPS2 in its repository's `docs/internals/overlays.md`: relocation lists must be
sorted by address, and section registration needs the total section count.

## At first run (the split build)

The downloaded app has no Python, so the half of `overlay_recomp.py` that reads the ROM is C++: `decomp/common/firstrun/overlay_rom.cpp`.
It takes the **recipe** (`recomp-host/recipes/<class>/overlays.txt`: screen names, ROM offsets and sizes of each blob and relocation stream,
the function map, and an XXH3-64 fingerprint of the ROM range they cover; no ROM bytes) and your ROM, checks the fingerprint (a modified dump is
refused with a message), then makes the same three things the Python tool makes: the code blob with the pre-linked overlays appended, the
`[[section]]` symbol text and the overlay table. The output is byte-identical to the static build's input; `decomp/common/firstrun/test_overlay_rom.py`
checks that, and that the recipes contain no ROM bytes. The N64Recomp and RSPRecomp configs are generated at package time from the committed
version tables, so they are not part of the recipe.

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived
from analysis of a retail cartridge dump. No game data is reproduced beyond names, addresses and individual values. See the README.
