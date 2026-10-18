"""Finds the shared host tree (THPS64Host) for this game's wrappers and puts its tools on sys.path.

The host tree is `decomp/common`: a directory in the private development tree, the THPS64Host submodule in a game
repository (same path in both). $THPS_HOST_ROOT overrides it (another THPS64Host checkout). The result is exported as
$THPS_HOST_ROOT, so child processes (cmake, the shell tools) use the same tree.
"""
import os
import sys

HOST = os.path.dirname(os.path.abspath(__file__))                         # decomp/thps<N>/recomp-host
_MARK = os.path.join("host", "tools", "hostenv.py")


def find():
    env = os.environ.get("THPS_HOST_ROOT")
    c = env or os.path.join(HOST, "..", "..", "common")
    if os.path.isfile(os.path.join(c, _MARK)):
        return os.path.abspath(c)
    if env:
        sys.exit(f"THPS_HOST_ROOT={env} is not a THPS64Host tree (no {_MARK})")
    sys.exit("the shared host (THPS64Host) was not found: in a game repository run `git submodule update --init`, "
             "or set THPS_HOST_ROOT to a THPS64Host checkout")


ROOT = find()
TOOLS = os.path.join(ROOT, "host", "tools")
os.environ["THPS_HOST_ROOT"] = ROOT
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
