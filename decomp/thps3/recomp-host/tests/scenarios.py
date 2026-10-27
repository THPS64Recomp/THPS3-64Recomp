"""Scenario definitions for the THPS3 recomp regression suite (data only; engine in run.py).

Checkpoints describe a screen: the expected RT64 frame size and one or more regions that are
compared with a reference frame recorded locally (build/tests/refs/<name>.png, ROM-derived,
never committed). Regions are fractions of the frame, so they don't depend on the resolution;
each is reduced to a gw x gh luma grid, normalised (zero mean, unit std: fades and brightness
don't matter) and compared by mean absolute difference: 0 = same picture, ~1.1 = unrelated.
`tol` is the largest distance that still counts as a match. `tests/run.py --check-refs`
prints, for each checkpoint, how far the *other* references are (as distance/tol; must stay
well above 1) -- run it after recording or after changing a region.

`record` says how --record captures the reference when none exists: ("frame", N) = at
displayed frame N; ("settle", N) = N displayed frames after the step's input.

Menus are navigated without references: the highlighted entry is gold/red (harness.gold),
the others blue/white, so the cursor row is the strongest gold band inside `y_range`, mapped to
the nearest of `rows` (centres as fractions of the frame height).
"""

# Per-game constants used by run.py (THPS3; a port edits these and the checkpoints below).
GAME = dict(
    trick_counters=False,      # THPS3's per-trick counters are not located: the "trick" expectation is not available
    press_limit=40,            # START on the logo screen is ignored for its first 7 s, the demo needs another
    skate_watch=40,            # 2-frame polls to watch after the inputs (80 frames; was 20, see LOG P3)
    skate_tries=6,
    skate_warn_only=True,      # +Skater_PhysState also toggles every ~48 frames with NO input (idle), so "air" cannot fail the suite (LOG P3)
    rev0_header=(b"THPS3", b"NTQP"),
)

# name: size, regions [(region (x0, y0, x1, y1), gw, gh, tol)], record
# A region (region, "mask", luma_min, min_frac) is a template match instead: at least min_frac
# of the reference's pixels brighter than luma_min must have the same colour (for HUD text over
# a moving 3D background; harness.mask_score).
# A region (region, "color", (rmin, rmax, gmin, gmax, bmin, bmax), min_frac) counts the pixels inside a colour box (a fixed-colour HUD element
# on a moving background). `regions=[]` = size-only checkpoint (any frame of that size, e.g. a 3D frame; needs no reference).
CHECKPOINTS = {
    # Front end (640x474: 640x480 VI with the first/last lines cropped by the VI timing).
    "title":          dict(size="640x474", regions=[((0.0, 0.0, 1.0, 1.0), 16, 12, 0.35)], record=("frame", 900),
                           what="logo screen (Tony Hawk's Pro Skater 3, Activision, Neversoft, Edge of Reality) after the legal text"),
    # No regions: any frame of this size counts (the attract demo that follows the logos is 3D, 320x237).
    "demo3d": dict(size="320x237", regions=[], record=("settle", 1), what="any 3D frame (the attract demo)"),
    "main_menu": dict(size="640x474", regions=[((0.11, 0.17, 0.51, 0.24), "mask", 170, 0.7)], record=("settle", 90),
                           what="MAIN MENU: CAREER MODE highlighted"),
    "career_menu": dict(size="640x474", regions=[((0.27, 0.27, 0.72, 0.35), "mask", 170, 0.7)], record=("settle", 90),
                           what="CAREER MENU: CONTINUE CAREER (grey) / NEW CAREER / LOAD CAREER"),
    "career_menu_loaded": dict(size="640x474", regions=[((0.27, 0.27, 0.72, 0.35), "mask", 170, 0.7), ((0.38, 0.35, 0.66, 0.41), "mask", 170, 0.5)], record=("settle", 90),
                           what="CAREER MENU after loading a career: CONTINUE CAREER enabled"),
    "career_screen": dict(size="640x474", regions=[((0.11, 0.17, 0.51, 0.24), "mask", 170, 0.7)], record=("settle", 90),
                           what="CAREER: CONTINUE / CHOOSE SKATER / UPGRADES / TRICKS / DECKS, Tony Hawk"),
    "level_select": dict(size="640x474", regions=[((0.52, 0.10, 0.92, 0.17), "mask", 170, 0.7)], record=("settle", 90),
                           what="LEVEL SELECT list: Foundry on top"),
    "goals": dict(size="640x474", regions=[((0.35, 0.16, 0.65, 0.22), "mask", 170, 0.7)], record=("settle", 90),
                           what="Foundry goals sheet, A TO PLAY"),
    "options_menu": dict(size="640x474", regions=[((0.27, 0.17, 0.72, 0.26), "mask", 170, 0.7)], record=("settle", 90),
                           what="OPTIONS list: CONTROLLER ONE .. BACK"),
    "pak_menu": dict(size="640x474", regions=[((0.26, 0.34, 0.73, 0.42), "mask", 170, 0.7)], record=("settle", 90),
                           what="OPTIONS > CONTROLLER PAK: LOAD DATA / SAVE DATA / LOAD REPLAY / BACK"),
    "enter_name": dict(size="640x474", regions=[((0.05, 0.12, 0.95, 0.55), "mask", 170, 0.7)], record=("settle", 60),
                           what="name entry (letter grid)"),
    "save_ok": dict(size="640x474", regions=[((0.25, 0.45, 0.75, 0.54), "mask", 150, 0.7)], record=("settle", 150),
                           what="SAVE SUCCESSFUL. OK"),
    "load_data_empty": dict(size="640x474", regions=[((0.2, 0.47, 0.8, 0.53), "mask", 170, 0.7)], record=("settle", 120),
                           what="LOAD DATA on a blank pak: the empty-pak message"),
    "load_data_list": dict(size="640x474", regions=[((0.2, 0.40, 0.8, 0.62), "mask", 120, 0.5)], record=("settle", 120),
                           what="LOAD DATA: the saved note listed"),
    # In level (320x237). The HUD bracket of the special meter is fixed; everything behind it moves.
    "in_level":       dict(size="320x237", regions=[((0.07, 0.18, 0.33, 0.24), "color", (0, 120, 0, 120, 150, 255), 0.008)], record=("settle", 420),
                           what="in level: the SPECIAL meter bracket of the HUD (blue)"),
    # Native frame of Foundry, paused PAUSE_POLLS input polls after the run flag (gRunActive) went to 1 (see PAUSE_AFTER_RUN_START);
    # recorded at 4:3, at 21:9 the game must show the very same frame (the camera must not move). Re-recorded 2026-10-14 (the anchor changed).
    "paused_w90":     dict(size="320x237", regions=[((0.0, 0.25, 1.0, 1.0), 32, 18, 0.12)], record=("settle", 30),
                           what="Foundry paused PAUSE_POLLS game frames after the run starts (the same game frame in every run; the skater rolls, so the frame is exact; camera reference, 4:3)"),
    "pause":          dict(size="320x237", regions=[((0.27, 0.09, 0.73, 0.14), "mask", 150, 0.6), ((0.10, 0.80, 0.90, 0.90), "mask", 150, 0.7)], record=("settle", 30),
                           what="PAUSED menu: header and the B / A prompts (CONTINUE RETRY VIEW GOALS CHANGE SOUND LEVELS END RUN)"),
}

MENUS = {
    # Highlighted entry = orange bar (harness.gold). Rows are centres as fractions of the frame height; the
    # cursor skips greyed entries (OPTIONS > CHEATS, index 4, is greyed until unlocked: never highlighted).
    "main":    dict(rows=[0.271 + 0.0548 * i for i in range(7)], y_range=(0.20, 0.68),
                    items=["CAREER MODE", "SINGLE SESSION", "FREE SKATE", "2 PLAYER", "CREATE SKATER", "PARK EDITOR", "OPTIONS"]),
    "career":  dict(rows=[0.38, 0.434, 0.489], y_range=(0.30, 0.56),
                    items=["CONTINUE CAREER", "NEW CAREER", "LOAD CAREER"]),
    "options": dict(rows=[0.268 + 0.0548 * i for i in range(10)], y_range=(0.20, 0.80),
                    items=["CONTROLLER ONE", "CONTROLLER TWO", "SOUND LEVELS", "CONTROLLER PAK", "CHEATS", "HIGH SCORES",
                           "GAP CHECKLIST", "DISPLAY OPTIONS", "CREDITS", "BACK"]),
    "pak":     dict(rows=[0.419 + 0.0548 * i for i in range(4)], y_range=(0.36, 0.66),
                    items=["LOAD DATA", "SAVE DATA", "LOAD REPLAY", "BACK"]),
    "pause":   dict(rows=[0.211, 0.27, 0.333, 0.392, 0.456], y_range=(0.15, 0.50),
                    items=["CONTINUE", "RETRY", "VIEW GOALS", "CHANGE SOUND LEVELS", "END RUN"]),
}

# Steps (all waits are in displayed frames or checkpoint matches, never wall-clock presses):
#   ("wait_for", cp)                 poll RT64 frames until checkpoint cp matches
#   ("go", BUTTON, from_cp, to_cp)   press BUTTON until to_cp matches (re-pressed only while
#                                    from_cp still matches, i.e. the press was dropped)
#   ("menu", menu, index)            move the cursor (DOWN) until entry `index` is highlighted
#   ("menu_at", menu, index)         assert the cursor is on entry `index` (no input)
#   ("go_watch", BUTTON, FROM_CP, ADDR, VALUE)  press, and wait until the HOST'S GAME THREAD sees the word at ADDR become VALUE (the exact poll)
#   ("press_when", ADDR, GE, BUTTON) the game thread presses BUTTON at the first poll where the word at ADDR is >= GE (a tick counter: cam-43 / cam-219)
#   ("wait_peek", ADDR, VALUE[, S])  frame by frame until the game word at ADDR ("@gRunActive") equals VALUE
#   ("press_after", BUTTON, N)       press exactly N game input polls after the previous press finished
#   ("press", BUTTON)                one press (3 polls held, 3 released)
#   ("menu_name_end",)               name-entry grid: move from the first letter to END
#   ("wait", frames)
#   ("dl", tasks, min_tris)          display-list stats of the next gfx tasks: in-level 3D
#   ("audio", frames, min_rms_dbfs)  RMS of the game's audio output over a window
#   ("fps", seconds, min_median)     median displayed fps from the perf log (warn-only if the
#                                    machine is overloaded: load avg > 2 x CPUs)
#   ("pak_snapshot",) / ("pak_changed",)   hash of <config>/saves/thps3_pak1.mpk before/after
#   ("pak_log", regex)               a host "[thps] pak" log line matching regex was printed
#   ("not_cp", cp)                   the current frame must NOT match cp (negative check)
#   ("max_frame", N)                 the checkpoint just matched came within N displayed frames of boot
#   ("log", regex)                   a host "[thps] skip intro|input|launcher" line matching regex
#   ("fps_overlay", seconds, tol)    Show FPS counter lines agree with the perf log's fps (median, +-tol)
#   ("vpad", "attach")               a virtual SDL game controller (no hardware needed)
#   ("vpress", NAME)                 press + release one of its buttons (SDL names: a, dpdown, y ...)
#   ("bind", INPUT, FIELDS)          replace a binding and save it (controls.cfg), as a user edit would
#   ("file_contains", FILE, regex)   <config>/FILE has a match
#   ("binding_saved", INPUT, B, rx)  the binding was saved (controls.cfg line rx, or controls.json button B)
#   ("audio_max", frames, max_rms)   audio output RMS at most max_rms dBFS (volume setting)
#   ("crash",)                       --control crash: exit 139 and a crash.log naming game code (last step)
#   ("keep_present", NAME)           copy the newest present capture to <out>/NAME.png (UI evidence)
#   ("json_value", FILE, KEY, VALUE) <config>/FILE (recompui settings JSON) has KEY = VALUE
#   ("loadrom", "rom"|"rev0", regex) launcher Load ROM (--control loadrom) with the suite's ROM or a
#                                    synthetic v1.0 header; the host log matches regex
#   ("pad_records", INPUT, [ids])    while INPUT ("vpad:NAME" or N64 buttons) is held, exactly these
#                                    records of the game's PlayStation-style pad layer are pressed
#                                    (0 grind, 1 flip, 2 grab, 3 ollie, ...; run.py)
#   ("skate", INPUTS, "air")         vpad inputs on the ground; the skater gets airborne (CBruce via the skater
#                                    pointer @gSkater; no trick counters located for THPS3)
#   ("edges", N, max)                border bands of the next N presented frames change by <= max
#   ("present_wide", "WxH", max)     newest present capture (session `present_every`) is WxH and at
#                                    most `max` of the bands outside the central 4:3 is unrendered
#   ("hfr_motion", SEC, STICK, checks) / ("hfr_cut",) / ("latency", "A/B", N, MAX_MS)
#                                    high frame rate + input latency (tests/hfr_steps.py)

