// THPS3's side of the extended draw distance (the setting and governor: common/host/src/draw_distance.cpp; THPS1's and THPS2's
// sides, with the notes, are game/draw_distance.cpp in THPS1-64Recomp and THPS2-64Recomp).
//
// The same engine and the same layout as THPS2 (THPS2's game/draw_distance.cpp has the notes): gFarPlane (US 0x800E9D20)
// is written by the level-fog function (func_80022C0C, THPS2's func_80023CFC) and passed to View_SetFrustum by the gameplay camera;
// the display lists and the matrix and vertex pools sit in one block (US 0x80105C14..0x80105C60) laid out as in THPS2, with
// THPS2's allocators (matrices: 0x800BCC94, count 0x80105C40).
//
// The renderer's lists, as THPS2's at other offsets: the mesh queue, 845 entries (+0x1CC, count +0x369C; THPS2 has 512) and the
// depth-sorted list of translucent meshes, 96 entries (+0x36A8, count +0x3FA8), both filled between a pass's begin (0x800C98F0) and end
// (0x800C9910), dropped past their size, drawn and emptied by Mesh_QueueEmit. New in THPS3: World_DrawItems puts every item with a depth
// offset (item +0x48 != 0) on a list of 64 pointers (0x800EA3AC, count gDeferredItemCount just after it) and World_DrawDeferredItems draws
// them in a pass of their own. Nothing checks that list: a 65th item would be written over the count. The hooks note all three, read only.
#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <mutex>
#include <vector>

#include "draw_distance.h"
#include "recomp.h"
#include "thps_hooks.h"
#include "host.h"
#include "versions.h"

namespace {

uint32_t word(const uint8_t* rdram, uint32_t vaddr) { return *reinterpret_cast<const uint32_t*>(rdram + (vaddr & 0x3FFFFFC)); }
float f32(const uint8_t* rdram, uint32_t vaddr) {
    uint32_t w = word(rdram, vaddr);
    float f;
    std::memcpy(&f, &w, 4);
    return f;
}

constexpr uint32_t kQueueCount = 0x369C, kQueueEntries = 845, kSortCount = 0x3FA8, kSortEntries = 96, kDeferEntries = 64;
std::atomic<uint32_t> g_runs_hw{0}, g_queue_hw{0}, g_sort_hw{0}, g_defer_hw{0};   // most entries one pass used since the last gfx task (game thread writes, gfx thread takes)
void max_into(std::atomic<uint32_t>& a, uint32_t v) {
    uint32_t m = a.load();
    while (v > m && !a.compare_exchange_weak(m, v)) {}
}

}  // namespace

// Mesh_QueueEmit(a0 = renderer) entry, game thread: the pass's lists are complete here (its end has just flushed the last batch).
extern "C" void thps_mesh_queue_emit(uint8_t* rdram, recomp_context* ctx) {
    thps::dd::HookTimer timer;
    const uint32_t r = uint32_t(ctx->r4);
    if (r != word(rdram, thps::sym().gRenderer)) return;   // not the renderer this was written for
    max_into(g_queue_hw, std::min(word(rdram, r + kQueueCount), kQueueEntries));
    max_into(g_sort_hw, std::min(word(rdram, r + kSortCount), kSortEntries));
}

// World_DrawDeferredItems(a0 = item list) entry, game thread: the list World_DrawItems filled this frame.
extern "C" void thps_world_draw_deferred(uint8_t* rdram, recomp_context* ctx) {
    (void)ctx;
    max_into(g_defer_hw, word(rdram, thps::sym().gDeferredItemCount));   // not clamped: more than 64 would be the game's own overrun
}

// The world view. Besides the gameplay camera's own frustum calls (every frame), the camera code keeps a second view (0x800E0040 in US)
// for the world: func_80022710 sets its perspective only when gFarPlane differs from the copy it cached (gWorldFarCache), i.e. once per
// level. A factor chosen after the level loaded therefore never reached it (the first measurements of this game, made that way,
// showed "no change"; with the setting from start-up the Hangar start draws more). So when the factor in use changes, the cached copy
// is cleared, and the camera code sets the world view's perspective again in the next frame, through View_SetFrustum and this hook.
bool thps::dd::supported() { return true; }
namespace thps::dd { void dd_game_sync_pools(uint8_t* rdram); }   // the matrix pools' cap in force (below)

// As THPS1: a call is the gameplay camera's (or the world view's) when its far is gFarPlane, or the far returned last; the answer is
// gFarPlane x k (k = 1 gives the game's value back). Game thread only.
float thps::dd::dd_game_far(uint8_t* rdram, float f, float k_in_use) {
    // The far plane follows the setting (projection_factor: the setting, lowered only by a back-off), not the factor in use: the world view takes a
    // new far only when the camera code sets it (a course start, camera changes), and the factor in use is applied to the extra items
    // in thps_world_draw_items instead.
    (void)k_in_use;
    const float k = projection_factor();
    static float last_out = 0.0f, applied_k = 1.0f;
    const auto& s = thps::sym();
    if (k != applied_k) {
        applied_k = k;
        *reinterpret_cast<uint32_t*>(rdram + (s.gWorldFarCache & 0x3FFFFFC)) = 0;   // 0.0f: never a far plane, so the next frame refreshes the world view
    }
    dd_game_sync_pools(rdram);   // the matrix pools' cap in force follows the setting (below)
    const float game_far = f32(rdram, s.gFarPlane);
    if (!(game_far > 0.0f) || (f != game_far && f != last_out)) return f;
    note_game_far(game_far);
    const float out = std::min(game_far * k, std::max(game_far, kFullFarPlane));   // full mode: as far as kFullFarPlane
    last_out = out == game_far ? 0.0f : out;
    note_effective(out / game_far);
    return out;
}

// Display-list measurements, debug only (off in normal runs; read once at start-up). THPS_DD_DLPROBE=1: the bytes each part of a frame
// writes into the display list (gDlHead - the frame's buffer): before World_DrawItems, each extra pass (with its pass end and begin), the
// game's own pass, and the rest of the frame after the extra passes (the game's pass, the scenery, the moving objects, the HUD, the other
// player's view), per frame; `dd dlprobe [reset]` reports their medians, 99th percentiles and maxima. THPS_DD_CANARY=1: each display
// list the course set-up allocates gets kGuard bytes of a pattern after its end, checked at every gfx task (a changed word = an overrun
// past gDlBufSize; counted and logged once per list; the pattern is written only at the allocation, so a guard can never damage memory
// that has a new owner since).
namespace {
bool probe_on() { static const bool on = std::getenv("THPS_DD_DLPROBE") != nullptr; return on; }
bool canary_on() { static const bool on = std::getenv("THPS_DD_CANARY") != nullptr; return on; }
constexpr uint32_t kGuard = 64, kGuardWord = 0xDDC0FFEEu;
void fill_guard(uint8_t* rdram, uint32_t buf, uint32_t size) {
    for (uint32_t k = 0; k < kGuard; k += 4) *reinterpret_cast<uint32_t*>(rdram + ((buf + size + k) & 0x3FFFFFC)) = kGuardWord;
}
// Bytes the frame being built has written into its display list so far (three word reads).
uint32_t dl_used(const uint8_t* rdram) {
    const auto& s = thps::sym();
    const uint32_t buf = word(rdram, s.gDlBufs + 4 * (word(rdram, s.gDlFrame) & 1)), head = word(rdram, s.gDlHead);
    return head >= buf && head - buf < (64u << 20) ? head - buf : 0;
}
void probe_view(uint8_t* rdram, uint32_t player, uint32_t entry, uint32_t after_extras);
struct Samples {
    std::vector<uint32_t> v;
    void add(uint32_t x) { if (v.size() < 500000) v.push_back(x); }
    std::string str(const char* name) const {
        if (v.empty()) return std::string(" ") + name + "=-";
        std::vector<uint32_t> c = v;
        std::sort(c.begin(), c.end());
        char b[96];
        std::snprintf(b, sizeof b, " %s=%u/%u/%u(n%zu)", name, c[c.size() / 2], c[std::min(c.size() - 1, c.size() * 99 / 100)], c.back(), c.size());
        return b;
    }
};
struct ProbeFrame { uint32_t after_extras[2] = {}, extra_bytes[2] = {}; uint8_t views = 0; };
struct Probe {
    Samples entry, pass, per_item, own, rest_1p, rest_2p_v0, rest_2p_v1, total_1p, total_2p, extras_1p;
    uint32_t frames = 0, canary_bad = 0;
    ProbeFrame frame[2];   // per buffer: the game thread fills it while it builds that frame, the gfx thread takes it at the task
};
std::mutex g_probe_mutex;
Probe g_probe;
std::atomic<uint32_t> g_direct_calls{0};   // World_DrawItems calls for the course items outside a pass (drawn at once, not in passes)
std::atomic<uint32_t> g_dl_guarded[2] = {0, 0};   // THPS_DD_CANARY: the display lists that have a guard after them (their addresses)
std::atomic<uint32_t> g_dl_guard_at[2] = {0, 0};  //   and the size the guard follows (the front end's set-up reuses the addresses with 72 KiB lists)
}  // namespace

