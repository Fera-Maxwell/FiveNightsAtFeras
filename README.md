# 📁 Insanity At Fera's — Version a0.0.3 (Early Alpha)

**Developer Note:** This repository contains the core logic for a horror-survival project. The current focus is on stability, AI framework, and interface architecture.

---

### 🕹️ REPOSITORY STATUS (Current GitHub Build)
The following features are currently pushed and functional in the Python source:

* **Engine Foundation:** Core game loop, multi-view state management, and platform-aware path handling.
* **Main Menu:** Full navigation with `Continue`, `New Game`, `Custom Night`, `Options`, and `Exit`. Mouse hover and keyboard both supported. Blinking cursor effect and animated static overlay.
* **Save System:** Persistent save and config files stored per-platform (`AppData` on Windows, `~/.local/share` on Linux).
* **Settings:** Subtitles and Static FX toggles with live ON/OFF display, saved to disk.
* **Confirmation Screen:** New Game prompts wipe confirmation before erasing save data.
* **Office View:** Background art loaded from `assets/Office_ALPHA.png`. Door controls (A/D to close left/right) and door lights (Q/E) functional with power drain.
* **Camera System:** 12-node camera network with CRT static/glitch overlay, dial-in mode (press K), name-based or number-based navigation, and CRT hum audio.
* **Attack Pipeline:** Characters progress through a forced `roaming → hall → door_cam → at_door` sequence. 20-second attack timer at door. Closing the door clamps timer to 5 seconds and forces retreat to spawn.
* **AI Movement:** Per-character AI level scaling (0–20). Movement tick fires every 5 seconds at 1/20 base chance per AI level.
* **Night Progression:** Nights 1–5 unlock sequentially on completion. Night 5 unlocks Custom Night. Save persists across sessions.
* **Custom Night:** Per-character AI sliders (0–20) with visual bars. Secret numeric code input (press C). Easter egg at code `6969`.
* **Game Over / Win Screens:** Death screen names the attacker. Win screen saves night progress.
* **Night Counter:** Current night number displayed on camera HUD above the time/power readout.
* **Jay's Video Time:** Passive drain system — drains while not watching CAM 09, refills when watching. (Vent entry not yet implemented.)
* **The "NULL" Handler:** 1/420 chance per camera interaction. Crashes the feed and exits after 2 seconds. Suppressed in dev mode.
* **Dev Mode:** Type `fera` on the main menu to toggle. Enables terminal pipeline logging, door/light overlay, F1/F2 teleport hotkeys, and NULL immunity.

---

### 🚀 OVERALL PROJECT GOALS (The Vision)

#### 1. AI & Behavior
* **Directed Pathing:** Character-specific routes replacing random roaming (N1 detour variants, N2+ direct paths).
* **May's Kitchen Linger:** 60-second hold at CAM 08 before continuing her route.
* **Jay's Vent Entry:** Triggered when Video Time hits 0%.
* **Jason's Blind Spot:** Bathroom detour with no camera coverage.

#### 2. Visuals & Content
* **Camera Art:** Per-room images for all 12 camera nodes.
* **Door Animation:** Single PNG sprite sliding up/down, mirrored for right side.
* **Jumpscares:** Per-character death animations.
* **Phone Calls:** Night 1–5 audio with subtitle support.

#### 3. Technical Polish
* **Universal Display Support:** Legacy (640x480), standard (1280x720), Full HD (1920x1080).
* **Compiled Builds:** Windows `.exe` and Linux binary via PyInstaller.

#### 4. Story Content
* **Night 5 Ending:** May special kill — stun + delayed Fera finish.
* **Nights 6/7** *(v1.1)* and **Night 8 / NULL sequence** *(v1.2, code: 2009)*.

---

### 🛠️ KNOWN ISSUES / BUGS

* **Camera 12:** Feed displays as `????`. Unintended behavior.
${\color{#0d1117}\text{FERA WILL SUFFER FROM HER CRIMES}}$
* **Console Logs:** Occasional `NULL` reference strings during runtime. Also intended.
* **Jason / Jay:** Configurable in Custom Night but no active attack behavior yet. Jay's Video Time drains but does not trigger vent entry.
* **Door Lights:** Toggle functional but no visual effect in office view yet (art pending).

---

### ⚠️ SYSTEM REQUIREMENTS
* **Language:** Python 3.10+
* **Dependencies:** `arcade`
* **OS:** Windows 10/11 (64-bit) · Linux (tested on Ubuntu 24)
* **Optimal Resolution:** 1280x720 (Required — no scaling yet)

---
*End of File.*