from hfr_steps import ids_phases as IDS_PHASES, ids_clip as IDS_CLIP  # noqa: E402

# Inside a controls screen the OPTIONS list is not shown (no reference frame of the screens themselves; THPS1's options-controls).
IN_SCREEN = [("wait", 40), ("shot", "in_controls_screen"), ("not_cp", "options_menu")]

BOOT_TO_MENU = [
    ("wait_for", "title"),
    # Do NOT press START on the logo screen: pressing it there keeps the screen up for much longer (measured: the
    # logos stay ~17 s with a press every 40 frames, ~8 s without). The logos end by themselves in the attract demo
    # (3D, 320x237); START in the demo opens the main menu.
    ("wait_for", "demo3d"),
    ("go", "START", "demo3d", "main_menu"),
]

# main_menu -> CAREER MODE -> NEW CAREER -> (CAREER screen) CONTINUE -> level select -> goals
CAREER_TO_GOALS = [
    ("go", "A", "main_menu", "career_menu"),
    ("menu_at", "career", 1),                    # no career yet: cursor on NEW CAREER
    ("go", "A", "career_menu", "career_screen"),
    ("go", "A", "career_screen", "level_select"),
    ("go", "A", "level_select", "goals"),
]

# cam-43 / cam-219: A on the goals sheet starts the run; go_watch waits for the run flag (gRunActive 0 -> 1: the level is playing, whatever
# the load time took), then START is pressed by the host's game thread the moment the level's TICK counter reaches RUN_TICKS_PAUSE. The pause lands
# on the same game tick in every run (counter 65 frozen in 8 of 8 runs, identical pictures), unlike a pause N polls or N frames after the start
# (counter 62 / 64 / 67, pictures up to 1.2 x the tolerance apart): the game's update advances 2 ticks per displayed frame, but sometimes 0 or 4.
# RUN_TICKS = word 0x800EA538 of THPS3 USA: 0 at the run start, +2 per game frame (60 Hz ticks); a mirror of it is at 0x800EAE50 (found by
# diffing RAM of runs whose paused pictures differed; 0x800E0D1C, the word before gRunActive, is the run clock in seconds, from the real clock).
RUN_TICKS = "0x800EA538"
RUN_TICKS_PAUSE = 60      # about a second into the run: the skater is in view and rolling
PAUSE_AFTER_RUN_START = [
    ("go_watch", "A", "goals", "@gRunActive", 1),
    ("press_when", RUN_TICKS, RUN_TICKS_PAUSE, "START"),
    ("wait", 30),
]

# Game frames to wait after a checkpoint before a check that needs the screen to have stopped animating (e169_menus): the front end's
# slide-ins end ~25 game frames after the press that opened the screen; 60 leaves a wide margin and costs 2 s per screen.
SETTLE = 60

# Sessions = one host instance each; scenarios in a session run in order on the same instance
# (a failure skips the rest of that session). `fresh_pak` starts from a blank Controller Pak.
# 2 PLAYER > TRICK ATTACK with two virtual pads (pad 1 = port 1, pad 2 = port 2) up to the split-screen run; then each pad reaches its own port.
_TWO_PADS_TO_LEVEL = [
    *BOOT_TO_MENU,
    ("menu", "main", 3),
    ("vpad", "attach"), ("vpad2", "attach"),
    ("vpress", "leftshoulder"), ("vpress2", "leftshoulder"),           # pad 1 = port 1, pad 2 = port 2
    ("log_n", r"Virtual Controller takes port 2", 1),
    ("wait", 30),
    *[x for _ in range(3) for x in (("vpress", "a"), ("wait", 150))],   # the main menu's 2 PLAYER, TRICK ATTACK, PLAYER ONE CONTINUE
    ("vpress2", "a"), ("wait", 150),                                    # PLAYER TWO CONTINUE: port 2 (pad 1's A does nothing there)
    ("vpress", "a"), ("wait", 60), ("vpress2", "a"), ("wait", 150),   # HANDICAP: each player accepts his own
    *[x for _ in range(3) for x in (("vpress", "a"), ("wait", 150))],   # LEVEL SELECT, rules, SELECT TIME
    ("wait_peek", "@gRunActive", 1, 60),
]
_TWO_PADS_PORTS = [
    ("ctl", "vpad2 button leftshoulder 1"), ("wait", 8),
    ("ctl_match", "inputstate", r"last=0x0000 last2=0x0020$"),        # pad 2 reaches port 2 only
    ("ctl", "vpad2 button leftshoulder 0"),
    ("ctl", "vpad button rightshoulder 1"), ("wait", 8),
    ("ctl_match", "inputstate", r"last=0x0010 last2=0x0000$"),        # pad 1 port 1 only
    ("ctl", "vpad button rightshoulder 0"),
]