namespace {
// THPS_DD_DLPROBE, game thread: one World_DrawItems call (a view; player 2 = the second view of a two-player frame) wrote `entry` bytes
// before it, and its extra passes ended at `after_extras`.
void probe_view(uint8_t* rdram, uint32_t player, uint32_t entry, uint32_t after_extras) {
    std::lock_guard lock{g_probe_mutex};
    ProbeFrame& f = g_probe.frame[word(rdram, thps::sym().gDlFrame) & 1];
    const uint32_t v = player ? 1 : 0;
    f.after_extras[v] = after_extras, f.extra_bytes[v] = after_extras - std::min(after_extras, entry), f.views |= uint8_t(1u << v);
    g_probe.entry.add(entry);
}
}  // namespace

std::string thps::dd::dd_game_dlprobe(uint8_t*, bool reset) {
    std::lock_guard lock{g_probe_mutex};
    char b[160];
    std::snprintf(b, sizeof b, "probe %d canary %d frames %u canary_bad %u direct %u", int(probe_on()), int(canary_on()), g_probe.frames, g_probe.canary_bad, g_direct_calls.load());
    const Probe& p = g_probe;
    std::string r = b + p.entry.str("entry") + p.pass.str("pass") + p.per_item.str("per_item") + p.own.str("own") + p.extras_1p.str("extras_1p") +
                    p.rest_1p.str("rest_1p") + p.total_1p.str("total_1p") + p.rest_2p_v0.str("rest_2p_v0") + p.rest_2p_v1.str("rest_2p_v1") + p.total_2p.str("total_2p");
    if (reset) {
        const uint32_t bad = g_probe.canary_bad;
        g_probe = Probe{};
        g_probe.canary_bad = bad;
    }
    return r;
}

bool thps::dd::dd_game_measure(uint8_t* rdram, uint32_t data_ptr, uint32_t data_size, BufferUse& u) {
    const auto& s = thps::sym();
    const uint32_t phys = data_ptr & 0x3FFFFFF;
    int idx = -1;
    for (int i = 0; i < 2; i++)
        if ((word(rdram, s.gDlBufs + 4 * i) & 0x3FFFFFF) == phys) idx = i;
    if (idx < 0) return false;
    u.dl_cap = word(rdram, s.gDlBufSize);
    u.dl_bytes = data_size;
    u.mtx_cap = word(rdram, s.gMtxCap);
    u.vtx_cap = word(rdram, s.gVtxCap);
    if (u.mtx_cap > 4096 || u.vtx_cap > 65536) return false;   // not set up yet
    u.queue_used = g_queue_hw.exchange(0), u.queue_cap = kQueueEntries;
    u.blend_used = g_sort_hw.exchange(0), u.blend_cap = kSortEntries;
    u.runs = g_runs_hw.exchange(0);
    u.defer_used = g_defer_hw.exchange(0), u.defer_cap = kDeferEntries;
    const uint32_t mpool = word(rdram, s.gMtxPools + 4 * idx) & 0x3FFFFFF, vpool = word(rdram, s.gVtxPools + 4 * idx) & 0x3FFFFFF;
    const uint32_t end = phys + std::min(data_size, u.dl_cap);
    for (uint32_t pc = phys; pc + 8 <= end; pc += 8) {
        const uint32_t w0 = word(rdram, pc), op = w0 >> 24;
        if (op == 0xDA) {   // G_MTX
            const uint32_t m = word(rdram, pc + 4) & 0x3FFFFFF;
            if (m >= mpool && m < mpool + u.mtx_cap * 64) u.mtx_used = std::max(u.mtx_used, (m - mpool) / 64 + 1);
        } else if (op == 0x01) {   // G_VTX: n vertices from w1
            const uint32_t v = word(rdram, pc + 4) & 0x3FFFFFF, n = (w0 >> 12) & 0xFF;
            if (v >= vpool && v < vpool + u.vtx_cap * 16) u.vtx_used = std::max(u.vtx_used, (v - vpool) / 16 + n);
        }
    }
    // The allocators clamp at the cap (they then hand out the last slots again): a pool counts as run out when its top slot is used.
    u.mtx_capped = (u.mtx_cap && u.mtx_used >= u.mtx_cap) || (u.vtx_cap && u.vtx_used >= u.vtx_cap);
    if (canary_on()) {   // the guard after this buffer (only lists the course set-up allocated have one)
        const uint32_t buf = word(rdram, s.gDlBufs + 4 * idx);
        bool bad = false;
        if (g_dl_guarded[idx].load() == buf && g_dl_guard_at[idx].load() == u.dl_cap)
            for (uint32_t k = 0; k < kGuard; k += 4) bad |= word(rdram, buf + u.dl_cap + k) != kGuardWord;
        if (bad) {
            std::lock_guard lock{g_probe_mutex};
            if (g_probe.canary_bad++ < 10) {
                std::printf("[thps] draw distance: WARNING display list %d (0x%08X, %u bytes) written past its end: task %u bytes\n", idx, buf, u.dl_cap, data_size);
                std::fflush(stdout);
            }
            g_dl_guarded[idx] = 0;   // counted once per list; never written again (the memory may be another owner's by now)
        }
    }
    if (probe_on()) {   // the rest of the frame after the extra passes of each view (the later views' extra passes not counted)
        std::lock_guard lock{g_probe_mutex};
        ProbeFrame f = g_probe.frame[idx];
        g_probe.frame[idx] = ProbeFrame{};
        g_probe.frames++;
        if (f.views == 1) {
            g_probe.rest_1p.add(data_size - std::min(data_size, f.after_extras[0]));
            g_probe.total_1p.add(data_size);
            g_probe.extras_1p.add(f.extra_bytes[0]);
        } else if (f.views == 3) {
            g_probe.rest_2p_v0.add(data_size - std::min(data_size, f.after_extras[0] + f.extra_bytes[1]));
            g_probe.rest_2p_v1.add(data_size - std::min(data_size, f.after_extras[1]));
            g_probe.total_2p.add(data_size);
        }
    }
    return true;
}

