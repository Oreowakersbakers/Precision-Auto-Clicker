# Precision Auto Clicker Roadmap

This document is the forward-looking product and design plan. Future agents should use it with `SPEC.md`, `ARCHITECTURE.md`, `TEST_PLAN.md`, `RESEARCH.md`, and `AGENTS.md`.

## Design North Star

Primary visual reference:

- `references/auto clicker visual reference.png`
- Chosen direction: Option 1, the numbered Precision Console concept.

The app should feel like a native, calm Windows utility: clear, compact, and confident. It should keep OP Auto Clicker's familiar mental model while improving scan order, hierarchy, and operator feedback.

## Current Baseline

The project now has a maintainable module split:

- `auto_clicker.py`: entrypoint.
- `ui.py`: Tkinter UI.
- `click_engine.py`: worker thread and click loop.
- `hotkeys.py`: global/focused `F6` behavior.
- `timing.py`: high-resolution waitable timer helpers.
- `win32_input.py`: Win32 mouse and cursor APIs.
- `models.py`: shared data models.

The app already supports interval selection, click options, repeat modes, cursor position modes, `F6` start/stop, live stats, and a Windows-native input engine.

## Product Direction

### 1. UI/UX Alignment To Option 1

Goal: make the implemented Tkinter interface more closely match the selected visual reference without changing click behavior.

Expected changes:

- Add numbered section headers: `1 Interval`, `2 Click`, `3 Repeat`, `4 Position`.
- Convert mouse button and click type dropdowns into segmented controls for faster scanning.
- Keep Start and Stop as the largest bottom actions.
- Add clearer top status summary with Ready/Running, hotkey, profile, estimated CPS, and interval.
- Move live performance into a footer-style metrics strip similar to the reference.
- Add helper text under section headings where it improves confidence.
- Preserve the current minimum-size guarantee: bottom actions must remain visible.

Acceptance checks:

- The screen reads in the same order as Option 1.
- Start/Stop remain visible at launch and minimum size.
- Existing controls still map to the same settings.
- No timing, click injection, repeat, hotkey, or stop behavior changes.

### 2. Hotkey Settings

Goal: make `F6` visible as a setting rather than only status text.

Expected changes:

- Add a Hotkey Settings row with current hotkey display.
- Add a disabled or informational `Change...` button first if full rebinding is not implemented yet.
- Later, support changing the hotkey with validation and conflict feedback.

Acceptance checks:

- Global `F6` still works.
- Focused-window `F6` fallback still works when global registration is unavailable.
- Any future custom hotkey must be documented in `SPEC.md`, `ARCHITECTURE.md`, and `TEST_PLAN.md`.

### 3. Record And Playback

Goal: introduce macro recording carefully, without confusing it with basic auto clicking.

Expected changes:

- Keep Record and Playback visible as a planned capability.
- Before implementing actual recording, define the macro data model and safety rules.
- Show unavailable states clearly if buttons are not functional yet.

Acceptance checks:

- The app must never start recording silently.
- Playback must have an obvious stop path.
- Macro behavior must not change the core auto-clicker loop without explicit planning.

### 4. Profiles And Presets

Goal: make common configurations easy to reuse.

Expected changes:

- Turn Profile into a real setting with saved values.
- Add simple presets such as Default, QA Testing, and Clicker Game.
- Store profiles locally in a readable format only after the user approves persistence.

Acceptance checks:

- Defaults remain safe.
- Profile load/save must not start clicking.
- Any persistence format must be documented in `ARCHITECTURE.md`.

### 5. Timing Confidence

Goal: make performance understandable without exposing too much machinery.

Expected changes:

- Keep estimated CPS visible in the top strip.
- Keep jitter, drift, CPU, and uptime in a footer-style strip.
- Clarify interval total, for example `Total: 100 milliseconds (0.100 s)`.

Acceptance checks:

- Stats update while clicking.
- UI remains responsive at fast intervals.
- Performance labels fit without overlap at minimum size.

### 6. Packaging And Distribution

Goal: eventually make the app easy for a non-coder to run.

Expected changes:

- Decide whether to stay with Python/Tkinter or move to a more native Windows framework.
- If staying with Python, evaluate PyInstaller or a similar packaging path.
- Add app icon, version display, and basic release notes.

Acceptance checks:

- Packaged app still uses Windows-native APIs.
- The elevated-app input caveat remains documented.
- Release steps and rollback notes exist before sharing widely.

## First Implementation Slice

Status: completed for the current Tkinter UI. Future work should continue with Hotkey Settings, Record And Playback, Profiles And Presets, Timing Confidence, or Packaging And Distribution.

Implemented scope:

- Update `ui.py` to align the visible layout with Option 1.
- Add numbered section headers.
- Replace mouse button and click type comboboxes with segmented controls.
- Improve the top status strip and footer metrics strip.
- Keep Hotkey Settings and Record & Playback as visible rows if feasible, but do not implement new hotkey rebinding or real macro recording in this slice.
- Preserve behavior and module boundaries.

Required docs to update in that slice:

- `CHANGELOG.md`
- `TEST_PLAN.md` if manual QA changes.
- `SPEC.md` only if user-facing behavior changes.
- `ARCHITECTURE.md` only if module boundaries or control-state flow changes.

Required validation:

- Compile all Python files.
- Import all modules.
- Launch the app and confirm the window opens.
- Manually inspect the layout against `references/auto clicker visual reference.png`.
- Confirm Start/Stop remain visible at launch and minimum size.

## Guardrails

- Do not change the click engine while doing visual work.
- Do not change timing strategy while doing visual work.
- Do not implement persistence, custom hotkeys, or macro playback without a separate plan.
- Do not remove safety caveats.
- Keep the app usable for a non-coder: visible labels, obvious defaults, and no hidden modes.