SESSIONS = [
    dict(name="frontend", config="suite-config", fresh_pak=True, wav=True, scenarios=[
        ("boot_title", "boot: Expansion Pak notice, legal text, then the logo screen (overlay t2_intro)", [
            ("wait_for", "title"),
            ("edges", 20, 4.0),
        ]),
        ("main_menu",  "logos -> START (attract demo) -> START -> MAIN MENU (overlay t3_mainmenu)", [*BOOT_TO_MENU[1:]]),
        ("career_level", "CAREER MODE -> NEW CAREER -> Foundry loaded, HUD + 3D", [
            *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            ("dl", 10, 500),
        ]),
        ("level_audio", "in-level audio is not silent", [("wait", 60), ("audio", 150, -40.0)]),
        ("level_fps",   "in-level median fps >= 28", [("fps", 10, 28.0)]),
        # THPS3's pad layer (LOG H3): C-up/left/right/down = records 0/1/2/3 (grind/flip/grab/ollie), N64 A = ollie (3) and
        # N64 B = flip (1) in the skating code too, L = 4+5 (spin left + nollie), R = 6+7 (spin right + switch, and REVERT).
        # thps-xbox: south = A + C-down (ollie), west = C-left (flip), east = C-right (grab; its N64 B is dropped while the skater
        # is under control, src/run_state.cpp; in every other screen C-right is dropped and B = back stays), north = C-up (grind), LB = L, RB / RT = R.
        ("level_controls", "default pad bindings reach the game's trick buttons (A/B are ollie/flip too)", [
            ("vpad", "attach"),
            ("pad_records", "A", [3]),            # N64 A: ollie (also menu accept)
            ("pad_records", "B", [1]),            # N64 B: flip (also menu back)
            ("pad_records", "CD", [3]),
            ("pad_records", "CL", [1]),
            ("pad_records", "CR", [2]),
            ("pad_records", "CU", [0]),
            ("pad_records", "L", [4, 5]),         # spin left + nollie
            ("pad_records", "R", [6, 7]),         # spin right + switch; revert
            ("pad_records", "vpad:a", [3]),       # south (Xbox A) = A + C-down -> ollie
            ("pad_records", "vpad:x", [1]),       # west (Xbox X) = C-left -> flip
            ("pad_records", "vpad:b", [2]),       # east (Xbox B) = C-right -> grab ONLY (B dropped in 3D, no flip)
            ("pad_records", "vpad:y", [0]),       # north (Xbox Y) = C-up -> grind
            ("pad_records", "vpad:rightshoulder", [6, 7]),   # RB = R: spin right / revert
            ("pad_records", "vpad:leftshoulder", [4, 5]),    # LB = L: spin left / nollie
        ]),
        ("level_ollie", "Xbox A held and released: the skater ollies (in air)", [
            ("skate", [("vpad", "a", 1), ("wait", 10), ("vpad", "a", 0)], "air"),
        ]),
        ("level_grab", "Xbox A, then B + right and Y in the air: the level keeps running", [
            ("skate", [("vpad", "a", 1), ("wait", 10), ("vpad", "a", 0), ("wait", 3),
                       ("axis", "leftx", 32767), ("vpad", "b", 1), ("wait", 6), ("vpad", "b", 0), ("vpad", "y", 1), ("wait", 4),
                       ("vpad", "y", 0), ("axis", "leftx", 0)], "air"),
            ("wait", 30),
            ("wait_for", "in_level"),
        ]),
        ("border_stable", "pause menu: the border bands of the presented frames don't flicker", [
            ("go", "START", "in_level", "pause"),
            ("wait", 20),
            ("edges", 45, 4.0),
        ]),
        # The pause menu draws the 3D level behind it and the game says "B TO GO BACK". Xbox B (east) is N64 B + C-right; the host used to drop
        # B whenever a 3D view was drawn, so back never arrived here (nor on the career screen, which shows a 3D skater). Now B is dropped only
        # while the skater is under control (src/run_state.cpp, the game's own run flag) and in every other screen C-right is dropped instead.
        ("pause_back", "pause menu: Xbox B (east) goes back = resumes the level (the HUD is drawn in the pause screen too: the pause menu must be gone)", [
            ("vpress", "b"), ("wait", 30), ("wait_for", "in_level"), ("not_cp", "pause"),
        ]),
        ("level_b_after_resume", "after the resume the skater is under control again: east sends C-right only (grab, no flip)", [
            ("pad_records", "vpad:b", [2]),
        ]),
        ("pause_resume", "pause menu: START resumes the level (the HUD is drawn in the pause screen too: the pause menu must be gone)", [
            ("go", "START", "in_level", "pause"),
            ("press", "START"), ("wait", 30), ("wait_for", "in_level"), ("not_cp", "pause"),
        ]),
        # Hand play 2026-10-13: "freezes after level retry". PAUSE > RETRY must put the skater back at the start and the level must
        # keep running (new gfx tasks with 3D triangles keep coming, the HUD returns).
        ("pause_retry", "pause menu > RETRY twice in a row: the level restarts and keeps running each time (was: every thread stuck in osRecvMesg)", [
            ("go", "START", "in_level", "pause"),
            ("menu", "pause", 1),
            ("press", "A"),
            ("wait", 60),
            ("wait_for", "in_level"),
            ("dl", 30, 500),
            ("wait", 90),
            ("go", "START", "in_level", "pause"),
            ("menu", "pause", 1),
            ("press", "A"),
            ("wait", 60),
            ("wait_for", "in_level"),
            ("dl", 30, 500),
            ("wait", 120),
            ("dl", 30, 500),
        ]),
    ]),
    # The career screen draws a 3D skater (so a "3D view is drawn" test counted it as skating) and shows "B BACK": Xbox B (east) is N64 B +
    # C-right and the B used to be dropped there. Own session: NEW CAREER creates a career, which changes the career menu's first cursor
    # position for the frontend session's career_level.
    dict(name="career-back", config="cb-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden"], scenarios=[
        ("career_back", "CAREER MODE > NEW CAREER > career screen (3D skater): Xbox B (east) goes back to the career menu, then to the main menu", [
            *BOOT_TO_MENU,
            ("go", "A", "main_menu", "career_menu"),
            ("menu_at", "career", 1),
            ("go", "A", "career_menu", "career_screen"),
            ("vpad", "attach"),
            ("vpress", "rightstick"),             # claims port 1 (a virtual controller takes a port on its first press)
            ("vpress", "b"),
            ("wait_for", "career_menu"),
            ("vpress", "b"),
            ("wait_for", "main_menu"),
        ]),
    ]),
    # Evidence frames for the hand-play answers (media/playtest-answers): the same screens under different --aspect / --refresh
    # (THPS_TEST_EXTRA_ARGS="--aspect original --refresh original" etc.); not part of the pass/fail suite.
    dict(name="answers", config="answers-config", fresh_pak=True, wav=False, present_every=3,
         args=["--skip-intro", "--hidden", "--window", "1280x720", "--res-scale", "2"], scenarios=[
        ("ans_menu", "evidence: main menu, career screens", [
            *BOOT_TO_MENU, ("wait", 40), ("keep_present", "a_main_menu"),
            ("go", "A", "main_menu", "career_menu"), ("wait", 30), ("keep_present", "a_career_menu"),
            ("menu_at", "career", 1),
            ("go", "A", "career_menu", "career_screen"), ("wait", 30), ("keep_present", "a_career_screen"),
            ("go", "A", "career_screen", "level_select"), ("wait", 30), ("keep_present", "a_level_select"),
            ("go", "A", "level_select", "goals"), ("wait", 30), ("keep_present", "a_goals"),
        ]),
        ("ans_level", "evidence: in level HUD (special meter), pause", [
            ("go", "A", "goals", "in_level", 90), ("wait", 120), ("keep_present", "a_level0"),
            ("vpad", "attach"),
            ("keep_present", "a_level1"), ("wait", 30), ("keep_present", "a_level2"),
            ("go", "START", "in_level", "pause"), ("wait", 30), ("keep_present", "a_pause"),
        ]),
    ]),
    # Hand play 2026-10-13, the strip left of the 16:9 picture: every presented frame of ~3 s in the level; two of three framebuffers
    # kept stale 3D in the unpainted left ring (dl_fixes.cpp lores_ring_clear). Was: left edge at column 10 or 16 of 640.
    dict(name="ringprobe", config="ringprobe-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--window", "1280x720", "--present-size", "640x360"], scenarios=[
        ("ring_level", "presented frames in the level: the picture's left/right edge does not move from frame to frame (stale strip in a framebuffer's border ring)", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            ("wait", 120),
            ("pcap", 90, "ring_level"),
            ("ring_check", "ring_level", 2),
        ]),
    ]),
    # Skater jitter / frame pop (hand play 2026-10-13): which world transforms RT64 pairs between game frames while skating at 60 Hz
    # (P = paired and interpolated, S = skipped, U = unpaired: shown at the game rate), where the skater lives, camera cuts logged.
    dict(name="jitter", config="jitter-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden", "--refresh", "60", "--present-size", "480x360"], scenarios=[
        ("jitter_probe", "evidence: pairing statistics while skating (host.log: hfrdbg, hfr, hfrcam, peek @gSkater)", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            ("wait", 90),
            ("cpu", 8),
            ("vpad", "attach"),
            ("ctl", "peek @gSkater 4"),
            ("ctl", "hfrcam"),
            ("ctl", "hfr"),
            ("vpress", "dpup"),
            ("ctl", "vpad axis lefty -32000"),
            ("wait", 45),
            ("ctl", "hfrdbg"), ("wait", 3), ("ctl", "hfrdbg"), ("wait", 5), ("ctl", "hfrdbg"),
            ("ctl", "hfr"), ("ctl", "hfrcam"),
            ("wait", 120),
            ("ctl", "hfr"), ("ctl", "hfrcam"),
            ("ctl", "vpad axis lefty 0"),
        ]),
    ]),
    # Matrix-group IDs (src/interp_ids.cpp): pairing statistics + idsdump (RT64's verdict per world transform joined with the display-list walk).
    dict(name="idsprobe", config="idsprobe-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden", "--refresh", "60", "--present-size", "480x360"], scenarios=[
        ("ids_probe", "evidence: pairing statistics standing / skating / turning / ollie, then idsdump", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            ("ctl", "idsscan 1"),
            ("go", "A", "goals", "in_level", 90),
            *IDS_PHASES(40, True),
        ]),
    ]),
    # Performance of the matrix IDs (docs/interpolation-ids.md, "Performance"): VISIBLE window, no capture; IDs off / on interleaved, a present-dump block and an idsstat block
    # for the cost of those debug modes, and a --refresh original baseline in the second session.
    dict(name="idsbench", config="idsbench-config", fresh_pak=True, wav=False,
         args=["--skip-intro"] + __import__("os").environ.get("THPS_BENCH_ARGS", "").split(), scenarios=[
        ("ids_bench", "performance: fps, frame-time percentiles, ID walk cost; IDs off/on interleaved (notes)", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            ("vpad", "attach"), ("wait", 30),
            ("bench", 12, "keep"),                       # warm-up
            ("bench", 20, "off"), ("bench", 20, "on"), ("bench", 20, "naive"), ("bench", 20, "off"), ("bench", 20, "on"), ("bench", 20, "naive"),
            ("bench", 20, "off"), ("bench", 20, "on"), ("bench", 20, "naive"),
        ]),
    ]),
    dict(name="idsbench-orig", config="idsbench-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--refresh", "original"] + __import__("os").environ.get("THPS_BENCH_ARGS", "").split(), scenarios=[
        ("ids_bench_orig", "performance baseline: --refresh original (30 fps, no interpolation)", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            ("vpad", "attach"), ("wait", 30),
            ("bench", 12, "keep"),
            ("bench", 20, "keep"), ("bench", 20, "keep"), ("bench", 20, "keep"),
        ]),
    ]),
    # Walk time over a whole boot (front end, loading screens, level start) and a RETRY (camera cut + level restart): the ten slowest walks with their CPU time (`ids slow`).
    dict(name="idsload", config="idsload-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--refresh", "60"], scenarios=[
        ("ids_load", "walk times over front end, level load and a camera cut (notes)", [
            ("ctl", "ids slowreset"),
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            ("wait", 60),
            ("ctl", "ids slow"),
            ("ctl", "ids slowreset"),
            ("hfr_cut",), ("wait", 90),
            ("ctl", "ids slow"),
        ]),
    ]),
    dict(name="idsclip", config="idsclip-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--refresh", "60", "--present-size", "480x360"], scenarios=[
        ("ids_clip", "evidence: every composited frame of ~8 s of skating (THPS_IDS=1: IDs on), into build/ids/clip", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            *IDS_CLIP(),
        ]),
    ]),
    # Hand play 2026-10-13: "often flashing strip of screen on top left side of screen in 16x9 mode". Border bands (left/right/top/bottom)
    # of the presented 16:9 frame on each kind of screen: the 640x480 front end (ring of the colour buffer), the in-level view, the pause menu.
    dict(name="edges169", config="edges169-config", fresh_pak=True, wav=False,
         args=["--aspect", "16:9", "--window", "1280x720", "--skip-intro", "--hidden"], scenarios=[
        ("e169_title", "16:9: logo screen, border bands stable", [("wait_for", "title"), ("edges", 30, 4.0, "rows")]),
        # Each screen's check starts SETTLE game frames after its checkpoint: a screen animates in after the checkpoint's text is up (the Career
        # screen's legend slides up from y 693 to 665, ~20 game frames after the A press; level select and goals the same), and the poll that
        # sees the checkpoint is a variable time into that (Windows 2026-10-14: row 693 changes by 16.9, 4 of 4; macOS passes only when its
        # polls land late). The animations are game-frame driven, so a fixed frame count is the same on every machine.
        ("e169_menus", "16:9: main menu, career menu, career screen, level select, goals: border bands stable", [
            ("wait_for", "demo3d"),            # the attract demo is 3D and moves: not measured
            ("go", "START", "demo3d", "main_menu"),
            ("wait", SETTLE), ("edges", 45, 4.0, "rows"),
            ("go", "A", "main_menu", "career_menu"),
            ("wait", SETTLE), ("edges", 45, 4.0, "rows"),
            ("menu_at", "career", 1),
            ("go", "A", "career_menu", "career_screen"),
            ("wait", SETTLE), ("edges", 45, 4.0, "rows"),
            ("go", "A", "career_screen", "level_select"),
            ("wait", SETTLE), ("edges", 45, 4.0, "rows"),
            ("go", "A", "level_select", "goals"),
            ("wait", SETTLE), ("edges", 45, 4.0, "rows"),
        ]),
        ("e169_level", "16:9: the pause menu over the level: border bands stable (the moving level itself: ringprobe)", [
            ("go", "A", "goals", "in_level", 90),
            ("wait", 60),
            ("go", "START", "in_level", "pause"),
            ("wait", 20),
            ("edges", 60, 4.0, "rows"),
        ]),
    ]),
    # Widescreen: the RDRAM frames the checkpoints compare stay native 4:3, so the 4:3 references apply;
    # the present capture checks the wide picture. Own config dir.
    dict(name="widescreen", config="ws-config", fresh_pak=True, wav=False, present_every=30,
         args=["--aspect", "16:9", "--window", "1280x720", "--res-scale", "2", "--msaa", "4", "--hidden", "--skip-intro"], scenarios=[
        ("ws_menu", "16:9: boot to the main menu (native frames unchanged)", [*BOOT_TO_MENU]),
        ("ws_level", "16:9: Foundry fills the wide frame (present capture), 30 fps", [
            *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            ("dl", 10, 500),
            ("wait", 60),
            ("present_wide", "1280x720", 0.15),
            ("fps", 10, 28.0),
        ]),
    ]),
    # OPTIONS > CONTROLLER ONE / CONTROLLER TWO (the game's controls screens; THPS1's soft lock was its PLAYER 2 CONTROLS, LOG "PLAYER 2
    # CONTROLS"). As in THPS2, CONTROLLER TWO opens only for port 2's A (and CONTROLLER ONE only for port 1's), so with one pad it could
    # not be opened; the host's p2_menu_mirror (game.toml; port 2 = port 1 in menus while no second pad is attached, input.cpp) opens it.
    # Inside a controls screen the OPTIONS list is not shown (not_cp options_menu); leaving must bring OPTIONS back.
    dict(name="options-controls", config="optctl-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden", "--keyboard"], scenarios=[
        ("ctlscr_p1_pad", "pad: A enters CONTROLLER ONE, B (east) leaves", [
            *BOOT_TO_MENU,
            ("menu", "main", 6),
            ("go", "A", "main_menu", "options_menu"),
            ("menu_at", "options", 0),
            ("vpad", "attach"), ("vpress", "leftshoulder"),              # the first press claims port 1 (a button that does nothing here)
            ("vpress", "a"), *IN_SCREEN,
            ("vpress", "b"), ("wait_for", "options_menu"),
            ("menu_at", "options", 0),
        ]),
        ("ctlscr_p2_pad", "ONE pad: A opens CONTROLLER TWO (it waited for port 2's A: did nothing), B leaves", [
            ("wait", 30), ("vpress", "dpdown"), ("menu_at", "options", 1),
            ("vpress", "a"), *IN_SCREEN,
            ("vpress", "b"), ("wait_for", "options_menu"),
            ("shot", "after_ctl2"),
        ]),
        ("ctlscr_p2_kbd", "keyboard only: Space opens CONTROLLER TWO, D leaves", [
            ("wait", 30), ("menu", "options", 1),
            ("ctl", "key Space"), *IN_SCREEN,
            ("ctl", "key D"), ("wait_for", "options_menu"),
        ]),
        ("ctlscr_p2_two_pads", "TWO pads: pad 1's A does not open CONTROLLER TWO (no mirror), pad 2's A does and its B leaves; "
                               "pad 2 unplugged inside: pad 1's B leaves", [
            ("vpad2", "attach"), ("vpress2", "leftshoulder"),
            ("log_n", r"Virtual Controller takes port 2", 1),
            ("wait", 30), ("menu", "options", 1),
            ("vpress", "a"), ("wait", 40), ("wait_for", "options_menu"), ("menu_at", "options", 1),
            ("vpress2", "a"), *IN_SCREEN,
            ("vpress2", "b"), ("wait_for", "options_menu"),
            ("wait", 30), ("menu", "options", 1), ("vpress2", "a"), *IN_SCREEN,
            ("vpad2", "detach"), ("wait", 20),
            ("vpress", "b"), ("wait_for", "options_menu"),
        ]),
    ]),
    # 2 PLAYER: after PLAYER ONE has picked, PLAYER TWO's CONTINUE / CHOOSE SKATER reads only port 2, so with ONE pad (or the keyboard)
    # neither A nor B did anything there: a soft lock (quit the app). p2_menu_mirror: port 2 carries port 1's input while the run flag
    # gRunActive is 0 (THPS3's menus all draw a live 3D background, so "no 3D drawn" is never true here), not in the split-screen run.
    # Screens from the main menu's 2 PLAYER row (one A each): 2 PLAYER GAMES, PLAYER ONE CONTINUE, PLAYER TWO CONTINUE, HANDICAP,
    # LEVEL SELECT, the mode's rules, SELECT TIME, then the level.
    dict(name="two-players", config="two-players-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden"], scenarios=[
        ("two_p_one_pad", "ONE pad: 2 PLAYER > TRICK ATTACK, both skaters picked with it, the split-screen level loads; there port 2 is empty", [
            *BOOT_TO_MENU,
            ("menu", "main", 3),
            ("vpad", "attach"), ("vpress", "leftshoulder"), ("wait", 30),
            *[x for _ in range(8) for x in (("vpress", "a"), ("wait", 150))],
            ("wait_peek", "@gRunActive", 1, 60),
            ("shot", "two_p_one_pad_level"),
            ("ctl", "vpad button leftshoulder 1"), ("wait", 8),
            ("ctl_match", "inputstate", r"in_control=1 .*last=0x0020 last2=0x0000$"),   # port 1 has L, port 2 nothing (no mirror in a run)
            ("ctl", "vpad button leftshoulder 0"),
        ]),
    ]),
    dict(name="two-players-pads", config="two-players-pads-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden"], scenarios=[
        ("two_p_two_pads", "TWO pads: each picks its own skater, the split-screen level loads, each pad reaches its own port", [
            *_TWO_PADS_TO_LEVEL,
            *_TWO_PADS_PORTS,
        ]),
    ]),
    # Controller Pak: the career must exist (SAVE DATA is greyed without one), so the first scenario starts a
    # NEW CAREER and backs out to the main menu.
    dict(name="pak", config="pak-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden"], scenarios=[
        ("pak_empty", "fresh pak: OPTIONS > CONTROLLER PAK > LOAD DATA finds no career saves", [
            *BOOT_TO_MENU,
            ("menu", "main", 6),
            ("go", "A", "main_menu", "options_menu"),
            ("menu", "options", 3),
            ("go", "A", "options_menu", "pak_menu"),
            ("menu_at", "pak", 0),
            ("go", "A", "pak_menu", "load_data_empty"),
            ("go", "B", "load_data_empty", "options_menu"),   # the OK box returns to the OPTIONS list
        ]),
        ("pak_save", "NEW CAREER, then OPTIONS > CONTROLLER PAK > SAVE DATA > name 'A' writes a note (.mpk changes)", [
            ("pak_snapshot",),
            ("go", "B", "options_menu", "main_menu"),
            ("menu", "main", 0),
            ("go", "A", "main_menu", "career_menu"),
            ("go", "A", "career_menu", "career_screen"),
            ("go", "B", "career_screen", "career_menu"),
            ("go", "B", "career_menu", "main_menu"),
            ("menu", "main", 6),
            ("go", "A", "main_menu", "options_menu"),
            ("menu", "options", 3),
            ("go", "A", "options_menu", "pak_menu"),
            ("menu", "pak", 1),
            ("go", "A", "pak_menu", "enter_name"),
            ("press", "A"),                      # letter A
            ("menu_name_end",),
            ("go", "A", "enter_name", "save_ok"),
            ("pak_log", r"pak 1: wrote \d+ bytes"),
            ("pak_changed",),
        ]),
    ]),
    dict(name="pak-reload", config="pak-config", fresh_pak=False, wav=False, needs=["pak"], args=["--skip-intro", "--hidden"], scenarios=[
        ("pak_list", "fresh run on the saved pak: LOAD DATA lists the note", [
            *BOOT_TO_MENU,
            ("menu", "main", 6),
            ("go", "A", "main_menu", "options_menu"),
            ("menu", "options", 3),
            ("go", "A", "options_menu", "pak_menu"),
            ("go", "A", "pak_menu", "load_data_list"),
            ("not_cp", "load_data_empty"),
        ]),
        ("pak_load", "load the note: host reads it back from the pak", [
            ("press", "A"),
            ("pak_log", r"pak 1: read \d+ bytes at 0 of note 0"),
        ]),
    ]),
    # QOL features: Skip Intro, Show FPS, remappable bindings with a virtual controller,
    # then the crash log (the host dies, so it is the last step). Fresh settings files each run.
    dict(name="qol", config="qol-config", fresh_pak=True, wav=False,
         fresh_files=["controls.cfg", "general.cfg", "crash.log", "controls.json", "general.json", "graphics.json", "sound.json"],
         args=["--skip-intro", "--show-fps", "--hidden"], scenarios=[
        ("skip_intro", "Skip Intro: boot to the logo screen in < 200 frames, no legal text (was ~700)", [
            ("wait_for", "title"),
            ("max_frame", 200),
            ("log", r"skip intro: pressing B on the Expansion Pak notice"),
            ("log", r"skip intro: legal screen skipped"),
            ("wait_for", "demo3d"),
            ("go", "START", "demo3d", "main_menu"),
        ]),
        ("fps_counter", "Show FPS: counter lines match the perf log", [("fps_overlay", 5, 2.0)]),
        ("vpad_bindings", "virtual controller moves the menu cursor; rebinding D-pad Down to Y works and is saved", [
            ("menu_at", "main", 0),
            ("vpad", "attach"),
            ("vpress", "dpdown"),
            ("log", r"Virtual Controller takes port 1"),
            ("menu_at", "main", 1),
            ("bind", "dpad_down", "button:y"),
            ("binding_saved", "dpad_down", 3, r"(?m)^dpad_down = button:y$"),   # SDL button 3 = Y
            ("vpress", "y"),
            ("menu_at", "main", 2),
            ("vpress", "dpdown"),            # no longer bound: the cursor stays
            ("menu_at", "main", 2),
        ]),
        ("crash_log", "a crash writes crash.log with the game function names", [("crash",)]),
    ]),
    dict(name="qol-reload", config="qol-config", fresh_pak=False, wav=False, needs=["qol"],
         args=["--skip-intro", "--volume", "0", "--hidden"], scenarios=[
        ("bindings_persist", "controls.cfg from the last run: Y is D-pad Down", [
            *BOOT_TO_MENU,
            ("vpad", "attach"),
            ("menu_at", "main", 0),
            ("vpress", "y"),
            ("menu_at", "main", 1),
        ]),
        ("volume_zero", "--volume 0: the audio output is silent", [("audio_max", 90, -90.0)]),
    ]),
    # Widescreen must not change the game: the same paused frame at 4:3 (records the reference) and
    # at 21:9 (compares). The 21:9 present capture must also fill the side bands.
    # The skater rolls from the first frame of the run, so every game tick is a different picture (4 frames apart: 1.3 - 3.3 x the tolerance): the
    # pause must land on the same game TICK in every run (PAUSE_AFTER_RUN_START). The earlier anchor (the in_level checkpoint, polled every ~10 frames
    # + a screenshot, then START and 30 frames) landed on a tick that varied by several ticks from run to run: paused_w90 distance 0.32 / 0.57 /
    # 0.80 / 0.97 in passing runs and 2.50 in a failing one (2026-10-14).
    dict(name="cam-43", config="cam43-config", fresh_pak=True, wav=False, args=["--skip-intro", "--hidden", "--aspect", "original", "--window", "960x720"], scenarios=[
        ("cam_ref_43", "4:3: Foundry paused a fixed number of game frames after the run starts", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            *PAUSE_AFTER_RUN_START,
            ("wait_for", "paused_w90"),
            ("edges", 45, 4.0),
        ]),
    ]),
    dict(name="cam-219", config="cam219-config", fresh_pak=True, wav=False, present_every=15, needs=["cam-43"],
         args=["--skip-intro", "--hidden", "--aspect", "21:9", "--window", "1680x720", "--res-scale", "2"], scenarios=[
        ("cam_same_219", "21:9: the same paused frame as 4:3 (camera unchanged), side bands filled", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS,
            *PAUSE_AFTER_RUN_START,
            ("wait_for", "paused_w90"),
            ("present_wide", "1680x720", 0.10),
        ]),
    ]),
    # Frontend build only (THPS3_BINARY=build/cmake-ui/thps3_recomp; skipped otherwise): the
    # launcher and settings menu, driven with the virtual controller. A setting changed in the menu
    # is saved, and a new process starts the game from the launcher with it.
    dict(name="ui", config="ui-config", fresh_pak=True, wav=False, requires="frontend", present_every=6,
         fresh_files=["controls.json", "general.json", "graphics.json", "sound.json"],
         args=["--launcher", "--hidden"], scenarios=[
        ("ui_launcher", "launcher shows Start Game (ROM stored)", [
            ("log", r"launcher ready \(ROM stored: Start Game\)"),
            ("vpad", "attach"),
            ("wait", 60),
            ("keep_present", "ui_launcher"),
        ]),
        ("ui_settings", "Settings: General Skip Intro + Show FPS ON, Graphics Aspect Ratio ORIGINAL + Apply, Sound volume 97; saved", [
            ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "a"), ("wait", 60),          # launcher: Settings
            ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpdown"),
            ("vpress", "dpright"), ("vpress", "a"),                                             # Skip Intro: ON
            ("vpress", "dpdown"), ("vpress", "dpright"), ("vpress", "a"), ("wait", 30),         # Show FPS: ON
            ("keep_present", "ui_general_skip_intro_on"),
            ("log", r"settings: skip_intro=1 show_fps=1"),
            ("vpress", "rightshoulder"), ("wait", 30), ("keep_present", "ui_tab_controls"),
            ("vpress", "rightshoulder"), ("wait", 30), ("keep_present", "ui_tab_graphics"),
            ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpleft"), ("vpress", "a"),   # Aspect Ratio: ORIGINAL
            ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpdown"), ("vpress", "dpdown"),
            ("vpress", "a"), ("wait", 30),                                                      # Apply
            ("keep_present", "ui_graphics_applied"),
            ("log", r"gfx: aspect=original"),
            ("vpress", "rightshoulder"), ("wait", 30),
            ("vpress", "dpdown"), ("vpress", "dpleft"), ("vpress", "dpleft"), ("vpress", "dpleft"),  # Main Volume 100 -> 97
            ("keep_present", "ui_tab_sound"),
            ("log", r"settings: .* volume=97"),
            ("vpress", "back"), ("wait", 60),
            ("json_value", "general.json", "thps_skip_intro", "On"),
            ("json_value", "general.json", "thps_show_fps", "On"),
            ("json_value", "graphics.json", "ar_option", "Original"),
            ("json_value", "sound.json", "main_volume", 97),
        ]),
    ]),
    # Frontend build, no ROM stored: the launcher offers Load ROM; a v1.0 header is refused with
    # our wording (an in-UI prompt), the real ROM is accepted and the entry becomes Start Game.
    dict(name="ui-norom", config="ui-norom-config", fresh_pak=True, wav=False, requires="frontend", present_every=6,
         no_rom=True, fresh_files=["thps3.n64.us.z64", "general.json", "graphics.json", "sound.json", "controls.json"],
         args=["--launcher", "--hidden"], scenarios=[
        ("ui_load_rom", "no ROM: Load ROM; PAL-code header refused (THPS3 USA wording); the ROM accepted -> Start Game", [
            ("log", r"launcher ready \(no ROM yet: Load ROM\)"),
            ("vpad", "attach"), ("wait", 60),
            ("keep_present", "ui_launcher_no_rom"),
            ("loadrom", "rev0", r"game code NTQP"), ("wait", 30),
            ("keep_present", "ui_rom_rejected"),
            ("vpress", "a"), ("wait", 30),
            ("loadrom", "rom", r"launcher: ROM stored, Start Game"), ("wait", 30),
            ("keep_present", "ui_launcher_rom_ok"),
        ]),
    ]),
    dict(name="ui-start", config="ui-config", fresh_pak=False, wav=False, requires="frontend", present_every=6,
         needs=["ui"], args=["--launcher", "--hidden"], scenarios=[
        ("ui_start_game", "new process: settings loaded (Skip Intro, Show FPS, 4:3, volume 97); Start Game -> title; FPS overlay; in-game menu", [
            ("log", r"gfx: aspect=original"),
            ("log", r"launcher ready"),
            ("vpad", "attach"),
            ("wait", 60),
            ("vpress", "dpdown"), ("vpress", "dpup"), ("vpress", "a"),
            ("wait_for", "title"),
            ("log", r"skip intro: legal screen skipped"),
            ("fps_overlay", 3, 2.0),
            ("keep_present", "ui_title_fps"),
            ("vpress", "back"), ("wait", 45),
            ("keep_present", "ui_ingame_menu"),
        ]),
    ]),
    # High frame rate: 60 Hz frame interpolation in Foundry (every composited frame captured small),
    # and input latency on the main menu. Explicit --refresh 60.
    dict(name="hfr", config="hfr-config", fresh_pak=True, wav=False,
         args=["--refresh", "60", "--skip-intro", "--hidden", "--present-size", "480x360"], scenarios=[
        ("input_latency", "main menu: press -> first changed presented frame (median of 6, <= 100 ms)", [
            *BOOT_TO_MENU,
            ("latency", "DOWN/UP", 6, 100.0),
        ]),
        ("hfr_motion", "60 Hz interpolation: every refresh shows a new, evenly spaced frame while skating (matrix-group IDs: 97 % of the transforms pair, was 29 % without; threshold 85 %)", [
            ("menu", "main", 0),
            *CAREER_TO_GOALS,
            ("go", "A", "goals", "in_level", 90),
            ("wait", 30),
            ("hfr_motion", 4.0, "SUP", dict(fm60=0.9, alt=0.3, interp=0.9, paired=0.85, dropped=0.05)),
            ("fps", 5, 28.0),
        ]),
    ]),
]