// Which hidden bits the zone culling set. The trigger scripts hide items in two ways: World_SetVisibilityInBox (by box, as the skater moves:
// draw-cost culling) and per-item commands (by name, on events: secret areas, things revealed by a gap or a goal). Only the first kind may
// be undone for "full". The box hook below runs the game's function and records, per item, the hidden bits that call changed (set ->
// noted, cleared -> forgotten); any other writer leaves the record alone, so a bit set by an event command is never in it. The record is
// per course instance: a new item list (pointer or count) or a new course set-up (thps::dd::course_generation: Gfx_SetupCourse, also at a
// RETRY, which can rebuild the list at the same address; review 2026-10-26, finding 7) starts it again: empty, except for what the zone culling did and the items an event
// named since the course items were last drawn (the new course's set-up scripts, whether they ran before the set-up or after it). Game
// thread only.
namespace {
struct ZoneRecord {
    uint32_t arr = 0, n = 0;
    uint64_t gen = 0;             // the course set-up it belongs to
    std::vector<uint8_t> bits;    // per item: hidden bits (of 0x41) the zone culling set and nothing has cleared since
    std::vector<uint8_t> after;   // per item: the item's hidden bits right after the zone culling last changed them
    std::vector<uint8_t> event;   // per item: named by World_FindItem in this course (a script / goal / gap command): never unhidden
} g_zone;
std::vector<uint16_t> g_before;
std::vector<uint32_t> g_named_since_draw;   // items World_FindItem named since the last World_DrawItems of the course items
std::vector<uint32_t> g_zoned_since_draw;   // and the indices of the items whose hidden bits the zone culling changed since then
uint16_t* flag_ptr(uint8_t* rdram, uint32_t arr, uint32_t i) {
    return reinterpret_cast<uint16_t*>(rdram + ((word(rdram, word(rdram, arr + 4 * i) + 4) & 0x3FFFFFE) ^ 2));
}
void zone_sync(uint8_t* rdram, uint32_t list) {
    const uint32_t n = word(rdram, list + 16), arr = word(rdram, list + 12);
    const uint64_t gen = thps::dd::course_generation();
    if (n != g_zone.n || arr != g_zone.arr || gen != g_zone.gen) {
        const size_t m = n <= 8192 ? n : 0;
        ZoneRecord old = std::move(g_zone);
        g_zone = ZoneRecord{arr, n, gen, std::vector<uint8_t>(m, 0), std::vector<uint8_t>(m, 0), std::vector<uint8_t>(m, 0)};
        // The same list, a new course instance: the zone culling done since the last draw (the new run's, while it loaded) is kept. Event
        // ownership comes only from the names below, never from the old record.
        if (arr == old.arr && n == old.n)
            for (uint32_t i : g_zoned_since_draw)
                if (i < m && i < old.bits.size()) g_zone.bits[i] = old.bits[i], g_zone.after[i] = old.after[i];
        for (uint32_t i = 0; i < m && !g_named_since_draw.empty(); i++)
            if (std::find(g_named_since_draw.begin(), g_named_since_draw.end(), word(rdram, arr + 4 * i)) != g_named_since_draw.end()) g_zone.event[i] = 1;
    }
}
}  // namespace

extern "C" int thps_world_set_visibility_in_box(uint8_t* rdram, recomp_context* ctx) {
    thread_local bool inside = false;
    if (inside) return 0;
    const uint32_t list = thps::sym().gWorldItems;
    zone_sync(rdram, list);
    const uint32_t n = uint32_t(g_zone.bits.size()), arr = g_zone.arr;
    g_before.resize(n);
    for (uint32_t i = 0; i < n; i++) g_before[i] = *flag_ptr(rdram, arr, i);
    inside = true;
    thps::call_guest(thps::sym().World_SetVisibilityInBox, rdram, ctx);
    inside = false;
    for (uint32_t i = 0; i < n; i++) {
        const uint16_t after = *flag_ptr(rdram, arr, i), changed = uint16_t((g_before[i] ^ after) & 0x41);
        if (changed) {
            g_zone.bits[i] = uint8_t((g_zone.bits[i] & ~changed) | (after & changed));
            if (g_zoned_since_draw.size() < 65536) g_zoned_since_draw.push_back(i);
            g_zone.after[i] = uint8_t(after & 0x41);
        }
    }
    return 1;
}

// Event ownership. Whatever looks an item up by name (the scripts' per-item show / hide / kill commands, goal and gap code) owns it from
// then on, for this course: "full" never unhides it, even if the zone culling had also hidden it. Conservative on purpose: a secret
// revealed or hidden by an event stays under the game's own control.
extern "C" int thps_world_find_item(uint8_t* rdram, recomp_context* ctx) {
    thread_local bool inside = false;
    if (inside) return 0;
    const uint32_t list = uint32_t(ctx->r4);
    inside = true;
    thps::call_guest(thps::sym().World_FindItem, rdram, ctx);
    inside = false;
    const uint32_t item = uint32_t(ctx->r2);
    if (item && list == thps::sym().gWorldItems) {
        if (g_named_since_draw.size() < 8192) g_named_since_draw.push_back(item);
        zone_sync(rdram, list);
        for (uint32_t i = 0; i < g_zone.event.size(); i++)
            if (word(rdram, g_zone.arr + 4 * i) == item) { g_zone.event[i] = 1; break; }
    }
    return 1;
}

// Zone visibility (draw call). The course's items (World_DrawItems' list: count at +16, pointers at +12; each item's flag halfword through the
// pointer at item +4) carry a "hidden" bit per player (1, player 2: 0x40) that the trigger scripts set and clear by box as the skater
// moves (the command at 0x800A95A0 calls World_SetVisibilityInBox 0x80032C88 in THPS3 US), so most of a course is not drawn from most places (THPS2 Hangar
// start: 144 of 470 items hidden). With "full" the hook clears those bits, runs the function, and puts every flag back exactly, so
// collision and the trigger state never see the change.
//
// Off since v0.2 (playtest 2026-10-26): "full" no longer clears them. In THPS2 the box zones turned out to do more than culling (the
// Hangar swaps its floor's light overlays and hides its crashed ceiling by box), and this engine is the same, so a box-hidden item is
// left to the game until the trigger that issued each call can tell culling from a course state (v0.3). The record below is kept, and
// `dd showall all` still clears every hidden bit for exploration.
//
// Runs of at most kChunk items, as in THPS2 (its game/draw_distance.cpp has the story). World_DrawItems is one pass of the renderer: its
// mesh queue (845 here) and sorted list (96) must hold every mesh of every item drawn, and the list of items it puts aside (64, unchecked)
// every item with a depth offset; what does not fit the first two is dropped, in course-item order. So
// when the call draws more than the game would (a longer far plane, or zone-hidden items unhidden), the items only the setting adds are
// drawn first, farthest first, in runs of at most kChunk visible items, each run its own pass (the pass end draws and empties the lists,
// 0x800C9910, then the next pass begins, 0x800C98F0), followed by a pass of its own for the items the run put aside
// (World_DrawDeferredItems, as the frame does after the item pass, 0x800325DC..0x800325F4; World_DrawItems empties that list when it
// starts, so a run of at most kChunk items can never put more than 64 aside). The last run is exactly what the game itself draws, and its
// put-aside items are left for the frame's own pass.
// Far before near keeps translucent meshes over what is behind them. An item is left out of a run by its +0x44 float, which the loop
// tests right after the sphere test (negative = not drawn): set to -1 for that run only and put back. Only when the call runs inside a
// pass (the renderer's batch flag +0x3FB0; World_DrawItems' other caller, 0x800717D4, draws without one). Visibility here is the game's
// own test (0x800C7E8C: the view's five planes at +0x1D0 and the far distance at +0x174, camera at +0x90; item centre +0x34, radius +0x40).
//
// The display-list budget (a backstop; with the 144 KiB lists it is not expected to act). Nothing in the game stops a display list at
// its end, and the extra passes come before the parts of the frame that must be drawn: the game's own pass, the scenery, the moving
// objects, the HUD and, in two-player games, the other view. So before each extra pass the hook reads how much of the frame's list is
// written (gDlHead - gDlBufs[gDlFrame]: three words) and draws the next passes only while used + kPassBound + the rest's bound + kMargin
// fits the buffer. When it does not fit them all, it keeps the nearest extra items it can afford and leaves the farthest out (the
// remaining ones are still drawn far to near); the cut is counted (`dd`: cuts, cut_items) and logged with --verbose. The bounds are
// measured maxima with room to spare (2026-10-23, THPS_DD_DLPROBE at Full with 256 KiB lists): see kPassBound / kRestBound.
// The nearest pass keeps its bound reserved from the first extra pass on (review 2026-10-26, finding 9): the passes are drawn far to near,
// and until then the passes after the next were all counted at their running average, so an expensive far pass could leave the room short
// for the nearest items. Now the next pass and the nearest one count at their bound and only those between at the average; a shortfall
// drops more of the far ones. The nearest pass is cut (late_cuts) only if a pass took more than kPassBound. (Every pass at its bound, the
// first version of this fix, cut School II's far items at the default budget with the list less than half full.)
namespace {
constexpr uint32_t kBatchOn = 0x3FB0;
constexpr uint32_t kChunk = 48;
constexpr uint32_t kPassBound = 0x2000;   // one extra pass (48 items, its pass end and begin): measured at most 6,264 bytes (THPS3 Rio)
constexpr uint32_t kItemBound = 0x200;    // one extra item drawn outside a pass: at most 336 bytes per item in the passes
constexpr uint32_t kRestBound = 0xC000;   // the rest of the frame after the extra passes: at most 32,144 (THPS3 Rio; p99 13-20 KB);
                                          // two players, after the first view's (the second view's own part included): 18,088
constexpr uint32_t kViewBound = 0x2000;   // and per view still to come (two players: the second view's own part, about 5.5 KB)
constexpr uint32_t kMargin = 0x1000;
float g_pass_avg = 4096.0f;   // the bytes an extra pass has been taking (a running average; game thread)
// How many of `wanted` more extra items (in passes of kChunk, or one by one outside a pass) the frame's display list can still take, with
// `used` bytes written. The next pass and the nearest (last) one must fit with their bound (kPassBound); the ones between are counted at
// what passes have been taking (g_pass_avg, at most the bound), since each of them is checked against its bound again before it is drawn.
size_t affordable(const uint8_t* rdram, uint32_t used, size_t wanted, bool in_passes, bool view_follows) {
    const thps::dd::DlBudget o = thps::dd::dl_budget();
    const uint32_t buf = word(rdram, thps::sym().gDlBufSize), cap = o.cap ? std::min(o.cap, buf) : buf;
    const uint64_t need = uint64_t(used) + (o.rest ? o.rest : kRestBound) + (view_follows ? kViewBound : 0) + (o.margin ? o.margin : kMargin);
    if (need >= cap) return 0;
    const uint64_t room = cap - need;
    if (!in_passes) return size_t(std::min<uint64_t>(room / kItemBound, wanted));
    const uint64_t bound = o.pass ? o.pass : kPassBound;
    if (room < bound) return 0;
    if (wanted <= kChunk || room < 2 * bound) return std::min<size_t>(wanted, kChunk);   // one pass: the nearest
    const uint64_t est = uint64_t(std::clamp(g_pass_avg, 1024.0f, float(bound)));
    return size_t(std::min<uint64_t>((2 + (room - 2 * bound) / est) * kChunk, wanted));
}
float fword(const uint8_t* rdram, uint32_t a) { return f32(rdram, a); }
}  // namespace

