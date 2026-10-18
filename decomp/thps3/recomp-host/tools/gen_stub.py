"""THPS3 wrapper: tools/gen_stub.py is shared by the THPS recomp hosts (decomp/common/host/tools/gen_stub.py); this runs it for THPS3."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # recomp-host: host_root.py
import host_root  # noqa: E402,F401  (puts the shared host's tools on sys.path: decomp/common here, host/ in a game repository)
import hostenv  # noqa: E402

if __name__ == "__main__":   # (not when imported, e.g. `import run` from a test step)
    hostenv.run_shared(__file__)