# Evidence / debugging sessions: not part of the suite, run only by name (tools/test.sh --session answers|jitter).
DEBUG_SESSIONS = [x for x in SESSIONS if x["name"] in ("answers", "jitter", "idsprobe", "idsclip", "idsbench", "idsbench-orig", "idsload")]
SESSIONS = [x for x in SESSIONS if x not in DEBUG_SESSIONS]

# HUD placement (src/hud_anchor.cpp): regression sessions (hud = the default, hud-original, hud-43) and optin present captures (hud-<orig169|orig219|edge169|edge219|clamp219>,
# hud-dbg; run by name): the sessions are built in the shared tests/hud_sessions.py from this game's navigation steps.
from hud_sessions import hud_sessions  # noqa: E402
SESSIONS += hud_sessions([*CAREER_TO_GOALS, ("go", "A", "goals", "in_level", 90)], pause_menu='pause', end_run=4, view_goals=2, boot=BOOT_TO_MENU)

# Cheats (test aids, game/cheats.cpp; the game's own cheats through the Cheat_IsOn hook): exploration (opt-in, CS_ARGS = cheat flags).
import os as _os
_CS_TRY = [("axis", "lefty", -32767), ("vpad", "a", 1), ("wait", 8), ("vpad", "a", 0), ("wait", 2), ("axis", "leftx", 32767), ("vpad", "x", 1),
           ("wait", 4), ("vpad", "x", 0), ("axis", "leftx", 0), ("vpad", "y", 1), ("wait", 12), ("vpad", "y", 0)]