extern "C" int thps_world_draw_items(uint8_t* rdram, recomp_context* ctx) {
    thread_local bool inside = false;
    if (inside) return 0;
    thps::dd::HookTimer timer;   // ftime: this hook's own time (the game's drawing excluded)
    const auto& sy = thps::sym();
    const uint32_t list = uint32_t(ctx->r4), view = uint32_t(ctx->r5), n = word(rdram, list + 16), arr = word(rdram, list + 12);
    if (n == 0 || n > 8192 || list != sy.gWorldItems) return 0;
    zone_sync(rdram, list);   // a new course instance takes the items named since the last draw (above), then that list starts again
    g_named_since_draw.clear(), g_zoned_since_draw.clear();
    const bool unhide = thps::dd::unhide_everything();   // zone unhiding is off (above); `dd showall all` only
    // The view's far (+0x174) is the world view's, which the camera code sets at a course start and on camera changes, with the far plane
    // of the setting (dd_game_far: projection_factor), not every frame. The governor's factor in use (lowered by its
    // back-offs) is applied to the extra items instead (hold_far below).
    const float game_far = f32(rdram, sy.gFarPlane), view_far = fword(rdram, view + 0x174);
    const uint32_t probe_entry = probe_on() ? dl_used(rdram) : 0;
    if (!unhide && !(game_far > 0.0f && view_far > game_far * 1.001f)) {   // the game's own picture: one run, as the game does
        if (probe_on()) probe_view(rdram, uint32_t(ctx->r6), probe_entry, probe_entry);
        return 0;
    }
    const uint16_t mask = uint16_t((ctx->r6 ? 0x40 : 0x01) | 0x1000);   // the loop's own skip test (player 2: 0x40; scenery 0x1000)
    zone_sync(rdram, list);
    static std::vector<uint32_t> saved;   // flag halfword address, value (game thread only)
    static std::vector<uint16_t> before;  // each item's flags before any unhiding: what the game itself would draw
    saved.clear();
    before.assign(n, 0);
    uint32_t hidden = 0;
    for (uint32_t i = 0; i < n; i++) {
        const uint32_t fl = word(rdram, word(rdram, arr + 4 * i) + 4) & 0x3FFFFFE;
        uint16_t* h = reinterpret_cast<uint16_t*>(rdram + (fl ^ 2));
        before[i] = *h;
        if (!unhide || i >= g_zone.bits.size()) continue;
        hidden += (*h & 0x41) != 0;
        // A record goes stale as soon as anything else changed the bits since the zone culling did (an event hid or showed the item:
        // the game's own state governs from then on), and an item named by an event is never unhidden.
        if (g_zone.bits[i] && ((*h & 0x41) != g_zone.after[i] || g_zone.event[i])) g_zone.bits[i] = 0;
        const uint16_t zone = uint16_t(*h & (thps::dd::unhide_everything() ? 0x41 : g_zone.bits[i]));   // only what the zone culling hid
        if (zone) {
            saved.push_back(fl);
            saved.push_back(*h);
            *h = uint16_t(*h & ~zone);
        }
    }
    static uint32_t frames = 0;
    if (unhide && thps::verbose() && (frames++ % 300) == 0) {   // evidence: hidden items, and how many of them only the zone culling hid
        uint32_t named = 0;
        for (uint8_t e : g_zone.event) named += e;
        std::printf("[thps] draw distance: items %u, hidden %u, of them by the zone culling (unhidden for this draw) %u; items named by events %u\n", n, hidden,
                    uint32_t(saved.size() / 2), named);
        // the ones kept hidden (not the zone culling's): index, flags, position (item +36/+40/+44, floats)
        for (uint32_t i = 0, shown = 0; i < n && i < g_zone.bits.size() && shown < 12; i++) {
            const uint32_t it = word(rdram, arr + 4 * i);
            const uint16_t f = *flag_ptr(rdram, arr, i);
            if (!(f & 0x41) || (f & g_zone.bits[i]) == (f & 0x41)) continue;
            float pos[3];
            for (int k = 0; k < 3; k++) { uint32_t w = word(rdram, it + 36 + 4 * k); std::memcpy(&pos[k], &w, 4); }
            std::printf("[thps] draw distance:   kept hidden: item %u flags 0x%04X zone 0x%02X at (%.0f, %.0f, %.0f)\n", i, f, g_zone.bits[i], pos[0], pos[1], pos[2]);
            shown++;
        }
        std::fflush(stdout);
    }
    const uint32_t renderer = word(rdram, sy.gRenderer);
    const uint64_t a0 = ctx->r4, a1 = ctx->r5, a2 = ctx->r6;
    const bool batched = renderer && word(rdram, renderer + kBatchOn) == 1;
    // Two players: the first view's call (a2 = 0) is followed by the second's in the same frame (seen within the last few calls).
    static uint32_t calls = 0, last_second = 0x80000000u;
    calls++;
    if (a2) last_second = calls;
    const bool view_follows = !a2 && calls - last_second < 4;

    // Which items this call draws, and which of them only the setting adds (beyond the game's far, or unhidden here).
    const float cam[3] = {fword(rdram, view + 0x90), fword(rdram, view + 0x94), fword(rdram, view + 0x98)};
    // Extra items beyond the factor in use are held back (a back-off, a lower setting, which the world view's far does not follow until the
    // camera code sets it again): those beyond the game's far past game far x factor, the unhidden ones, while the factor is below its end,
    // past (factor - 1) x the game's far.
    const float reach = unhide ? thps::dd::unhide_reach() * game_far : 0.0f, hold_far = game_far * thps::dd::factor();
    static std::vector<std::pair<float, uint32_t>> extra;   // (distance to the bounding sphere, item index)
    static std::vector<uint32_t> held;                      // extra items beyond the factor in use (left out of every run)
    static std::vector<uint32_t> skip_addr;                 // each item's +0x44 (RDRAM word address)
    static std::vector<uint32_t> skip_was;
    extra.clear(), held.clear();
    skip_addr.resize(n), skip_was.resize(n);
    for (uint32_t i = 0; i < n; i++) {
        const uint32_t it = word(rdram, arr + 4 * i);
        skip_addr[i] = (it + 0x44) & 0x3FFFFFC;
        skip_was[i] = word(rdram, it + 0x44);
        const uint32_t fl = word(rdram, it + 4) & 0x3FFFFFE;
        if (*reinterpret_cast<const uint16_t*>(rdram + (fl ^ 2)) & mask) continue;   // not drawn by this call at all
        const float d[3] = {fword(rdram, it + 0x34) - cam[0], fword(rdram, it + 0x38) - cam[1], fword(rdram, it + 0x3C) - cam[2]};
        const float r = fword(rdram, it + 0x40), d2 = d[0] * d[0] + d[1] * d[1] + d[2] * d[2];
        if ((r + view_far) * (r + view_far) < d2) continue;   // the game's far test with the far in use
        bool in = true;
        for (int k = 0; k < 5 && in; k++) {
            const uint32_t pl = view + 0x1D0 + 12 * k;
            in = fword(rdram, pl) * d[0] + fword(rdram, pl + 4) * d[1] + fword(rdram, pl + 8) * d[2] + r >= 0.0f;
        }
        if (!in) continue;
        const bool game_draws = !(before[i] & mask) && (r + game_far) * (r + game_far) >= d2;
        if (game_draws) continue;
        const float gap = std::sqrt(d2) - r;
        if ((before[i] & mask) ? gap > reach : gap > hold_far) held.push_back(i);
        else extra.emplace_back(gap, i);
    }
    constexpr uint32_t kNeg = 0xBF800000u;   // -1.0f
    inside = true;
    if (!batched) {
        // Not inside a pass (THPS3's other caller, 0x800717D4, draws its own list this way; for the course items it has not been seen,
        // `dd dlprobe` direct): the batcher draws at once, no lists to fill. One call, the held items left out.
        g_direct_calls.fetch_add(1, std::memory_order_relaxed);
        if (probe_on()) probe_view(rdram, uint32_t(a2), probe_entry, probe_entry);
        // The budget per item (kItemBound): the farthest extra items that do not fit are left out with the held ones.
        const size_t keep = affordable(rdram, dl_used(rdram), extra.size(), false, view_follows);
        if (keep < extra.size()) {
            std::sort(extra.begin(), extra.end(), [](const auto& x, const auto& y) { return x.first > y.first; });
            const size_t cut = extra.size() - keep;
            for (size_t k = 0; k < cut; k++) held.push_back(extra[k].second);
            thps::dd::note_cut(uint32_t(cut), dl_used(rdram), word(rdram, sy.gDlBufSize));
        }
        for (uint32_t i : held) *reinterpret_cast<uint32_t*>(rdram + skip_addr[i]) = kNeg;
        timer.guest([&] { thps::call_guest(sy.World_DrawItems, rdram, ctx); });
        for (uint32_t i : held) *reinterpret_cast<uint32_t*>(rdram + skip_addr[i]) = skip_was[i];
    } else {
        std::sort(extra.begin(), extra.end(), [](const auto& x, const auto& y) { return x.first > y.first; });
        static std::vector<uint8_t> in_run;
        in_run.assign(n, 0);
        auto run = [&](size_t from, size_t to, bool last) {
            // last: everything except the extra and held items (= what the game draws); otherwise extra[from, to)
            std::fill(in_run.begin(), in_run.end(), uint8_t(last ? 1 : 0));
            for (size_t k = last ? 0 : from; k < (last ? extra.size() : to); k++) in_run[extra[k].second] = uint8_t(last ? 0 : 1);
            if (last)
                for (uint32_t i : held) in_run[i] = 0;
            for (uint32_t i = 0; i < n; i++)
                if (!in_run[i]) *reinterpret_cast<uint32_t*>(rdram + skip_addr[i]) = kNeg;
            ctx->r4 = a0, ctx->r5 = a1, ctx->r6 = a2;
            timer.guest([&] { thps::call_guest(sy.World_DrawItems, rdram, ctx); });
            for (uint32_t i = 0; i < n; i++) *reinterpret_cast<uint32_t*>(rdram + skip_addr[i]) = skip_was[i];
            if (!last) {   // this run's pass ends (its lists drawn and emptied), its put-aside items get their own pass, the next one begins
                ctx->r4 = int32_t(renderer);   // sign-extended, as the recompiled code keeps addresses
                timer.guest([&] { thps::call_guest(sy.Mesh_PassEnd, rdram, ctx); });
                ctx->r4 = int32_t(renderer);   // sign-extended, as the recompiled code keeps addresses
                timer.guest([&] { thps::call_guest(sy.Mesh_PassBegin, rdram, ctx); });
                if (word(rdram, sy.gDeferredItemCount)) {
                    ctx->r4 = a0;
                    timer.guest([&] { thps::call_guest(sy.World_DrawDeferredItems, rdram, ctx); });
                    ctx->r4 = int32_t(renderer);   // sign-extended, as the recompiled code keeps addresses
                    timer.guest([&] { thps::call_guest(sy.Mesh_PassEnd, rdram, ctx); });
                    ctx->r4 = int32_t(renderer);   // sign-extended, as the recompiled code keeps addresses
                    timer.guest([&] { thps::call_guest(sy.Mesh_PassBegin, rdram, ctx); });
                }
            }
        };
        // The extra passes, far to near, within the display-list budget: before each pass, the items the list can no longer take are
        // dropped from the far end of what is left; the nearest pass keeps its bound reserved throughout (affordable), so it is the one
        // kept. Items cut from the nearest pass once passes were drawn (late) mean a pass took more than its bound.
        size_t cut = 0, late = 0, passes = 0;
        uint32_t cut_used = 0, late_used = 0;
        for (size_t k = 0; k < extra.size();) {
            const uint32_t used = dl_used(rdram);
            const size_t left = extra.size() - k, keep = affordable(rdram, used, left, true, view_follows);
            if (keep < left) {
                const size_t near_cut = passes && std::min(left, size_t(kChunk)) > keep ? std::min(left, size_t(kChunk)) - keep : 0;
                if (near_cut && !late) late_used = used;
                if (left - keep > near_cut && !cut) cut_used = used;
                late += near_cut, cut += left - keep - near_cut, k += left - keep;
                if (k >= extra.size()) break;
            }
            const uint32_t u0 = probe_on() ? dl_used(rdram) : 0;
            const size_t to = std::min(extra.size(), k + kChunk);
            run(k, to, false);
            passes++;
            const uint32_t items = uint32_t(to - k);
            if (items == kChunk) g_pass_avg += (float(dl_used(rdram) - used) - g_pass_avg) * 0.125f;   // full passes only
            k = to;
            if (probe_on()) {
                const uint32_t d = dl_used(rdram) - u0;
                std::lock_guard lock{g_probe_mutex};
                g_probe.pass.add(d), g_probe.per_item.add(d / items);
            }
        }
        if (cut) thps::dd::note_cut(uint32_t(cut), cut_used, word(rdram, sy.gDlBufSize));
        if (late) thps::dd::note_cut(uint32_t(late), late_used, word(rdram, sy.gDlBufSize), true);
        const uint32_t probe_after = probe_on() ? dl_used(rdram) : 0;
        if (probe_on()) probe_view(rdram, uint32_t(a2), probe_entry, probe_after);
        run(0, 0, true);
        if (probe_on()) {
            const uint32_t d = dl_used(rdram) - probe_after;
            std::lock_guard lock{g_probe_mutex};
            g_probe.own.add(d);
        }
        max_into(g_runs_hw, uint32_t((extra.size() + kChunk - 1) / kChunk + 1));
    }
    ctx->r4 = a0, ctx->r5 = a1, ctx->r6 = a2;
    inside = false;
    for (size_t i = 0; i + 1 < saved.size(); i += 2) *reinterpret_cast<uint16_t*>(rdram + (saved[i] ^ 2)) = uint16_t(saved[i + 1]);
    return 1;
}

