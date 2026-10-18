# Contributing

Bug reports, play-testing notes and pull requests are all welcome. This page says where each one goes and what we need.

## Bugs and questions

- **Bugs:** use the [bug report form](https://github.com/THPS64Recomp/THPS3-64Recomp/issues/new/choose). It asks for the game release, the app version, your
  system, your settings, whether a cheat was on, and `crash.log` after a crash. [docs/TESTING.md](docs/TESTING.md) explains
  where to find each of these.
- **Questions, ideas and play-testing notes:** [Discussions](https://github.com/THPS64Recomp/THPS3-64Recomp/discussions).
- **Bugs in N64Recomp, N64ModernRuntime or RT64** that you find through this project: report them here first. We check
  them against our patches and, if they're upstream bugs, a maintainer reports them upstream with a small repro.

## Code changes

- **THPS3 only** (its symbols, hooks, game profile, tests, docs): a pull request to this repository.
- **The shared host** (anything in the submodule at `decomp/common`, whose host sources are in `decomp/common/host/`: the
  engine, the runtime glue, the patches, the test harness): a pull request to [THPS64Host](https://github.com/THPS64Recomp/THPS64Host). Don't edit the submodule from here. Once the host change is tagged,
  each game moves its submodule to the new tag.

Each pull request should:
- say what it changes and why, and how you tested it;
- add or update a test when it fixes a bug the suite could catch;
- add a line under `## [Unreleased]` in [CHANGELOG.md](CHANGELOG.md);
- update the docs it affects.

Before you open it, you can run `tools/check.sh`. It needs no ROM, runs the same checks as CI, and ends with
"Ready for a PR." If you have your own dump, please also run the tests for the area you changed
([BUILDING.md](BUILDING.md#tests)) and say which ones passed.

## What happens to your PR

1. CI builds it on Linux, Windows and macOS without a ROM, and checks the host pin. A failure says what to fix.
2. A maintainer reviews it.
3. A maintainer runs the full game test suite locally before merging. It needs the game, which CI can't have. You don't
   need to.
4. It's merged and listed in the CHANGELOG for the next release.

How the checks and releases work, for the curious: [MAINTAINING.md](https://github.com/THPS64Recomp/THPS64Host/blob/main/MAINTAINING.md) in THPS64Host.

## AI-assisted and hand-written contributions

Both are welcome, and we review every change the same way. Please:
- say how the change was made (by hand, or with which tool), in the pull request description;
- include tests, or say which tests you ran;
- read and understand what you submit. You're responsible for it, however it was written.

**Don't forward our patches, or AI-written changes, to the upstream projects.** N64Recomp, N64ModernRuntime and RT64 don't
accept contributions written with LLMs. We carry our changes as patch files in [THPS64Host](https://github.com/THPS64Recomp/THPS64Host) instead.

## What never goes in the repository

- ROMs, or any bytes copied from one;
- anything extracted or generated from the game: the code image, assembly, the generated C, the built game library, assets,
  textures, audio, or test reference pictures;
- copied game text beyond a short name, and screenshots or recordings of the game's art or music.

Addresses, data layouts, algorithms and names are fine, in your own words. Pull requests that contain game data are closed
and the data removed.

## Licence

This project is GPL-3.0-only ([LICENSE](LICENSE)). By contributing, you agree that your contribution is licensed the same
way.