SESSIONS += [
    dict(name="cheats-explore", config="cheats-explore-config", fresh_files=["cheats.cfg"], fresh_pak=True, wav=False, optin=True, args=["--skip-intro"] + _os.environ.get("CS_ARGS", "").split(), scenarios=[
        ("cheats_explore", "exploration: first level, forward + ollie + flip + grind presses; skater state / rail balance / time scale samples", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS, ("go", "A", "goals", "in_level", 90), ("wait", 30),
            ("vpad", "attach"),
            ("skater_watch", 80, _CS_TRY, ["Skater_PhysState", "Skater_RailBalance", "@gTimeScale"]),
            ("ctl", "vpad axis lefty 0"),
            ("go", "START", "in_level", "pause"), ("wait", 20), ("shot", "pause"),
        ]),
    ]),
]

from cheat_sessions import cheat_sessions  # noqa: E402
SESSIONS += cheat_sessions(BOOT_TO_MENU, [*CAREER_TO_GOALS, ("go", "A", "goals", "in_level", 90)], [
    ("menu", "main", 0), ("go", "A", "main_menu", "career_menu"), ("go", "A", "career_menu", "career_screen"),   # a career in RAM (SAVE DATA saves it)
    ("go", "B", "career_screen", "career_menu"), ("go", "B", "career_menu", "main_menu"),
    ("menu", "main", 6), ("go", "A", "main_menu", "options_menu"),
    ("menu", "options", 3), ("go", "A", "options_menu", "pak_menu"),
    ("menu", "pak", 1), ("go", "A", "pak_menu", "enter_name"), ("press", "A"), ("menu_name_end",),
    ("go", "A", "enter_name", "save_ok"), ("pak_log", r"pak 1: wrote \d+ bytes"),
], _CS_TRY)

# The in-game settings menu (THPS_MENU builds; skipped otherwise): tests/menu_session.py in the shared host.
from menu_session import MENU_SESSIONS  # noqa: E402
SESSIONS += MENU_SESSIONS

# Draw distance (2026-10-17): career (unlocked levels), one level with the setting under test.
# Same steps as THPS1's dd-probe: a paused spot compared per factor (DD_AB), then a ride with frame times. Exploration only (optin).
# DD_RIGHTS: RIGHT presses at the level select; DD_TAG / DD_OUT: output; DD_ARGS: extra host args; DD_RIDE "lefty:frames ..." (x=... for leftx).
_DD_DIR = _os.path.join(_os.environ.get("DD_OUT", "/tmp/dd"), _os.environ.get("DD_TAG", "run"))
_DD_SHOT = lambda name: [("ctl", f"pcap 1 {_DD_DIR}/{name}"), ("wait", 3), ("ctl", "pcap 0"), ("wait", 10)]
# DD_AB "K[:S] ...": factor K, with `dd showall S` first when given (1:0 = the game's own picture inside `full`); DD_TRACE=1: `dltrace 1` after
# each shot (the frame's commands in the host log: which course items are drawn, tools in the private notes); DD_VTRACE=1 / DD_VRAMSAVE=1:
# the same, and a RAM dump, at the "vantage" frame (DD_WATCH runs).
_DD_TRACE = [("ctl", "dltrace 1"), ("wait", 5)] if _os.environ.get("DD_TRACE") else []
DD_RESTART_PRESSES = lambda v: [] if v == "" else [s for n, d in [(v.split(":") + ["3"])[:2]] for k, w in [
    ("START", 45), *[("DOWN", 12)] * int(d), ("A", 30), *[("DOWN", 12)] * int(n), ("A", 120)] for s in (("press", k), ("wait", w), ("shot", "pre"))]
_DD_AB = [s for t in _os.environ.get("DD_AB", "1 2 4 8").split() for k, sa in [(t.split(":") + [""])[:2]] for s in (
    *([("ctl", f"dd showall {sa}")] if sa else []),
    ("ctl", f"dd factor {k}"), ("ctl", "dd reset"), ("wait", 20), *_DD_SHOT(f"start_x{k}{'_s' + sa if sa else ''}"), *_DD_TRACE, ("dl", 30, 0), ("ctl", "dd"))]
SESSIONS += [
    dict(name="dd-probe", config="dd-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--present-size", "960x540", "--aspect", "16:9", "--window", "1280x720",
               "--refresh", "60"] + _os.environ.get("DD_ARGS", "").split(),
         scenarios=[
        ("dd_probe", "draw distance: paused spot per factor (frame, triangles, buffers), camera swing, ride with frame times", [
            *BOOT_TO_MENU,
            *CAREER_TO_GOALS[:-1],
            *[s for _ in range(int(_os.environ.get("DD_RIGHTS", "0"))) for s in (("press", "DOWN"), ("wait", 20))],   # THPS3: a vertical list
            ("shot", "level_select"),
            ("press", "A"), ("wait", 150), ("shot", "goals"),
            # DD_WATCH=1: start counting at the run flag (gRunActive 0 -> 1), so DD_RIDE and the "vantage" frame land on the same game frame in
            # every run (THPS2/3 runs are repeatable from there; the load time before it is not).
            *([("ctl", "dd showall " + _os.environ["DD_SHOWALL"])] if _os.environ.get("DD_SHOWALL") else []),   # A/B of the zone visibility alone
            *([("press", "A"), ("ctl", "watch @gRunActive 1")] if _os.environ.get("DD_WATCH") else [("press", "A"), ("wait", 300)]),
            ("shot", "in_level"),
            # DD_IDLEWATCH=1: the level_grab question: the skater word the "air" check reads (Skater_PhysState) sampled every 2 frames with no input
            *([("skater_watch", 90, [("wait", 2)], ["Skater_PhysState"])] if _os.environ.get("DD_IDLEWATCH") else []),
            ("ctl", "dd"),
            *([("ctl", f"ramsave {_DD_DIR}/ram_start.bin")] if _os.environ.get("DD_RAMSAVE") else []),
            # DD_PRE "KEY:frames ...": presses before the ride, with a shot after each (e.g. with --skip-to-restart in DD_ARGS: the pause menu's
            # SKIP TO RESTART to one of the course's restart points: repeatable spots all over the course)
            # DD_RESTART "N[:D]" (needs --skip-to-restart in DD_ARGS): the same to restart point N of the RESTARTS list (0 RESTART SKATE,
            # 1 RE-2P, 2 the first of the course's own). D = DOWNs to SKIP TO RESTART in the pause menu: 3 in career courses (CONTINUE, RETRY,
            # VIEW GOALS, SKIP TO RESTART: THPS2's two DOWNs open VIEW GOALS here), 2 in the competitions (Rio, Skater Island, Tokyo: CONTINUE,
            # RESTART COMPETITION, SKIP TO RESTART).
            *DD_RESTART_PRESSES(_os.environ.get("DD_RESTART", "")),
            *[s for st in _os.environ.get("DD_PRE", "").split() for s in (("press", st.split(":")[0]), ("wait", int(st.split(":")[1])), ("shot", "pre"))],
            ("vpad", "attach"),
            *[s for st in _os.environ.get("DD_RIDE", "").split() for s in (
                (("ctl", f"vpad axis leftx {st.split(':')[0][2:]}"),) if st.startswith("x=") else (("ctl", f"vpad axis lefty {st.split(':')[0]}"),)) +
                (("wait", int(st.split(':')[1])),)],
            *(_DD_SHOT("vantage") if _os.environ.get("DD_WATCH") else []),
            *([("ctl", "dltrace 1"), ("wait", 2)] if _os.environ.get("DD_VTRACE") else []),
            *([("ctl", f"ramsave {_DD_DIR}/ram_vantage.bin")] if _os.environ.get("DD_VRAMSAVE") else []),
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"),
            *([("press", "START"), ("wait", 45)] if _os.environ.get("DD_PAUSE", "1") == "1" else []),
            # DD_SETTLE: frames to wait first (THPS3's pause screen does not set the frustum again, so the comparison is made while playing:
            # standing still after the course's intro camera has settled). gTimeScale cannot freeze it: the game rewrites it every frame.
            ("wait", int(_os.environ.get("DD_SETTLE") or "0") or 1),
            *_DD_AB,
            # DD_CTL "cmd1;cmd2;..." at the paused spot after DD_AB (exploration: "dd factor 2;dltrace 1;dd factor 4;dltrace 1")
            *[s for c in _os.environ.get("DD_CTL", "").split(";") if c.strip() for s in (("ctl", c.strip()), ("wait", 20))],
            # DD_BUDGET "CAP [REST PASS MARGIN]": `dd dlbudget` at the paused spot (a shot of the same frame after it) and for the ride
            # (the byte budget forced to cut: near scenery and the game's own pass must stay)
            *([("ctl", "dd dlbudget " + _os.environ["DD_BUDGET"]), ("wait", 20), *_DD_SHOT("budget"), ("ctl", "dd")] if _os.environ.get("DD_BUDGET") else []),
            ("ctl", "dd mode " + _os.environ.get("DD_MODE", "original")),
            *([("ctl", "dd factor " + _os.environ["DD_FACTOR"])] if _os.environ.get("DD_FACTOR") else []),
            *([("ctl", "dd testcap " + _os.environ["DD_TESTCAP"])] if _os.environ.get("DD_TESTCAP") else []),
            ("ctl", "dd reset"),
            *([("press", "START"), ("wait", 45)] if _os.environ.get("DD_PAUSE", "1") == "1" else []),
            ("ctl", "vpad axis lefty 32767"), ("wait", 120), ("ctl", "vpad axis lefty 0"), ("wait", 40),
            *_DD_SHOT("back"),
            ("dl", 30, 0),
            ("ctl", "ftime start"),
            *([("ctl", f"pcap {_os.environ['DD_TOUR']} {_DD_DIR}/tour")] if _os.environ.get("DD_TOUR") else []),   # every Nth composited frame of the ride
            ("ctl", "vpad axis lefty -32767"),
            # DD_BURSTS=N: N short bursts of consecutive frames along the ride (b0, b1, ...: pairs of runs line up within a burst)
            *[s for k in range(int(_os.environ.get("DD_BURSTS") or "0")) for s in (("wait", 40), *_DD_SHOT(f"b{k}"),
                                                                              ("ctl", f"vpad axis leftx {(-32767, 0, 32767, 0)[k % 4]}"))],
            ("wait", 150),
            *_DD_SHOT("ride1"),
            *[s for k in range(6) for s in (("ctl", f"vpad axis leftx {32767 if k % 2 else -32767}"), ("wait", 20), ("ctl", "vpad axis leftx 0"), ("wait", 20))],
            *_DD_SHOT("ride2"),
            ("dl", 30, 0),
            *([("ctl", "pcap 0")] if _os.environ.get("DD_TOUR") else []),
            ("ctl", f"ftime stop {_DD_DIR}/ftime.csv"),
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"), ("wait", 20),
            ("ctl", "dd"), ("ctl", "stats"), ("ctl", "dd dlprobe"), ("ctl", "dd heap"),
        ]),
    ]),
]

