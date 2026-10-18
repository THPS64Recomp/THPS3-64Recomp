# THPS3 (N64, U) decomp - asm round-trip build.
#
#   make setup      venv with pinned splat (once)
#   make extract    baserom.z64 -> baserom.main.bin, splat both configs
#   make            build main image + boot + ROM, then verify checksums
#   make check      checksums only
#   make boot-test  headless mupen64plus screenshots of the built ROM
#
# Nothing produced here (baserom*, asm/, assets/, build/, linker_scripts/) may
# be committed: it is all derived from the user's ROM.

# Path to your own dump (z64, big-endian). Only needed once: it is copied to
# baserom.z64. Example: make extract ROM_SRC=/path/to/thps3.z64
ROM_SRC     ?= baserom.z64
PY          := .venv/bin/python
COMMON      := ../common
GAME        := thps3
CROSS       ?= mips-linux-gnu-
AS          := $(CROSS)as
LD          := $(CROSS)ld
OBJCOPY     := $(CROSS)objcopy
ASFLAGS     := -EB -march=vr4300 -mabi=32 -G 0 -I include -I asm --no-pad-sections
LDFLAGS     := -EB --no-check-sections --accept-unknown-input-arch -nostdlib

BUILD       := build
MAIN_BIN    := $(BUILD)/thps3.main.bin
BOOT_BIN    := $(BUILD)/thps3.boot.bin
ROM         := $(BUILD)/thps3.z64
ROM_RNC     := $(BUILD)/thps3.recompressed.z64

MAIN_S      := $(shell find asm/main -name '*.s' 2>/dev/null)
MAIN_O      := $(MAIN_S:%.s=$(BUILD)/%.o)
BOOT_S      := $(shell find asm/boot -name '*.s' 2>/dev/null)
BOOT_O      := $(BOOT_S:%.s=$(BUILD)/%.o)
BIN_O       := $(patsubst %.bin,$(BUILD)/%.o,$(shell find assets/boot -name '*.bin' 2>/dev/null))

.PHONY: all setup extract check clean distclean boot-test recompress recomp-inputs recomp

all: $(ROM) $(ROM_RNC) check

setup: deps
	uv venv .venv -p 3.12
	uv pip install --python $(PY) -r requirements.txt

RNC_COMMIT := 499e8128f9a3890cb4d287a11608b3ae1e0df440
deps:
	@test -d .deps/rnc_propack_source || git clone -q https://github.com/lab313ru/rnc_propack_source .deps/rnc_propack_source
	git -C .deps/rnc_propack_source checkout -q $(RNC_COMMIT)

baserom.z64:
	@test -f "$(ROM_SRC)" || (echo "Put your THPS3 (U) v1.1 z64 at baserom.z64 or pass ROM_SRC=..."; false)
	cp "$(ROM_SRC)" $@

extract: baserom.z64
	shasum -c checksums/input.rom.sha1
	$(PY) -I $(COMMON)/thps_unpack.py --game $(GAME) baserom.z64 baserom.main.bin
	shasum -c checksums/input.main.sha1
	rm -rf asm assets linker_scripts
	mkdir -p linker_scripts
	$(PY) -m splat split config/$(GAME).main.yaml
	$(PY) -m splat split config/$(GAME).boot.yaml
	$(PY) -I $(COMMON)/fix_asm.py --game $(GAME) $$(find asm -name '*.s')

# ---------------------------------------------------------------- objects
$(BUILD)/%.o: %.s
	@mkdir -p $(dir $@)
	$(AS) $(ASFLAGS) -o $@ $<

$(BUILD)/assets/%.o: assets/%.bin
	@mkdir -p $(dir $@)
	$(LD) -EB -r -b binary -o $@ $<

# ---------------------------------------------------------------- main image
$(BUILD)/thps3_main.elf: $(MAIN_O) linker_scripts/thps3_main.ld
	$(LD) $(LDFLAGS) -T linker_scripts/thps3_main.ld \
	  -T linker_scripts/main_undefined_syms_auto.txt \
	  -T linker_scripts/main_undefined_funcs_auto.txt \
	  -Map $(BUILD)/thps3_main.map -o $@

$(MAIN_BIN): $(BUILD)/thps3_main.elf
	$(OBJCOPY) -O binary $< $@

# ---------------------------------------------------------------- boot + ROM
# The ROM link places header, IPL3, boot segment and every byte after the boot
# segment (chunk table, compressed main chunks, asset packs) from the splat
# config. The chunks are taken from the ROM as-is (bin) for this target.
$(BUILD)/thps3.elf: $(BOOT_O) $(BIN_O) linker_scripts/thps3.ld
	$(LD) $(LDFLAGS) -T linker_scripts/thps3.ld \
	  -T linker_scripts/boot_undefined_syms_auto.txt \
	  -T linker_scripts/boot_undefined_funcs_auto.txt \
	  -Map $(BUILD)/thps3.map -o $@

$(ROM): $(BUILD)/thps3.elf
	$(OBJCOPY) -O binary --gap-fill 0x00 $< $@

