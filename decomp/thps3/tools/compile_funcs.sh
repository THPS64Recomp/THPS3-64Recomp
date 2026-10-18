#!/bin/sh
# Compile the N64Recomp output (build/recomp/funcs/funcs_*.c) as a library, no link. Proves the C is
# well-formed against N64ModernRuntime's recomp.h. Needs NMR's include dir (INC) and clang.
#   usage: INC=/path/to/N64ModernRuntime/N64Recomp/include tools/compile_funcs.sh [jobs]
# recomp/runtime_stubs.txt lists the *_recomp functions the game calls that neither N64Recomp
# nor NMR declare (libultra internals N64Recomp ignores): the host must provide them (THPS1:
# recomp-host/src/ultra_stubs.cpp). They are declared here with a generated header.
set -e
cd "$(dirname "$0")/.."
: "${INC:?set INC to N64ModernRuntime/N64Recomp/include}"
FUNCS=${FUNCS:-build/recomp/funcs}      # FUNCS=build/recomp/ovl_funcs OUT=build/recomp/ovl_obj for the overlay variant
OUT=${OUT:-build/recomp/obj}; mkdir -p "$OUT"
( echo '#include "recomp.h"'; sed 's/.*/void &(uint8_t* rdram, recomp_context* ctx);/' recomp/runtime_stubs.txt ) > "$OUT/extern_decls.h"
export OUT INC FUNCS
ls "$FUNCS"/funcs_*.c | xargs -P "${1:-6}" -n 1 sh -c '
  b=$(basename "$0" .c)
  clang -O0 -c -w -include "$OUT/extern_decls.h" -I"$INC" -I"$FUNCS" "$0" -o "$OUT/$b.o" || echo "FAIL $0"'
echo "objects: $(ls $OUT/*.o | wc -l)"
