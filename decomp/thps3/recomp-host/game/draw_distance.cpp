// THPS3's side of the extended draw distance. The engine is shared with THPS2 and lives in the Host (src/draw_distance_thps23.cpp, with
// the notes); this file holds what is THPS3's own: the profile (offsets and sizes of the renderer's lists, the bigger vertex pools and the
// callbacks below), the zone ownership profile, and the hooks that need THPS3's symbols.
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <vector>

#include "draw_distance_thps23.h"
#include "guest_mem.h"
#include "host.h"
#include "recomp.h"
#include "thps_hooks.h"
#include "versions.h"
#include "zone_ownership.h"

namespace {

using thps::mem::f32;
using thps::mem::max_into;
using thps::mem::word;

constexpr uint32_t kDeferEntries = 64;
std::atomic<uint32_t> g_defer_hw{0};   // most put-aside items one frame had since the last gfx task (game thread writes, gfx thread takes)

// The profile's after_run: an extra run's pass has just ended and the next begun. The items the run put aside (World_DrawItems fills the
// list, gDeferredItemCount) get a pass of their own, as the frame does after the item pass (0x800325DC..0x800325F4).
void after_run(uint8_t* rdram, recomp_context* ctx, uint64_t a0, uint32_t renderer, thps::dd::HookTimer& timer, std::vector<uint32_t>* pass_log) {
    const auto& sy = thps::sym();
    if (word(rdram, sy.gDeferredItemCount)) {
        if (pass_log) pass_log->push_back(0xDEF00000u | (word(rdram, sy.gDeferredItemCount) & 0xFFFFFu));   // tests: this flush and its count
        ctx->r4 = a0;
        timer.guest([&] { thps::call_guest(sy.World_DrawDeferredItems, rdram, ctx); });
        ctx->r4 = int32_t(renderer);   // sign-extended, as the recompiled code keeps addresses
        timer.guest([&] { thps::call_guest(sy.Mesh_PassEnd, rdram, ctx); });
        ctx->r4 = int32_t(renderer);   // sign-extended, as the recompiled code keeps addresses
        timer.guest([&] { thps::call_guest(sy.Mesh_PassBegin, rdram, ctx); });
    }
}

// The profile's measure: the put-aside list's use goes into the gfx task's BufferUse.
void measure(thps::dd::BufferUse& u) { u.defer_used = g_defer_hw.exchange(0), u.defer_cap = kDeferEntries; }

}  // namespace

// The renderer's mesh queue: 845 entries (+0x1CC, count +0x369C) and the depth-sorted list of translucent meshes: 96 entries (+0x36A8,
// count +0x3FA8); the batch flag is +0x3FB0. The vertex pools are enlarged like the matrix pools.
const thps::dd23::Profile& thps::dd23::profile() {
    static const Profile p{0x369C, 845, 0x3FA8, 96, 0x3FB0, true, after_run, measure};
    return p;
}

// Zone ownership (src/zone_ownership.h): the box command shows on 1.
const thps::zones::Profile& thps::zones::profile() {
    static const Profile p{false, 0x40, 0x34};
    return p;
}

// World_DrawDeferredItems(a0 = item list) entry, game thread: the list World_DrawItems filled this frame.
extern "C" void thps_world_draw_deferred(uint8_t* rdram, recomp_context* ctx) {
    (void)ctx;
    max_into(g_defer_hw, word(rdram, thps::sym().gDeferredItemCount));   // not clamped: more than 64 would be the game's own overrun
}

// Scene objects have a second distance policy after the view's sphere test: the model renderer
// compares squared distance / gModelDistanceScale with its model-entry thresholds. Extending the
// projection alone leaves these objects fading out at their original range (750 units for the
// recorded scenery). Scale that shared policy for this render pass, using the governor's factor.
// No visibility flags or model tables change; the original byte/mesh-mask gates still run. The
// borrowed global is restored before returning, so simulation and other model callers retain it.
extern "C" int thps_scene_objects_draw(uint8_t* rdram, recomp_context* ctx) {
    thread_local bool inside = false;
    const float factor = thps::dd::factor();
    const bool dg = thps::dd::digest::on();   // tests: the decision digest (draw_distance.h); the nested call of our own guest call is not a decision
    const auto& sy = thps::sym();
    // tests: the 'O' record: the factor, the scale word before and as extended, whether the hook took the call, and whether the word was put back
    auto record_o = [&](uint32_t original_bits, uint32_t extended_bits, bool took, bool restored, const char* why) {
        thps::dd::digest::Hash h;
        h.f(factor), h.u(original_bits), h.u(extended_bits), h.u(took), h.u(restored);
        char d[96];
        std::snprintf(d, sizeof d, "%s factor=%.3f restored=%d", why, double(factor), restored);
        thps::dd::digest::record('O', 0, h, d);
    };
    if (inside || !(factor > 1.0f)) {   // Original and a complete governor back-off
        if (dg && !inside) record_o(word(rdram, sy.gModelDistanceScale), 0, false, true, "left (factor)");
        return 0;
    }
    const float original = f32(rdram, sy.gModelDistanceScale);
    const float extended = original * factor * factor;   // thresholds compare squared distance
    if (!(original > 0.0f) || !std::isfinite(extended)) {
        if (dg) record_o(word(rdram, sy.gModelDistanceScale), 0, false, true, "left (scale)");
        return 0;
    }
    auto* scale_word = reinterpret_cast<uint32_t*>(rdram + (sy.gModelDistanceScale & 0x3FFFFFC));
    const uint32_t original_bits = *scale_word;
    uint32_t extended_bits;
    std::memcpy(&extended_bits, &extended, sizeof(extended_bits));
    {   // its own block: the Restore below has run when the digest checks the word
        struct Restore {
            uint32_t* word;
            uint32_t original;
            bool& inside;
            ~Restore() { *word = original; inside = false; }
        } restore{scale_word, *scale_word, inside};
        std::memcpy(scale_word, &extended, sizeof(extended));
        inside = true;
        thps::dd::HookTimer timer;
        timer.guest([&] { thps::call_guest(sy.SceneObjects_Draw, rdram, ctx); });
    }
    if (dg) record_o(original_bits, extended_bits, true, *scale_word == original_bits, "took");
    return 1;
}
