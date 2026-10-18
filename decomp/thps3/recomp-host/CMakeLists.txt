cmake_minimum_required(VERSION 3.20)

# THPS3 (N64) recomp host. The host itself is shared by THPS1-3 (decomp/common/host, ADR 0006): this file only names the game
# and includes the shared CMake file. The game profile is game/game.toml (names, flags) and game/; the version tables are
# versions/ and decomp/common/games.toml. Build instructions and options: ../../common/host/cmake/thps_host.cmake and README.md.
project(THPS3Recomp C CXX)
set(THPS_FAMILY thps3)
set(THPS_SKIP_INTRO overlay)   # the legal screen is the front-end overlay t2_intro: the shared skip_intro_overlay.cpp
# The shared host tree (THPS64Host): decomp/common (a directory in the development tree, the submodule in a game repository);
# -DTHPS_HOST_ROOT or $THPS_HOST_ROOT override it with another THPS64Host checkout.
if (NOT THPS_HOST_ROOT AND DEFINED ENV{THPS_HOST_ROOT})
    set(THPS_HOST_ROOT "$ENV{THPS_HOST_ROOT}")
endif()
if (NOT THPS_HOST_ROOT)
    get_filename_component(THPS_HOST_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../common" ABSOLUTE)
endif()
set(THPS_HOST_ROOT "${THPS_HOST_ROOT}" CACHE PATH "The shared host tree (THPS64Host; default decomp/common)")
if (NOT EXISTS "${THPS_HOST_ROOT}/host/cmake/thps_host.cmake")
    message(FATAL_ERROR "The shared host (THPS64Host) was not found: run `git submodule update --init`, or pass -DTHPS_HOST_ROOT=<a THPS64Host checkout>")
endif()
include("${THPS_HOST_ROOT}/host/cmake/thps_host.cmake")