// The matrix pools. The gfx set-up gets both pools (420 x 64 bytes each) with one Mem_Alloc(heap, 0xD200, 8) and stores the cap (420) in
// that call's delay slot; right after the call it reads the cap back to place the second pool (pool 2 = pool 1 + cap x 64), and the
// per-frame allocator caps at it (the only other reader of the cap word). 420 is what limits `full` in the busiest courses.
// With dd_buffers = bigger (the default; src/draw_distance.cpp) this asks for kBigCap matrices per pool at every course start, whatever the
// setting, and raises the cap word before the call so the set-up places pool 2 at pool 1 + kBigCap x 64. The cap word is then set to
// what is in force: kBigCap while the setting is not `original`, else the game's 420 (sync_cap: first at the set-up's next request, the
// vertex pools, which comes after the cap was read back; then every frame from dd_game_far). Both caps index the same two pools, so the
// setting takes effect at once, in either direction; past the cap the allocator hands out the pool's last slots again, as the game does.
// With dd_buffers = original the game's own request and cap (the governor then keeps the far plane within 420). If the heap has no room
// for the bigger block (checked before the request, see thps_mem_alloc), the game's own request is made.
// The heap has room (2026-10-22, every course, one and two players): at least 2.9 MB free and a largest free block of 894,880 bytes.
//
// The display lists. The same set-up first allocates the two top-level display lists: gDlBufSize = gDlUnits x 8 (0x2400 x 8 = 72 KiB; the
// setter 0x800BC8D0 picks 0x3000, 96 KiB, in one mode), then two Mem_Alloc(heap, gDlBufSize, 8), before the matrix pools. Nothing caps the
// writes to a list (the frame end notices an overrun only afterwards and puts the end commands back inside the buffer), and THPS2 School II at
// Full went past 72 KiB (78,376 bytes, 2026-10-22; this engine is the same). With dd_buffers = bigger each list gets at least kBigDl bytes, whatever the setting
// (as the matrix pools: so the setting takes effect at once); a larger size of the game's own is kept. thps_gfx_setup_course marks the
// set-up, so only its two requests are changed (the front end's set-up, 0x800BD5EC, keeps its own 72 KiB lists). gDlBufSize is set to the
// size really allocated before each request, so both buffers always hold what it says: if the heap has no room for a bigger list (checked
// before the request: a failed request hangs the game, see thps_mem_alloc), gDlBufSize stays the game's size for that request and the next.
namespace {
constexpr uint32_t kBigDl = 0x24000;   // 144 KiB per display list (2 x 72 KiB more heap in all; the heap has room: 2026-10-23 dd-heap runs)
// Tests / measurements: THPS_DD_DL_BYTES=N asks for N bytes per list instead (rounded up to 8; a larger buffer than the game's still).
uint32_t dl_min_bytes() {
    static const uint32_t n = std::getenv("THPS_DD_DL_BYTES") ? (uint32_t(std::strtoul(std::getenv("THPS_DD_DL_BYTES"), nullptr, 0)) + 7u) & ~7u : kBigDl;
    return n;
}
thread_local bool t_setup = false, t_dl_fallback = false;
thread_local uint32_t t_dl_calls = 0, t_dl_native = 0;
std::atomic<uint32_t> g_dl_native{0}, g_dl_fallbacks{0};   // the game's own size of the current lists; requests that fell back to it
}  // namespace

