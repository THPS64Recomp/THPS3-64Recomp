// THPS3's cheats (test aids; the shared part, cheats.cfg and the menu: common/host/src/cheats.cpp).
//
// Unlock All Levels (--unlock-levels): the shared hook on Level_IsSelectable (common/host/src/hooks.cpp, config/thps3.hooks.toml) answers
// "available" for levels 0-9; the career data is not touched, so nothing of it reaches the save.
//
// The others are the game's own cheats. THPS3 asks "is cheat N on?" in one place, Cheat_IsOn(N) (USA 0x8005900C), which returns
// the on byte of cheat N (game state +0x130E + 4 * N). The hook answers 1 for the cheats the host has on and leaves the rest to the
// game; no game memory is written, so nothing can reach the Controller Pak save, and the game's own cheat menu is not involved.
// Indices (from the game's cheat-name switch, func_80058858): 1 Skip To Restart, 3 Perfect Balance, 4 Always Special, 8 Slow-Nic.
//   Perfect Balance: the rail balance (lean) is held at 0 (DoOnRail).
//   Always Special: the special meter counts as full (asked by the stat helper and the special-trick code; not checked by eye).
//   Slow-Nic (shown as Slow Motion): the frame update divides the step (gTimeScale) by 4 when one of two skater flags is set (which
//   states those are was not traced; in the test run the step was 64 on some frames even with the skater standing).
//   Skip To Restart: the pause menu's restart-point entry.
// All of them are read where they are used, every frame: they take effect at once.
#include <atomic>
#include <string>

#include "recomp.h"
#include "host.h"
#include "thps_hooks.h"

namespace {
constexpr int kIndex[thps::cheats::kCount] = {-1, 3, 8, 1, 4};   // UnlockLevels (no game cheat), PerfectBalance, SlowMotion, SkipToRestart, AlwaysSpecial
std::atomic<uint64_t> g_yes[thps::cheats::kCount];   // how often the hook answered "on" per cheat (control "cheat": tests)
}

bool thps::cheats::game_has(Id) { return true; }

std::string thps::cheats::game_stats() {
    std::string s;
    for (int i = 0; i < kCount; i++)
        if (kIndex[i] >= 0) s += std::string(s.empty() ? "" : ",") + info(Id(i)).key + ":" + std::to_string(g_yes[i].load());
    return s;
}

const char* thps::cheats::game_note(Id id) {
    switch (id) {
        case UnlockLevels: return "Every level can be picked in the level select (career, free skate, single session). Takes effect at once.";
        case PerfectBalance: return "Grinds never lose balance (the game's own cheat). Takes effect at once.";
        case SlowMotion: return "The game's own Slow-Nic cheat: quarter-speed physics in the skater states the game picks for it. Takes effect at once.";
        case SkipToRestart: return "The pause menu gets the game's Skip To Restart entry: jump to any start point of the level. Takes effect the next time you pause.";
        case AlwaysSpecial: return "The special meter is always full (the game's own cheat). Takes effect at once.";
        default: return "";
    }
}

void thps::cheats::game_tick(uint8_t*) {}

extern "C" int thps_cheat_is_on(uint8_t*, recomp_context* ctx) {
    const int n = int(ctx->r4);
    for (int i = 0; i < thps::cheats::kCount; i++)
        if (kIndex[i] >= 0 && kIndex[i] == n && thps::cheats::on(thps::cheats::Id(i))) {
            g_yes[i]++;
            return 1;
        }
    return 0;
}
