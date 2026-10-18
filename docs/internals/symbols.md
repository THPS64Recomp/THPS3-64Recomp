# THPS3 symbols: coverage, sources and evidence

How the function and data names in `decomp/thps3/symbols/{boot,main}.txt` came about, how much is named, and how far to trust each
name. Names are identifiers only; no code from any reference project is used.

## Coverage

| Segment | Named | How |
|---|---|---|
| Boot segment (libultra, IDO) | 233 of 253 | n64sym's built-in signatures; the loader functions are THPS2's addresses |
| Main image | 220 of 3,141 (82 with a `_maybe` suffix) | n64sym hits, body matching against THPS2 and THPS1, hand identification |
| Function bounds | all 3,394 set | `recomp/thps3.syms.toml`, checked by `make recomp-check` |

Body matching from THPS2 reached 2,431 of the 3,141 main functions (77 %). A matched function inherits THPS2's name, and THPS2 had
names for only 214 of its own, so the count of names stays low while the *structure* (translation-unit order, vtables, jump
tables) carries over for free. The 703 unmatched functions (62 KB, mostly small) are the code that is new or changed in THPS3.
By category the named main functions are skater and tricks 53, camera 12, loading and assets 30, audio libraries 31 and other 94.

## Where the names come from

<!-- table-ok: the name sources in priority order -->
| Tag in `symbols/*.txt` | Source | Count | Trust |
|---|---|---|---|
| `loader` | Edge of Reality loader (`Boot_*`, `Erz_*`), THPS2's addresses | 6 | high |
| `manual` | read in the disassembly: `Trick_Land`, `Trick_Bail`, `DoPhysics`, `Pi_DmaThread`, `osAiGetStatus`, `GGame`, the overlay loader | 13 (+3 data symbols) | medium-high |
| `n64sym` | shygoo's n64sym built-in signatures (libultra IDO in boot; libmus, n_audio, libgcc in main) | 288 | high (exact bytes) |
| `sigmatch-A` | masked body unique in THPS2 (or THPS1) and one hit in THPS3 | 168 | high (2,123 of 2,123 agree with the function-list starts, 2,122 sizes) |
| `sigmatch-O` | identical bodies resolved by link order | 14 | medium |
| `sigmatch-C` / `sigmatch-F` | callee of a matched function / fuzzy match; both get `_maybe` | 8 / 4 | low |

No code from any reference project is used, and no leaked source code was used.

## Suspect names inherited from THPS2 and THPS1

- `n_alSynRemovePlayer_800CFB34` at `0x800D47A4` (0x258 bytes) is a body-matched copy of an n64sym name, but it has 36 call sites in
  the front-end overlays; an audio-synth player-removal function is implausible there. Treat it as a false n64sym hit (a generic
  helper). The 8-byte `n_alSynRemovePlayer` at `0x800295E0` is a tiny-body coincidence as well.
- `_maybe` names and fuzzy-match names keep the *source's* size; the real size is the function list's (for example `Trick_Land` is
  `0x40C` bytes, not `0x354`).

## Jump tables and vtables

- 75 non-`$ra` `jr` in `.text`; N64Recomp turned 71 into `switch` statements; 65 are reached through jump tables.
- 122 GCC 2.x vtables (the same count as THPS2), 264 virtual call sites, 132 translation units. Class names do not transfer from THPS1.

## Still unnamed

The trick-handling family (`HandleTricksNew`, `Trick_TakeOff`, `Trick_Trick`, the rail-grind start, manuals, specials) is unnamed.
Anchors: `Trick_Land` `0x800805AC`, `Trick_Bail` `0x800809B8`, `DoPhysics` `0x80092160`, `GGame` `0x800ED588`, and the physics unit around
`0x8007DF1C-0x80095A04`. Physics functions that changed from THPS2 (where new behaviour such as reverts must live): `0x80069124`
(`0x5804` bytes), `0x800882C8` (`0x1E6C` bytes), `0x8008D4BC`, `0x8008A824`, the camera's `ReactToCollision__7CCamera_maybe` `0x8004C780`
and an unmatched `0x212C`-byte function at `0x80063AB0`.

---
Unofficial. This project is not affiliated with Activision, Neversoft, Edge of Reality, Tony Hawk or Nintendo. Facts derived
from analysis of a retail cartridge dump. No game data is reproduced beyond names, addresses and individual values. See the README.