namespace { void vtx_setup_starts(); }
extern "C" int thps_gfx_setup_course(uint8_t* rdram, recomp_context* ctx) {
    thread_local bool inside = false;
    if (inside) return 0;
    inside = true, t_setup = true, t_dl_calls = 0, t_dl_native = 0, t_dl_fallback = false;
    thps::dd::heap_view_begin();     // tests (THPS_DD_HEAP_FREE): the planning's view of the free list starts again
    vtx_setup_starts();   // the last course's vertex pools are not this one's (their cap must not be synced over the game's 500 at the request)
    thps::dd::note_course_start();   // the governor: the setting again for this course (ceiling reset)
    thps::call_guest(thps::sym().Gfx_SetupCourse, rdram, ctx);
    t_setup = false, inside = false;
    if (t_dl_calls) g_dl_native = t_dl_native;
    // Every set-up, like the matrix pools' line (until 2026-10-23 only the first three: a player's log then looked as if later courses had
    // the game's own lists)
    std::printf("[thps] draw distance: display lists: 2 x %u bytes (the game's %u)%s\n", word(rdram, thps::sym().gDlBufSize), t_dl_native,
                t_dl_fallback ? ", no room for the bigger ones" : "");
    std::fflush(stdout);
    return 1;
}

// The vertex pools, the same way (2026-10-25). Right after the matrix pools the set-up asks for both vertex pools with one
// Mem_Alloc(heap, 0x3E80, 8) (500 x 16 bytes each), storing the cap (500, gVtxCap) in the delay slot and placing pool 2 at pool 1 + cap x 16
// after the call; the per-frame allocator (0x800BCD1C) is the cap's only other reader: it hands out n vertices while count + n < cap, and
// past that returns the start of the pool again (and counts the refused vertices at 0x80105C5C, both reset every frame). The pool holds text,
// particles and shadows. THPS3's career goals screen, drawn over the course at every course start, takes 498 of the 500 at any setting
// (and a two-player start screen the same), so the governor, which counts this pool, panicked to 1x on those frames and kept that
// ceiling for the whole run: Full looked like Original (the user's Canada reports, one and two players). With dd_buffers = bigger each
// pool now holds kBigVtx, and the cap in force is kBigVtx while the setting is not `original` (the game's 500 at `original`, as for the
// matrices); the governor still counts the pool, against the cap in force.
namespace {
constexpr uint32_t kGameCap = 420, kBigCap = 2048;
constexpr uint32_t kGameVtx = 500, kBigVtx = 4096;   // 2 x 4096 x 16 = 128 KiB (the game's 16,000 bytes; the heap has room, see below). Measured at Full:
                                                     // the goals screen 820, a two-player start 1600, gameplay up to 152
std::atomic<uint32_t> g_heap{0};        // the heap the gfx set-up allocates from (Mem_Alloc's a0 for the matrix pools)
std::atomic<uint32_t> g_big_block{0};   // the bigger pools of the current course (0: the game's own)
std::atomic<uint32_t> g_big_vtx{0};     // the bigger vertex pools of the current course (0: the game's own)
struct HeapStats { uint32_t failed, free_bytes, largest, blocks; };
HeapStats heap_stats(uint8_t* rdram, uint32_t heap) {   // free list: head at +0, next at +4, free bytes at +20; +16 = the last failed size (-1 = none)
    HeapStats h{word(rdram, heap + 16), 0, 0, 0};
    for (uint32_t b = word(rdram, heap), k = 0; b && k < 100000; b = word(rdram, b + 4), k++) {
        const uint32_t f = word(rdram, b + 20);
        h.free_bytes += f, h.largest = std::max(h.largest, f), h.blocks++;
    }
    return h;
}
void put_word(uint8_t* rdram, uint32_t vaddr, uint32_t v) { *reinterpret_cast<uint32_t*>(rdram + (vaddr & 0x3FFFFFC)) = v; }
// The bigger pools are the ones in use (the set-up placed both in the block this hook got), so the cap word may be set.
bool big_in_use(uint8_t* rdram) {
    const uint32_t b = g_big_block.load();
    const auto& s = thps::sym();
    return b && word(rdram, s.gMtxPools) == b && word(rdram, s.gMtxPools + 4) == b + kBigCap * 64;
}
bool big_vtx_in_use(uint8_t* rdram) {
    const uint32_t b = g_big_vtx.load();
    const auto& s = thps::sym();
    return b && word(rdram, s.gVtxPools) == b && word(rdram, s.gVtxPools + 4) == b + kBigVtx * 16;
}
void sync_cap(uint8_t* rdram) {   // game thread
    if (big_in_use(rdram)) {
        const uint32_t want = thps::dd::enlarge_pools() ? kBigCap : kGameCap;
        if (word(rdram, thps::sym().gMtxCap) != want) put_word(rdram, thps::sym().gMtxCap, want);
    }
    if (big_vtx_in_use(rdram)) {
        const uint32_t want = thps::dd::enlarge_pools() ? kBigVtx : kGameVtx;
        if (word(rdram, thps::sym().gVtxCap) != want) put_word(rdram, thps::sym().gVtxCap, want);
    }
}
// Low-water marks of the gfx heap since the start or `dd heap reset` (under g_low_mutex).
struct HeapLow {
    uint32_t calls = 0, failed = 0, biggest = 0;
    uint32_t free_min = UINT32_MAX, largest_min = UINT32_MAX;   // after an allocation
    int64_t margin_min = INT64_MAX;                              // largest free block before a request - its size
    uint32_t margin_size = 0;                                    //   the request that had the least margin
};
std::mutex g_low_mutex;
HeapLow g_low;
void note_heap(const HeapStats& before, const HeapStats& after, uint32_t size, bool ok) {
    std::lock_guard lock{g_low_mutex};
    g_low.calls++;
    if (!ok) g_low.failed++;
    g_low.biggest = std::max(g_low.biggest, size);
    g_low.free_min = std::min(g_low.free_min, after.free_bytes);
    g_low.largest_min = std::min(g_low.largest_min, after.largest);
    const int64_t m = int64_t(before.largest) - int64_t(size);
    if (m < g_low.margin_min) g_low.margin_min = m, g_low.margin_size = size;
}
}  // namespace

