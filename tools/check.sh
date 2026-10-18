#!/bin/sh
# The checks of this repository, in one command. The script itself lives in THPS64Host (host/tools/check.sh), so the four
# repositories share it.
#   tools/check.sh                no ROM needed: the checks CI runs on a pull request. Ends with "Ready for a PR."
#   tools/check.sh --maintainer   maintainers: adds the ROM-based steps (needs your dumps)
#   tools/check.sh --help
# Windows: run it in Git Bash.
ROOT=$(cd "$(dirname "$0")/.." && pwd)
if [ -f "$ROOT/host/tools/check.sh" ]; then S=$ROOT/host/tools/check.sh                       # THPS64Host
else S=${THPS_HOST_ROOT:-$ROOT/decomp/common}/host/tools/check.sh; fi                          # a game: the host submodule
[ -f "$S" ] || { echo "The shared host (THPS64Host) is missing. Fix: git submodule update --init --recursive" >&2; exit 2; }
CHECK_REPO=$ROOT exec sh "$S" "$@"