# Heap headroom with the always-allocated 2048-matrix pools (2026-10-22, the private development notes; optin, measurement): one career
# course (DH_COURSE: list position), loaded, skated ~12 s and ended from the pause menu (END RUN), `dd heap` (low-water marks since the
# start) after the load, after the ride and after the end. DD_ARGS: extra host args (e.g. "--draw-distance full", "--dd-buffers original").
_DH_PLAY = [("ctl", "vpad axis lefty -32767"),
            *[x for k in range(12) for x in (("ctl", f"vpad axis leftx {(-32767, 0, 32767, 0)[k % 4]}"),
                                             ("ctl", "vpad button a 1"), ("wait", 8), ("ctl", "vpad button a 0"), ("wait", 22))],
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0")]
SESSIONS += [
    dict(name="dd-heap", config="dd-heap-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--unlock-levels"] + _os.environ.get("DD_ARGS", "").split(), scenarios=[
        ("dd_heap", "heap headroom: one course, `dd heap` low-water marks", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"),
            *CAREER_TO_GOALS[:-1],
            *[s for _ in range(int(_os.environ.get("DH_COURSE", "0"))) for s in (("press", "DOWN"), ("wait", 30))],
            ("shot", "select"),
            ("press", "A"), ("wait", 150), ("press", "A"), ("ctl", "watch @gRunActive 1"), ("wait", 30),
            ("shot", "in_level"), ("ctl", "dd heap"),
            ("vpad", "attach"), *_DH_PLAY,
            ("ctl", "dd heap"), ("ctl", "dd"),
            ("press", "START"), ("wait", 40), ("menu", "pause", 3), ("press", "A"), ("wait", 150), ("shot", "ended"),
            ("ctl", "dd heap"),
        ]),
    ]),
]