namespace { void vtx_setup_starts() { g_big_vtx = 0; } }
void thps::dd::dd_game_sync_pools(uint8_t* rdram) { sync_cap(rdram); }

namespace {
// The set-up's requests to the gfx heap, in order (Gfx_SetupCourse, as THPS2's: two display lists of gDlBufSize, the matrix pools 0xD200,
// the vertex pools 0x3E80, all align 8), each as the allocator counts it.
uint32_t heap_need(uint32_t n) { return ((n + 0x23) & ~3u) + 8; }
struct PlanReq { uint32_t native, big; bool can; };
// Which of the set-up's remaining requests to make bigger (review 2026-10-26, finding 1; rest[0] is the request at hand). A request that
// fails hangs the game, and so does a later one the bigger ones left no room for: so the plan places every remaining request, first fit, on
// a copy of the free list. The native plan first: if it does not fit, nothing is enlarged (the game's own set-up fails there anyway). Then
// each enlargement in order (the first `pair` requests, the two display lists, together) is kept when the plan with it still places every
// request and leaves a largest free block of thps::dd::plan_floor (the native plan's, at most 768 KiB), so the requests after the set-up
// find a block as big as the biggest one they make.
std::vector<bool> plan_enlarge(uint8_t* rdram, uint32_t heap, const std::vector<PlanReq>& rest, size_t pair) {
    const std::vector<uint32_t> blocks = thps::dd::heap_free_blocks(rdram, heap);
    const uint32_t cache = thps::dd::heap_failed_cache(rdram, heap);
    std::vector<bool> big(rest.size(), false);
    auto needs = [&] {
        std::vector<uint32_t> v;
        for (size_t i = 0; i < rest.size(); i++) v.push_back(big[i] ? rest[i].big : rest[i].native);
        return v;
    };
    const int64_t native = thps::dd::first_fit_after(blocks, needs(), cache);
    if (native < 0) return big;
    const int64_t floor = thps::dd::plan_floor(native);
    for (size_t i = 0; i < rest.size();) {
        const size_t n = i < pair ? pair - i : 1;
        bool can = true;
        for (size_t k = i; k < i + n && k < rest.size(); k++) can = can && rest[k].can && rest[k].big != rest[k].native;
        if (can) {
            for (size_t k = i; k < i + n && k < rest.size(); k++) big[k] = true;
            if (thps::dd::first_fit_after(blocks, needs(), cache) < floor)
                for (size_t k = i; k < i + n && k < rest.size(); k++) big[k] = false;
        }
        i += n;
    }
    return big;
}
}  // namespace

