#!/bin/sh
# Wrapper: the suite runner is shared by the THPS recomp hosts (decomp/common/host/tools/test.sh); same options.
THPS_HOST=$(cd "$(dirname "$0")/.." && pwd)
export THPS_HOST
# The shared host tree: $THPS_HOST_ROOT (an override), else decomp/common (a directory here, the THPS64Host submodule in a game repository).
if [ -z "${THPS_HOST_ROOT:-}" ] && [ -f "$THPS_HOST/../../common/host/tools/hostenv.py" ]; then THPS_HOST_ROOT=$(cd "$THPS_HOST/../../common" && pwd); fi
[ -f "${THPS_HOST_ROOT:-}/host/tools/hostenv.py" ] || { echo "the shared host (THPS64Host) was not found: git submodule update --init, or set THPS_HOST_ROOT" >&2; exit 2; }
export THPS_HOST_ROOT
exec sh "$THPS_HOST_ROOT/host/tools/test.sh" "$@"
