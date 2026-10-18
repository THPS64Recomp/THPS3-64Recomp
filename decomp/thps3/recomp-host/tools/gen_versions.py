"""Version tables for the THPS3 recomp host (docs: docs/internals/versions.md; design: docs/internals/versions.md).

The generator is decomp/common/gen_versions.py (shared by the hosts); this wrapper gives it THPS3's profile (game/game.toml).
Commands (see that file): check | header OUT.h | config CLASS OUTDIR | namespace CLASS FUNCS_DIR OUT.h | rsp-config CLASS OUT.toml BLOB CPP |
list | class-info CLASS | classes

usage: python3 -I tools/gen_versions.py <command> [args]
"""
import os
import sys

HOST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # recomp-host
sys.path.insert(0, HOST)
import host_root  # noqa: E402  (the shared host tree: decomp/common here, host/ in a game repository)
sys.path.insert(0, host_root.ROOT)
import gen_versions  # noqa: E402  (decomp/common/gen_versions.py)

if __name__ == "__main__":
    gen_versions.main(sys.argv[1:], gen_versions.Profile(HOST))