# Draw distance long run (2026-10-17): several courses back to back in one host, each played DD_LONG_S seconds with stick
# input, then pause -> END RUN and on through the end-of-run screens (DD_LONG_NAV: presses after END RUN) to the next course. Exploration
# only (optin): shots at every step, `dd` stats after each course (buffer peaks, governor), `stats` at the end.
_DDL_COURSES = [int(x) for x in _os.environ.get("DD_LONG_COURSES", "0 1 2").split()]   # increasing list positions
_DDL_PLAY = lambda s: [("ctl", "vpad axis lefty -32767"), *[x for k in range(max(1, s // 2)) for x in (
    ("ctl", f"vpad axis leftx {(-32767, 0, 32767, 0)[k % 4]}"), ("ctl", "vpad button a 1"), ("wait", 8), ("ctl", "vpad button a 0"), ("wait", 52))],
    ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0")]
_DDL_NAV = [s for p in _os.environ.get("DD_LONG_NAV", "A:120 DOWN:20 DOWN:20 A:150").split() for s in (("press", p.split(":")[0]), ("wait", int(p.split(":")[1])), ("shot", "nav"))]
SESSIONS += [
    dict(name="dd-long", config="dd-long-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--present-size", "480x270", "--refresh", "60"] + _os.environ.get("DD_ARGS", "").split(),
         scenarios=[
        ("dd_long", "draw distance: several courses back to back (heap, buffers, governor)", [
            *([*BOOT_TO_MENU] if "BOOT_TO_MENU" in globals() and _os.environ.get("DD_LONG_BOOT3") else [("wait_for", "title"), ("go", "START", "title", "main_menu")]),
            *CAREER_TO_GOALS[:-1],
            *[s for i, c in enumerate(_DDL_COURSES) for s in (
                # the level select keeps its cursor on the last course: move by the difference
                *[x for _ in range(c - (_DDL_COURSES[i - 1] if i else 0)) for x in (("press", _os.environ.get("DD_LONG_KEY", "DOWN")), ("wait", 30))],   # a list
                ("shot", f"select_{i}"),
                ("press", "A"), ("wait", 150), ("press", "A"), ("ctl", "watch @gRunActive 1"), ("vpad", "attach"),
                *([] if _os.environ.get("DD_LONG_NODD") else [("ctl", "dd reset")]), ("ctl", "ftime start"),   # DD_LONG_NODD: a host without `dd` (v0.1)
                *_DDL_PLAY(int(_os.environ.get("DD_LONG_S", "120"))),
                ("ctl", "ftime stop"), *([] if _os.environ.get("DD_LONG_NODD") else [("ctl", "dd"), ("ctl", "dd heap")]), ("shot", f"played_{i}"),
                ("press", "START"), ("wait", 40), ("menu", "pause", 4), ("press", "A"), ("wait", 120), ("shot", f"endrun_{i}"),   # END RUN is the 5th entry
                *_DDL_NAV,
            )],
            ("ctl", "stats"), *([] if _os.environ.get("DD_LONG_NODD") else [("ctl", "dd heap")]),
        ]),
    ]),
]
# Course cycle (src/music.cpp; the THPS2 crash after a few courses, 2026-10-17: THPS3 has the same music player): Foundry, Los Angeles,
# Suburbia, Airport back to back (Rio is a competition), each ended from the pause menu: END RUN -> statistics -> A -> the END RUN menu ->
# LEVEL SELECT (third entry). The level select list keeps its cursor on the last course: move by the difference.
from course_cycle import course_cycle_session  # noqa: E402
SESSIONS += [course_cycle_session(
    "course-cycle", [*BOOT_TO_MENU, *CAREER_TO_GOALS[:-1]],
    [[x for _ in range(n) for x in (("press", "DOWN"), ("wait", 20))] for n in (0, 1, 2, 1)],
    [("press", "A"), ("wait", 150), ("press", "A"), ("wait_peek", "@gRunActive", 1, 60)],
    [("press", "START"), ("wait", 40), ("menu", "pause", 4), ("press", "A"), ("wait", 120), ("press", "A"), ("wait", 60),
     ("press", "DOWN"), ("wait", 20), ("press", "DOWN"), ("wait", 20), ("shot", "end_menu"), ("press", "A"), ("wait", 150)],
    claim=[("vpress", "rightstick"), ("wait", 10)],
)]

# Two players in widescreen (v0.2, rt64-splitscreen-widescreen.patch + hud_anchor.cpp): the side-by-side split screen fills the wide picture,
# each view widened like the one-player camera (`split` views > 0), each player's HUD block at its own view's edge (the game mirrors player 2's
# HUD to the right of its view: groups at q0 and q4), both pads on their own ports. present_split: in each side band outside the central 4:3
# area >= 90 % of the columns are drawn. Then `split off` (live) for a before picture. `169-hudorig`: HUD Placement `original` places the
# split screen's HUD the same way (the views fill the picture; the 4:3 spot would leave each HUD inside its view), so the same groups are expected.
SESSIONS += [
    dict(name=f"two-players-{var}", config=f"two-players-{var}-config", fresh_pak=True, wav=False, present_every=10,
         args=["--skip-intro", "--hidden", "--aspect", asp, "--window", win, "--res-scale", "2", *extra], scenarios=[
        (f"two_players_{var}", f"two players at {asp}{' (hud original)' if extra else ''}: the split screen fills the picture, each HUD at its view's edge, each pad on its port", [
            *_TWO_PADS_TO_LEVEL,
            ("wait", 60),
            ("present_split", win, 0.90),
            ("keep_present", f"two_players_{var}_after"),
            ("ctl_match", "split", r"wide=1 views=[1-9]\d* .* hud_tasks=[1-9]\d* groups q0=[1-9]\d* .* q4=[1-9]\d* "),
            ("ctl_match", "hud", r"mode=%s " % ("original" if extra else "expand")),
            *_TWO_PADS_PORTS,
            ("ctl", "split off"), ("wait", 20), ("keep_present", f"two_players_{var}_before"),
        ]),
    ])
    for (var, asp, win, extra) in (("169", "16:9", "1280x720", []), ("219", "21:9", "1680x720", []),
                                   ("169-hudorig", "16:9", "1280x720", ["--hud", "original"]))
]

# Two players with split original (hud expand): each player's HUD stays with its view in the 4:3 middle (hud_sessions.two_players_split_original).
from hud_sessions import two_players_split_original  # noqa: E402
SESSIONS.append(two_players_split_original(_TWO_PADS_TO_LEVEL))
# Border crop (graphics setting `border`, src/border_crop.cpp): the shared tests/crop_sessions.py.
from crop_sessions import crop_sessions  # noqa: E402
SESSIONS += crop_sessions([*CAREER_TO_GOALS, ("go", "A", "goals", "in_level", 90)], boot=BOOT_TO_MENU, pause=[("go", "START", "in_level", "pause")])
# Border crop in a two-player split screen at 16:9: each view's own inset scissor goes to the frame's edges too (crop_sessions.crop_two_players).
from crop_sessions import crop_two_players  # noqa: E402
SESSIONS.append(crop_two_players(_TWO_PADS_TO_LEVEL, [("ctl", "vpad button start 1"), ("wait", 10), ("ctl", "vpad button start 0"), ("wait", 45)]))
# Level-start freeze (v0.2 queue item 3, tests/load_freeze.py): the course cycle's four starts with frame timestamps over each load
# phase (A on the level select, A on the goals). `lf-probe` (optin) runs in a visible window; THPS_LF_SAMPLE=8 adds a `sample`.
from load_freeze import load_freeze_session  # noqa: E402
_LF = dict(
    to_select=[*BOOT_TO_MENU, *CAREER_TO_GOALS[:-1]],
    courses=[[x for _ in range(n) for x in (("press", "DOWN"), ("wait", 20))] for n in (0, 1, 2, 1)],
    phases=[("A", []), ("A", [("wait_peek", "@gRunActive", 1, 60)])],
    end_run=[("press", "START"), ("wait", 40), ("menu", "pause", 4), ("press", "A"), ("wait", 120), ("press", "A"), ("wait", 60),
             ("press", "DOWN"), ("wait", 20), ("press", "DOWN"), ("wait", 20), ("press", "A"), ("wait", 150)],
    claim=[("vpress", "rightstick"), ("wait", 10)],
)
SESSIONS += [load_freeze_session("lf-probe", **_LF, hidden=False, optin=True, limits={"composited": 1000.0, "game": 1000.0})]
# The suite's check (hidden window, the first three courses): the median over the three starts of the longest gap between game
# frames while the course loads stays under LF_GAME_MS (one preempted window on a busy machine does not fail it; a warning only
# when the machine is overloaded). Before the v0.2 fixes (ERZ decoder, native memset / memcpy) every start was over it.
LF_GAME_MS = 135.0   # 2026-10-18: 100-112 ms after the fixes, 140-155 ms before (load 3-6)
SESSIONS += [load_freeze_session("lf-check", **{**_LF, "courses": _LF["courses"][:3]}, limits={"game": 1000.0}, median=("game", LF_GAME_MS))]
# Draw distance "full" leaves event items to the game (game/draw_distance.cpp): in the Foundry the first valve of the "5 valves" goal
# swaps two course items when the skater hits it (item 516 hidden, item 517 shown; found by diffing RAM before and after the hit). With
# `full` on, 517 must stay hidden until the hit (it is hidden at load and named by the goal's script, so not the zone culling's to undo)
# and be drawn after it, because the game showed it; 516 the other way round. `dd item N` reports the bits and what "full" does with them.
_VALVE_ROUTE = [("ctl", "vpad axis lefty -32767"), ("wait", 40), ("ctl", "vpad axis leftx 32767"), ("wait", 25), ("ctl", "vpad axis leftx 0"),
                ("wait", 30), ("ctl", "vpad button a 1"), ("wait", 10), ("ctl", "vpad button a 0"), ("wait", 4), ("ctl", "vpad button x 1"),
                ("wait", 6), ("ctl", "vpad button x 0"), ("wait", 40), ("ctl", "vpad button a 1"), ("wait", 10), ("ctl", "vpad button a 0"),
                ("wait", 4), ("ctl", "vpad button b 1"), ("wait", 25), ("ctl", "vpad button b 0"), ("wait", 60), ("ctl", "vpad axis lefty 0")]
SESSIONS += [dict(name="dd-event", config="dd-event-config", fresh_pak=True, wav=False,
    args=["--skip-intro", "--hidden", "--draw-distance", "full", "--window", "960x540"], scenarios=[
    ("dd_event_item", "draw distance full: an item the Foundry's valve goal reveals stays hidden until the valve is hit, then is drawn", [
        *BOOT_TO_MENU, *CAREER_TO_GOALS, ("go", "A", "goals", "in_level", 90), ("wait_peek", "@gRunActive", 1, 60),
        ("vpad", "attach"), ("vpress", "rightstick"), ("wait", 20),
        ("ctl_match", "dd item 517", r"flags 0x0041 zone 0x00 event \d drawn 0"),
        ("ctl_match", "dd item 516", r"flags 0x0000 .* drawn 1"),
        ("shot", "before_valve"),
        ("ctl_same", "dd item 516", r" named (\d+) ", "named"),   # what the course's set-up scripts named (the valve's goal among them)
        *_VALVE_ROUTE,
        ("shot", "after_valve"),
        ("ctl_match", "dd item 517", r"flags 0x0000 .* drawn 1"),
        ("ctl_match", "dd item 516", r"flags 0x0041 zone 0x00 event 1 drawn 0"),
    ]),
    # RETRY runs the course set-up again and rebuilds the item list at the same address and count (review 2026-10-26, finding 7): the zone
    # record starts again, so item 516 is shown and the game's again, and the event-owned items are exactly what the set-up named (before
    # the fix the record survived: 516 kept the last run's event ownership, `named` one more).
    ("dd_event_retry", "pause > RETRY: the valve's items are back as the course starts them; event ownership is the new run's", [
        ("press", "START"), ("wait", 40), ("menu", "pause", 1), ("press", "A"), ("wait", 150), ("wait_peek", "@gRunActive", 1, 60),
        ("ctl_match", "dd item 516", r"flags 0x0000 .* drawn 1 named \d+ gen [1-9]"),
        ("ctl_match", "dd item 517", r"flags 0x0041 .* drawn 0"),
        ("ctl_same", "dd item 516", r" named (\d+) ", "named"),
        ("ctl_match", "dd", r"course_starts=[2-9]"),
    ]),
    # Governor feedback across a transition (review 2026-10-26, finding 6), deterministic: `dd stale 99` gives a 99 % sample measured across
    # a transition and one built before it, in one critical section: both dropped, Full keeps its ceiling. `dd feed 99` (the control case)
    # gives a current one once the settle is over: it panics.
    ("dd_stale_feedback", "a stale buffer sample after a setting change is dropped; a current one still acts", [
        ("ctl", "dd mode full"), ("wait", 10), ("ctl", "dd reset"),
        ("ctl_match", "dd stale 99", r"ceiling=64\.00 .* panics=0 .* stale_dropped=1 settle_dropped=[1-9]"),
        ("wait", 10),
        ("ctl_match", "dd feed 99", r"ceiling=(?!64\.00)\d.* panics=1 "),
        ("ctl_match", "dd mode full", r"ceiling=64\.00 "),
    ]),
])]

# Draw distance in a two-player split screen (exploration, optin): the one-pad 2 PLAYER > TRICK ATTACK start of `two-players` (first course),
# then the same paused (THPS3: standing, DD_PAUSE=0) A/B as dd-probe (DD_AB, DD_TRACE, DD_ARGS, DD_OUT / DD_TAG) and a RAM dump.
SESSIONS += [
    dict(name="dd-2p", config="dd-2p-config", fresh_pak=True, wav=False, optin=True,
         args=["--skip-intro", "--hidden", "--present-size", "960x540", "--aspect", "16:9", "--window", "1280x720",
               "--refresh", "60"] + _os.environ.get("DD_ARGS", "").split(),
         scenarios=[
        ("dd_2p", "draw distance in a two-player split screen: paused spot per factor (frames, traces, buffers)", [
            *BOOT_TO_MENU,
            ("menu", "main", 3),
            ("vpad", "attach"), ("vpress", "leftshoulder"), ("wait", 30),
            # DD_2P_COURSE=N: N DOWNs at the level select (the 6th A; THPS3 order: 0 Foundry .. 6 Canada, 7 Tokyo; needs --unlock-levels in DD_ARGS)
            *[x for k in range(8) for x in (
                *[y for _ in range(int(_os.environ.get("DD_2P_COURSE", "0")) if k == 5 else 0) for y in (("vpress", "dpdown"), ("wait", 20))],
                ("shot", f"dd_2p_menu{k}"), ("vpress", "a"), ("wait", 150))],
            ("wait_peek", "@gRunActive", 1, 60),
            ("wait", int(_os.environ.get("DD_SETTLE") or "60")),
            ("shot", "dd_2p_level"),
            # DD_2P_RIDE "lefty:leftx:frames ..." (pad 1, unpaused, before the paused A/B): turning with `dd` readings and a shot after each step
            *([("ctl", "dd"), ("ctl", "dd reset")] if _os.environ.get("DD_2P_RIDE") else []),
            *[x for i, st in enumerate(_os.environ.get("DD_2P_RIDE", "").split()) for x in (
                ("ctl", f"vpad axis lefty {st.split(':')[0]}"), ("ctl", f"vpad axis leftx {st.split(':')[1]}"), ("wait", int(st.split(':')[2])),
                *_DD_SHOT(f"ride{i:02d}"), ("ctl", "dd"))],
            *([("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"), ("ctl", "dd"), ("ctl", "dd dlprobe")] if _os.environ.get("DD_2P_RIDE") else []),
            *([("vpress", "start"), ("wait", 45)] if _os.environ.get("DD_PAUSE", "1") == "1" else []),
            ("ctl", f"ramsave {_DD_DIR}/ram_vantage.bin"),
            *_DD_AB,
            ("ctl", "dd showall auto"), ("ctl", "dd"), ("ctl", "dd heap"), ("ctl", "dd dlprobe"),
        ]),
    ]),
]

# Draw distance at a course start (2026-10-25, the user's Canada reports): the career goals screen, drawn over the course, takes 820 vertices
# at Full (the game's pool holds 500), a two-player start 1600; when the governor counted the game's 500-vertex pool it panicked to 1x
# there and kept that ceiling for the whole run, so Full showed only what Original shows (in one and two players). With the bigger vertex
# pools (game/draw_distance.cpp) Canada starts and stays at Full: no step back since start-up, the factor and ceiling at 64, and the extra
# passes drawing the course items beyond the game's own distance (runs_hw >= 2: the buildings above the first slope in the user's video).
_DDC_FULL = r"in_use=64\.00 in_use_min=64\.00 ceiling=64\.00 .* runs_hw=[2-9]\d* mtx_capped=0 backoffs=0 panics=0 cuts=0 "
_DDC_RIDE = [("ctl", "dd reset"), ("ctl", "vpad axis lefty -32767"),
             *[x for k in range(6) for x in (("ctl", f"vpad axis leftx {(32767, 0, -32767, 0, 32767, -32767)[k]}"), ("wait", 25))],
             ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"), ("wait", 10)]
SESSIONS += [
    dict(name="dd-canada", config="dd-canada-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--draw-distance", "full", "--window", "960x540"], scenarios=[
        ("dd_canada", "draw distance full, one player: Canada starts at Full after the goals screen and stays there while skating and turning", [
            *BOOT_TO_MENU, *CAREER_TO_GOALS[:-1],
            *[x for _ in range(6) for x in (("press", "DOWN"), ("wait", 20))], ("shot", "select_canada"),
            ("press", "A"), ("wait", 150), ("shot", "goals"),
            ("press", "A"), ("wait_peek", "@gRunActive", 1, 60), ("wait", 30), ("shot", "in_level"),
            ("ctl_match", "dd", _DDC_FULL),
            ("ctl_match", "dd heap", r"vtx_pool 4096 vtx_cap 4096"),
            ("vpad", "attach"), *_DDC_RIDE, ("shot", "after_ride"),
            ("ctl_match", "dd", r"in_use=64\.00 .*ceiling=64\.00 .* runs_hw=[2-9]\d* mtx_capped=0 backoffs=0 panics=0 cuts=0 "),
        ]),
    ]),
    dict(name="dd-canada-2p", config="dd-canada-2p-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--unlock-levels", "--draw-distance", "full", "--window", "960x540"], scenarios=[
        ("dd_canada_2p", "draw distance full, two players (one pad, dd-2p's start): Canada starts at Full and stays there while turning", [
            *BOOT_TO_MENU,
            ("menu", "main", 3),
            ("vpad", "attach"), ("vpress", "leftshoulder"), ("wait", 30),
            *[x for k in range(8) for x in (*[y for _ in range(6 if k == 5 else 0) for y in (("vpress", "dpdown"), ("wait", 20))],
                                            *([("shot", "select_canada")] if k == 5 else []), ("vpress", "a"), ("wait", 150))],
            ("wait_peek", "@gRunActive", 1, 60), ("wait", 30), ("shot", "in_level"),
            ("ctl_match", "dd", _DDC_FULL),
            ("ctl_match", "dd heap", r"vtx_pool 4096 vtx_cap 4096"),
            *_DDC_RIDE, ("shot", "after_ride"),
            ("ctl_match", "dd", r"in_use=64\.00 .*ceiling=64\.00 .* runs_hw=[2-9]\d* mtx_capped=0 backoffs=0 panics=0 cuts=0 "),
        ]),
    ]),
]