extern "C" int thps_mem_alloc(uint8_t* rdram, recomp_context* ctx) {
    const auto& s = thps::sym();
    static thread_local bool inside = false, pending = false, vtx_pending = false;
    if (inside) return 0;
    const uint32_t heap = uint32_t(ctx->r4), size = uint32_t(ctx->r5), align = uint32_t(ctx->r6);
    // The set-up's next request after the pools (the vertex pools): pool 2 is placed by now, so the cap in force can be set.
    if (pending) pending = false, sync_cap(rdram);
    // The same for the vertex pools at the request after theirs (or, if the set-up makes none, at the next frame: dd_game_far).
    if (vtx_pending) vtx_pending = false, sync_cap(rdram);
    // The recompiled code does not keep a return address in ra, so the call is told apart by its arguments and by the caller's state at
    // entry: size 0xD200, align 8, v0 = 420 (the cap it has just stored, in the delay slot) and the cap word = 420. No other call matches.
    const bool pools = size == kGameCap * 64 * 2 && align == 8 && uint32_t(ctx->r2) == kGameCap && word(rdram, s.gMtxCap) == kGameCap;
    if (pools) g_heap = heap, g_big_block = 0;
    // The vertex pools' request: size 0x3E80, align 8, v0 = 500 (stored in the delay slot) and the cap word = 500, inside the course set-up.
    const bool vpools = t_setup && size == kGameVtx * 16 * 2 && align == 8 && uint32_t(ctx->r2) == kGameVtx && word(rdram, s.gVtxCap) == kGameVtx;
    if (vpools) g_big_vtx = 0;
    // One of the set-up's two display-list requests (see thps_gfx_setup_course): size = gDlBufSize, align 8.
    const bool dl = t_setup && t_dl_calls < 2 && align == 8 && size != 0 && size == word(rdram, s.gDlBufSize);
    uint32_t dl_want = size;
    // A bigger request is made only when it and every request after it will succeed: the game's allocator does not survive a failure
    // (Heap_AllocUnlocked's failure path calls 0x800B4818, which takes the heap's lock again while Mem_Alloc holds it: the game hangs; found
    // 2026-10-23 by forcing one). So the set-up's remaining requests are planned on the free list first (plan_enlarge: first fit; size +
    // 0x23 rounded to 4, plus the alignment; a size at or above the failed-size cache fails at once), and the game's own size is asked for
    // when the bigger one does not fit the plan. (Until the review of 2026-10-26 only the request at hand was checked: an enlarged first
    // list could leave no room for the second one's native size, enlarged matrix pools none for the vertex pools.)
    const bool pools_can = thps::dd::big_buffers() && !std::getenv("THPS_DD_NOPOOL");
    const PlanReq mtx_req{heap_need(kGameCap * 64 * 2), heap_need(kBigCap * 64 * 2), pools_can}, vtx_req{heap_need(kGameVtx * 16 * 2), heap_need(kBigVtx * 16 * 2), pools_can};
    if (dl) {
        if (t_dl_calls++ == 0) t_dl_native = size;
        if (thps::dd::big_buffers() && !t_dl_fallback) dl_want = std::max(t_dl_native, dl_min_bytes());
        // Tests: THPS_DD_DL_FAIL=1|2: that request of the set-up finds no room for the bigger list (the fallback runs).
        static const uint32_t fail_at = std::getenv("THPS_DD_DL_FAIL") ? uint32_t(std::atoi(std::getenv("THPS_DD_DL_FAIL"))) : 0;
        const uint32_t g = canary_on() ? kGuard : 0;
        const PlanReq dl_req{heap_need(t_dl_native + g), heap_need(dl_want + g), true};
        const bool planned = dl_want != t_dl_native && fail_at != t_dl_calls &&
                             (t_dl_calls == 1 ? plan_enlarge(rdram, heap, {dl_req, dl_req, mtx_req, vtx_req}, 2) : plan_enlarge(rdram, heap, {dl_req, mtx_req, vtx_req}, 0))[0];
        if (dl_want != t_dl_native && !planned) {
            // no room for the bigger list: the game's own size for this one and the next
            t_dl_fallback = true;
            g_dl_fallbacks.fetch_add(1);
            std::printf("[thps] draw distance: WARNING no room for a %u-byte display list (request %u of the set-up): the game's %u\n", dl_want, t_dl_calls,
                        t_dl_native);
            std::fflush(stdout);
            dl_want = t_dl_native;
        }
    }
    const bool enlarge = pools && pools_can && plan_enlarge(rdram, heap, {mtx_req, vtx_req}, 0)[0];
    const bool venlarge = vpools && pools_can && plan_enlarge(rdram, heap, {vtx_req}, 0)[0];
    const bool measure = heap == g_heap.load();
    const HeapStats before = measure ? heap_stats(rdram, heap) : HeapStats{};
    if (enlarge) {
        ctx->r5 = int32_t(kBigCap * 64 * 2);
        put_word(rdram, s.gMtxCap, kBigCap);
    }
    if (venlarge) {   // the set-up reads the cap back right after the call to place pool 2
        ctx->r5 = int32_t(kBigVtx * 16 * 2);
        put_word(rdram, s.gVtxCap, kBigVtx);
    }
    const uint32_t guard = dl && canary_on() ? kGuard : 0;   // THPS_DD_CANARY (debug): room for the guard after the list
    if (dl) {   // gDlBufSize = what this request gets (the game reads it again for the second request and every frame)
        put_word(rdram, s.gDlBufSize, dl_want);
        ctx->r5 = int32_t(dl_want + guard);
    }
    // Tests (THPS_DD_HEAP_FREE): the set-up's request, as made, from the planning's view of the free list (a WARNING if it could not fit).
    if (t_setup && (dl || pools || vpools)) thps::dd::heap_view_take(heap_need(uint32_t(ctx->r5)), dl ? "a display list" : pools ? "the matrix pools" : "the vertex pools");
    inside = true;
    thps::call_guest(s.Mem_Alloc, rdram, ctx);
    if (dl) {
        const uint32_t b = uint32_t(ctx->r2);
        if (guard && b) fill_guard(rdram, b, word(rdram, s.gDlBufSize));
        g_dl_guarded[(t_dl_calls - 1) & 1] = guard ? b : 0;
        g_dl_guard_at[(t_dl_calls - 1) & 1] = word(rdram, s.gDlBufSize);
    }
    const bool big = enlarge && uint32_t(ctx->r2) != 0;
    const bool vbig = venlarge && uint32_t(ctx->r2) != 0;
    inside = false;
    const uint32_t got = uint32_t(ctx->r2);
    if (measure) note_heap(before, heap_stats(rdram, heap), big ? kBigCap * 64 * 2 : vbig ? kBigVtx * 16 * 2 : dl ? word(rdram, s.gDlBufSize) : size, got != 0);
    if (big) g_big_block = got, pending = true;
    if (vbig) g_big_vtx = got, vtx_pending = true;
    if (venlarge || (vpools && thps::dd::big_buffers())) {
        std::printf("[thps] draw distance: vertex pools: %s at 0x%08X\n", vbig ? "4096 per frame (131072 bytes)" : "WARNING no room: the game's 500", got);
        std::fflush(stdout);
    }
    if (enlarge) {
        std::printf("[thps] draw distance: matrix pools: %s (%u bytes) at 0x%08X, heap largest free block before %u\n",
                    big ? "2048 per frame" : "the game's 420", big ? kBigCap * 64 * 2 : size, got, before.largest);
        std::fflush(stdout);
    } else if (pools && thps::dd::big_buffers()) {
        std::printf("[thps] draw distance: WARNING no room for the 2048-matrix pools: the game's 420 (%u bytes) at 0x%08X\n", size, got);
        std::fflush(stdout);
    }
    if (got == 0 && measure) {   // a failed allocation in the gfx heap: say so (the game may carry on without it)
        static std::atomic<int> warned{0};
        if (warned++ < 20) {
            const HeapStats h = heap_stats(rdram, heap);
            std::printf("[thps] draw distance: WARNING Mem_Alloc(0x%08X, %u, %u) failed: free %u bytes in %u blocks, largest %u (pools %s)\n", heap, size,
                        align, h.free_bytes, h.blocks, h.largest, big_in_use(rdram) ? "2048" : "the game's");
            std::fflush(stdout);
        }
    }
    return 1;
}

// `dd heap [reset]` (tests): the gfx heap's failed-size cache, free bytes, free blocks and the largest one, the pools' size and the cap in
// force, then the low-water marks since the start (or the last reset): least free bytes and smallest largest block after an allocation,
// the least margin between a request and the largest free block (and that request's size), failed requests, the biggest request.
std::string thps::dd::dd_game_heap(uint8_t* rdram, bool reset) {
    const uint32_t heap = g_heap.load();
    if (!heap) return "none";
    const HeapStats h = heap_stats(rdram, heap);
    HeapLow l;
    {
        std::lock_guard lock{g_low_mutex};
        l = g_low;
        if (reset) g_low = HeapLow{};
    }
    char buf[560];
    std::snprintf(buf, sizeof buf, "at 0x%08X failed %d free %u blocks %u largest %u mtx_pool %u mtx_cap %u dl %u dl_game %u dl_fallbacks %u low: calls %u free_min %u largest_min %u margin_min %lld "
                  "(size %u) failed_calls %u biggest %u vtx_pool %u vtx_cap %u view_fail %u", heap, int32_t(h.failed), h.free_bytes, h.blocks, h.largest, big_in_use(rdram) ? kBigCap : word(rdram, sym().gMtxCap),
                  word(rdram, sym().gMtxCap), word(rdram, sym().gDlBufSize), g_dl_native.load(), g_dl_fallbacks.load(), l.calls, l.calls ? l.free_min : 0, l.calls ? l.largest_min : 0,
                  l.calls ? (long long)l.margin_min : 0LL, l.margin_size, l.failed, l.biggest, big_vtx_in_use(rdram) ? kBigVtx : word(rdram, sym().gVtxCap),
                  word(rdram, sym().gVtxCap), thps::dd::heap_view_fails());
    return buf;
}

// `dd item N` (tests): the item's hidden bits now, the zone record (after the draw call's stale-record check), event ownership, and
// whether "full" draws it this frame (the same rule as thps_world_draw_items).
std::string thps::dd::dd_game_item(uint8_t* rdram, uint32_t index) {
    const uint32_t list = thps::sym().gWorldItems;
    const uint32_t n = word(rdram, list + 16), arr = word(rdram, list + 12);
    if (n == 0 || n > 8192 || index >= n) return "none";
    zone_sync(rdram, list);
    const uint16_t f = *flag_ptr(rdram, arr, index);
    const uint8_t zone = index < g_zone.bits.size() ? g_zone.bits[index] : 0, event = index < g_zone.event.size() ? g_zone.event[index] : 0;
    const uint16_t unhidden = thps::dd::unhide_everything() ? uint16_t(f & 0x41) : 0;
    uint32_t named = 0;
    for (uint8_t e : g_zone.event) named += e;
    char buf[160];
    std::snprintf(buf, sizeof buf, "flags 0x%04X zone 0x%02X event %u drawn %d named %u gen %llu", f, zone, event, ((f & 0x41) & ~unhidden) == 0, named,
                  (unsigned long long)g_zone.gen);
    return buf;
}

// `dd own N` (tests): item N is event-owned from now on, as World_FindItem would make it (thps_world_find_item).
std::string thps::dd::dd_game_own(uint8_t* rdram, uint32_t index) {
    const uint32_t list = thps::sym().gWorldItems;
    const uint32_t n = word(rdram, list + 16);
    if (n == 0 || n > 8192 || index >= n) return "none";
    zone_sync(rdram, list);
    if (index >= g_zone.event.size()) return "none";
    g_zone.event[index] = 1;
    return dd_game_item(rdram, index);
}
