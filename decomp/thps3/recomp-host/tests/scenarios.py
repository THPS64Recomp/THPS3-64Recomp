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