# Draw distance's matrix pools (2026-10-22, the private development notes): with dd_buffers = bigger (the default) the game gets pools of
# 2048 matrices at every course start and keeps its own cap (420) at `original`, so the setting takes effect at once, both ways; with
# --dd-buffers original the game's own pools (420) whatever the setting.
_DDB_TO_LEVEL = [("wait_for", "title"), ("go", "START", "title", "main_menu"), *CAREER_TO_GOALS[:-1], ("press", "A"), ("wait", 150), ("press", "A"), ("ctl", "watch @gRunActive 1"), ("wait", 30)]
SESSIONS += [
    dict(name="dd-buffers", config="dd-buffers-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--draw-distance", "original", "--dd-buffers", "bigger"], scenarios=[
        ("dd_buffers_now", "default buffers: pools of 2048 with the game's cap 420 at Original; Full raises the cap at once, Original puts it back", [
            *_DDB_TO_LEVEL,
            ("ctl_match", "dd heap", r"mtx_pool 2048 mtx_cap 420 "),
            ("ctl_match", "dd", r"buffers=bigger .* mtx_cap=420 "),
            ("ctl", "dd mode full"), ("wait", 30),
            ("ctl_match", "dd heap", r"mtx_pool 2048 mtx_cap 2048 "),
            ("ctl_match", "dd", r"mtx_cap=2048 "),
            ("ctl", "dd mode original"), ("wait", 30),
            ("ctl_match", "dd heap", r"mtx_pool 2048 mtx_cap 420 .* failed_calls 0 "),
        ]),
    ]),
    dict(name="dd-buffers-own", config="dd-buffers-own-config", fresh_pak=True, wav=False,
         args=["--skip-intro", "--hidden", "--draw-distance", "original", "--dd-buffers", "original"], scenarios=[
        ("dd_buffers_own", "--dd-buffers original: the game's own pools (420), at Original and at Full", [
            *_DDB_TO_LEVEL,
            ("ctl_match", "dd heap", r"mtx_pool 420 mtx_cap 420 "),
            ("ctl_match", "dd", r"buffers=original .* mtx_cap=420 "),
            ("ctl", "dd mode full"), ("wait", 30),
            ("ctl_match", "dd heap", r"mtx_pool 420 mtx_cap 420 "),
            ("ctl", "dd mode original"),
        ]),
    ]),
    # Opt-in demo: Rio at Original, then Graphics > Draw Distance > Full in the menu in the middle of the run, a ride: the pool use goes past
    # the game's 420 with no restart (`dd`: mtx_hw > 420, mtx_capped=0). DD_ARGS: extra host args.
    dict(name="dd-switch", config="dd-switch-config", fresh_pak=True, wav=False, optin=True, requires="menu",
         fresh_files=["graphics.cfg"],
         args=["--skip-intro", "--hidden", "--unlock-levels", "--window", "1280x720", "--draw-distance", "original"] + _os.environ.get("DD_ARGS", "").split(), scenarios=[
        ("dd_switch", "switch Original -> Full in the menu mid-run: the matrix pool use passes 420 at once", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), *CAREER_TO_GOALS[:-1],
            *[s for _ in range(8) for s in (("press", "DOWN"), ("wait", 30))],   # Rio: list position 8 with --unlock-levels
            ("shot", "select"),
            ("press", "A"), ("wait", 150), ("press", "A"), ("ctl", "watch @gRunActive 1"), ("wait", 30),
            ("shot", "in_level_original"),
            ("ctl", "dd reset"), ("wait", 60),
            ("ctl_match", "dd", r"mode=original .* mtx_cap=420 "),
            ("ui", "esc"), ("ui_state", "open=1"), ("ui", "tab 2"), ("ui", "click #lbl_dd_full"), ("log", r"draw distance: full"), ("ui", "esc"),
            ("ctl", "dd reset"),
            ("vpad", "attach"),
            ("ctl", "vpad axis lefty -32767"), ("wait", 150),
            *[s for k in range(6) for s in (("ctl", f"vpad axis leftx {32767 if k % 2 else -32767}"), ("wait", 20), ("ctl", "vpad axis leftx 0"), ("wait", 20))],
            ("ctl", "vpad axis lefty 0"), ("wait", 30),
            # pause -> RETRY: the run starts again (the game is not restarted); the course's start view is the busy one
            ("press", "START"), ("wait", 40), ("press", "DOWN"), ("wait", 10), ("press", "A"), ("wait", 200),
            ("shot", "in_level_full"),
            ("ctl_match", "dd", r"mode=full .* mtx_hw=(42[1-9]|4[3-9]\d|[5-9]\d\d|1\d\d\d|20[0-4]\d) mtx_cap=2048 "),   # past the game's 420, no restart
            ("ctl_match", "dd", r"mtx_capped=0 "),
            ("ctl", "dd heap"),
        ]),
    ]),
]

# Draw distance stress (2026-10-23, the bigger display lists and the byte budget; optin): Full from the start. Airport (one of THPS3's
# busiest courses at Full) started DD_STRESS_N times (pause > RETRY runs the course gfx set-up again): each time the first ride with
# camera turns and quick setting changes (Original, Full, 2x, Full, a few frames apart); then END RUN and the same rides in Foundry and
# Tokyo (last: a competition, whose pause menu has no RETRY / END RUN at the usual places). The session sets THPS_DD_CANARY=1 (guard bytes
# after the display lists) and checks that the guards are on (`dd dlprobe` canary 1; until 2026-10-26 it only asked for the variable in
# this comment, and `canary_bad 0` passed with no guard at all). Expected: no guard word changed, no budget cut at the default budget,
# no panic, no failed heap request. The forced cuts are dd-cut's.
_DS_RIDE = [("ctl", "vpad axis lefty -32767"),
            *[x for k in range(6) for x in (("ctl", f"vpad axis leftx {(-32767, 32767)[k % 2]}"), ("wait", 15), ("ctl", "vpad axis leftx 0"), ("wait", 10))],
            ("ctl", "dd mode original"), ("wait", 4), ("ctl", "dd mode full"), ("wait", 4), ("ctl", "dd mode 2x"), ("wait", 4), ("ctl", "dd mode full"),
            *[x for k in range(4) for x in (("ctl", f"vpad axis leftx {(32767, -32767)[k % 2]}"), ("wait", 20))],
            ("ctl", "vpad axis lefty 0"), ("ctl", "vpad axis leftx 0"), ("wait", 45)]
_DS_END = [("press", "START"), ("wait", 40), ("menu", "pause", 4), ("press", "A"), ("wait", 120), ("press", "A"), ("wait", 60),
           ("press", "DOWN"), ("wait", 20), ("press", "DOWN"), ("wait", 20), ("press", "A"), ("wait", 150)]
_DS_START = [("press", "A"), ("wait", 150), ("press", "A"), ("wait_peek", "@gRunActive", 1, 60), ("vpad", "attach")]
_DS_CHECK = [("ctl_match", "dd", r"mode=full .* backoffs=\d+ panics=0 cuts=0 "), ("ctl_match", "dd dlprobe", r"canary 1 frames \d+ canary_bad 0 "),
             ("ctl_match", "dd heap", r" dl 147456 .* dl_fallbacks 0 .* failed_calls 0 ")]
_DS_KEYS = lambda key, n: [x for _ in range(n) for x in (("press", key), ("wait", 20))]   # THPS3's level select is a vertical list
SESSIONS += [
    dict(name="dd-stress", config="dd-stress-config", fresh_pak=True, wav=False, optin=True, env={"THPS_DD_CANARY": "1"},
         args=["--skip-intro", "--hidden", "--unlock-levels", "--draw-distance", "full", "--dd-buffers", "bigger"] + _os.environ.get("DD_ARGS", "").split(), scenarios=[
        ("dd_stress", "Airport starts and first rides, setting changes, camera turns; Foundry and Tokyo: guard bytes intact, no cut", [
            ("wait_for", "title"), ("go", "START", "title", "main_menu"), *CAREER_TO_GOALS[:-1],
            *_DS_KEYS("DOWN", 4), ("shot", "select_airport"),
            *_DS_START, ("ctl", "dd reset"),
            *[x for _ in range(int(_os.environ.get("DD_STRESS_N", "4"))) for x in (
                *_DS_RIDE, ("shot", "airport_ride"),
                ("press", "START"), ("wait", 40), ("menu", "pause", 1), ("press", "A"), ("wait", 150), ("vpad", "attach"))],
            *_DS_RIDE, ("ctl", "dd"), *_DS_CHECK, *_DS_END,
            *_DS_KEYS("UP", 4), ("shot", "select_foundry"),
            *_DS_START, *_DS_RIDE, ("shot", "foundry_ride"), ("ctl", "dd"), *_DS_CHECK, *_DS_END,
            *_DS_KEYS("DOWN", 7), ("shot", "select_tokyo"),
            *_DS_START, *_DS_RIDE, ("shot", "tokyo_ride"), ("ctl", "dd"), *_DS_CHECK,
        ]),
    ]),
]
# The display-list budget with a forced cap (review 2026-10-26, findings 9 and 10): Airport at Full with `dd dlbudget CAP` (DD_CUT_CAP,
# bytes) so tight that only some of the extra passes fit. The nearest extra items are reserved before the first pass with every pass at
# its bound, so the cuts leave out the farthest and none is made after the passes began (late_cuts=0: before the fix the passes after the
# first were counted at their average and an expensive far pass left the nearest ones out). The guard bytes are on (THPS_DD_CANARY) and
# intact. dd-stress checks the default budget (no cut at all).
_DC_RIDE = [("ctl", "vpad axis lefty -32767"),
            *[x for k in range(8) for x in (("ctl", f"vpad axis leftx {(-32767, 32767)[k % 2]}"), ("wait", 15), ("ctl", "vpad axis leftx 0"), ("wait", 10))],
            ("ctl", "vpad axis lefty 0"), ("wait", 20)]
SESSIONS += [
    dict(name="dd-cut", config="dd-cut-config", fresh_pak=True, wav=False, env={"THPS_DD_CANARY": "1"},
         args=["--skip-intro", "--hidden", "--unlock-levels", "--draw-distance", "full", "--window", "960x540"], scenarios=[
        ("dd_cut", "a forced display-list budget: the farthest extra items are left out before the passes, never the nearest after them", [
            *_fs_to_run(4, 30), ("vpad", "attach"),
            ("ctl_match", "dd dlprobe", r"canary 1 "),
            ("ctl", f"dd dlbudget {_os.environ.get('DD_CUT_CAP', '81920')} 0 0 0"), ("ctl", "dd reset"),
            *_DC_RIDE,
            ("ctl_match", "dd", r"cuts=[1-9]\d* cut_items=[1-9]\d* late_cuts=0 "),
            ("ctl_match", "dd dlprobe", r"canary 1 frames \d+ canary_bad 0 "),
            ("ctl", "dd dlbudget 0 0 0 0"),
        ]),
    ]),
]
# The bigger buffers on a constrained heap (review 2026-10-26, finding 1): THPS_DD_HEAP_FREE makes the planning see a free list of the given
# blocks from the course set-up's start, and every set-up request is taken from that view (`dd heap` view_fail counts the ones it could
# not have satisfied: the real allocator hangs there). One block of 266,240 bytes holds the game's own set-up (2 x 72 KiB lists, the
# matrix and vertex pools: 217,392) but not one 144 KiB list more: everything stays the game's size and nothing fails (before the fix the
# first list was enlarged and the second one's native size no longer fitted). With 600,000 + 900,000 bytes the lists and the matrix pools
# fit the first block, the bigger vertex pools would take from the second, the one later requests rely on: they stay the game's.
_DHP_TO_COURSE = [*_fs_to_run(0, 30)]
SESSIONS += [
    dict(name="dd-heap-plan", config="dd-heap-plan-config", fresh_pak=True, wav=False, env={"THPS_DD_HEAP_FREE": "266240"},
         args=["--skip-intro", "--hidden", "--draw-distance", "full", "--window", "960x540"], scenarios=[
        ("dd_heap_plan_tight", "a free list with room for the game's own set-up only: every buffer the game's size, no request that would fail", [
            *_DHP_TO_COURSE,
            ("log", r"draw distance: WARNING no room for a 147456-byte display list \(request 1"),
            ("ctl_match", "dd heap", r"mtx_pool 420 .* dl 73728 dl_game 73728 .* failed_calls 0 .* vtx_pool 500 .* view_fail 0"),
        ]),
    ]),
    dict(name="dd-heap-plan-room", config="dd-heap-plan-config", fresh_pak=True, wav=False, env={"THPS_DD_HEAP_FREE": "600000,900000"},
         args=["--skip-intro", "--hidden", "--draw-distance", "full", "--window", "960x540"], scenarios=[
        ("dd_heap_plan_room", "room for the bigger lists and matrix pools in the first block: those enlarged, the vertex pools left the game's", [
            *_DHP_TO_COURSE,
            ("ctl_match", "dd heap", r"mtx_pool 2048 .* dl 147456 dl_game 73728 .* failed_calls 0 .* vtx_pool 500 .* view_fail 0"),
        ]),
    ]),
]