# ERZ packer: lab313ru/rnc_propack_source + our look-ahead patch.
# lab313ru/rnc_propack_source checkout (make deps clones it into .deps/)
RNC_SRC     ?= .deps/rnc_propack_source
RNC         := $(BUILD)/tools/rnc_propack
$(RNC): $(COMMON)/rnc_propack/lookahead.patch
	@mkdir -p $(BUILD)/tools/rnc_src
	cp $(RNC_SRC)/main.c $(BUILD)/tools/rnc_src/main.c
	patch -s -p1 -d $(BUILD)/tools/rnc_src < $(COMMON)/rnc_propack/lookahead.patch
	cc -O2 -o $@ $(BUILD)/tools/rnc_src/main.c

# Main image built from asm -> ERZ recompress -> spliced into the built ROM.
$(ROM_RNC): $(ROM) $(MAIN_BIN) $(RNC) $(COMMON)/erz_pack.py $(COMMON)/build_rom.py
	$(PY) -I $(COMMON)/build_rom.py --game $(GAME) $(RNC) $(ROM) $(MAIN_BIN) $@

recompress: $(ROM_RNC)

check: $(MAIN_BIN) $(ROM) $(ROM_RNC)
	@echo "--- main image (asm -> GNU as/ld) vs decompressed baserom image"
	shasum -c checksums/build.main.sha1
	@echo "--- ROM (boot asm + original compressed chunks) vs baserom"
	shasum -c checksums/build.rom.sha1
	@echo "--- ROM with main image recompressed by decomp/common/erz_pack.py"
	shasum -c checksums/build.rom_recompressed.sha1

boot-test: $(ROM_RNC)
	$(COMMON)/boot_test.sh $(ROM_RNC) $(BUILD)/boot-test

# ---------------------------------------------------------------- N64Recomp
# Function list -> recomp/thps3.syms.toml (committed: addresses/names only) and
# build/thps3.codeblob.bin (ROM-derived, local only). `make recomp` runs
# N64Recomp (set N64RECOMP=/path/to/N64Recomp) into build/recomp/funcs.
N64RECOMP ?= N64Recomp
recomp-inputs: baserom.main.bin
	$(PY) -I $(COMMON)/gen_syms.py --game $(GAME) baserom.z64 baserom.main.bin $(BUILD)/thps3.codeblob.bin recomp/thps3.syms.toml

recomp: recomp-inputs
	rm -rf $(BUILD)/recomp/funcs && mkdir -p $(BUILD)/recomp/funcs
	$(N64RECOMP) recomp/thps3.recomp.toml > $(BUILD)/recomp/log.txt 2>&1 || (tail -5 $(BUILD)/recomp/log.txt; false)
	@grep -c "" $(BUILD)/recomp/log.txt >/dev/null; tail -2 $(BUILD)/recomp/log.txt
	@echo "warnings: $$(grep -c '^\[Warn\]' $(BUILD)/recomp/log.txt)"

clean:
	rm -rf $(BUILD)

distclean: clean
	rm -rf asm assets linker_scripts include baserom.main.bin

# RSP audio microcode (n_aspMain) -> build/rsp/n_aspMain.cpp (set RSPRECOMP=/path/to/RSPRecomp)
RSPRECOMP ?= RSPRecomp
rsp: recomp-inputs
	@mkdir -p $(BUILD)/rsp
	$(RSPRECOMP) recomp/thps3.aspMain.toml

# Static completeness checks on the function list (no missing code, jr sites, hidden starts)
recomp-check: recomp-inputs
	$(PY) -I $(COMMON)/recomp_check.py --game $(GAME) recomp/thps3.syms.toml baserom.z64 baserom.main.bin

coverage:
	$(PY) -I $(COMMON)/coverage.py --game $(GAME)

# Compile the generated C as a library (INC=.../N64ModernRuntime/N64Recomp/include)
recomp-lib:
	tools/compile_funcs.sh

.PHONY: rsp recomp-check coverage recomp-lib

# Regenerate symbols/*.txt from n64sym + sigmatch (needs THPS1=... N64SYM=...); see tools/seed_all.sh
seed:
	tools/seed_all.sh
.PHONY: seed

# Front-end overlays as N64Recomp relocatable sections (decomp/common/overlay_syms.py): appends the 16 relocated blobs to
# a copy of the code blob, writes recomp/thps3.ovl.syms.toml (committed, addresses only) and recompiles main + overlays.
recomp-ovl: recomp-inputs baserom.main.bin
	$(PY) -I $(COMMON)/overlay_syms.py --game $(GAME) baserom.z64 baserom.main.bin $(BUILD)/thps3.codeblob.bin recomp/thps3.syms.toml $(BUILD)/thps3.ovl.codeblob.bin recomp/thps3.ovl.syms.toml
	rm -rf $(BUILD)/recomp/ovl_funcs && mkdir -p $(BUILD)/recomp/ovl_funcs
	$(N64RECOMP) recomp/thps3.ovl.recomp.toml > $(BUILD)/recomp/ovl_log.txt 2>&1 || (tail -5 $(BUILD)/recomp/ovl_log.txt; false)
	@grep "Function count" $(BUILD)/recomp/ovl_log.txt
	@echo "warnings: $$(grep -c '^\[Warn\]' $(BUILD)/recomp/ovl_log.txt)"
.PHONY: recomp-ovl
