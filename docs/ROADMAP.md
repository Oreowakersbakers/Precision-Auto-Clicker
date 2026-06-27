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
- Keep state feedback compact, with active hotkey and minimal status in the Hotkey row.
- Move live performance into a footer-style metrics strip.
- Keep section headings compact and avoid helper text where the controls are self-explanatory.
- Preserve the current minimum-size guarantee: bottom actions must remain visible.

Acceptance checks:

- The screen reads in the same order as Option 1.
- Start/Stop remain visible at launch and minimum size.
- Existing controls still map to the same settings.
- No timing, click injection, repeat, hotkey, or stop behavior changes.

### 1b. Compactness Via Progressive Disclosure

Status: implemented for the collapsible Advanced layout; mini always-on-top mode deferred.

Goal: make the window feel right-sized for "set an interval and start," which is the dominant use, without removing any capability.

Decision (2026-06-26): the user's main concern was compactness, not visual design. Rather than fixed-size sections always on screen, the window now uses progressive disclosure — a small default that expands on demand. This intentionally supersedes the earlier "all four sections always visible" framing from the Option 1 slice; that earlier acceptance check no longer applies.

Implemented changes:

- Single narrow column instead of the 2×2 grid.
- Interval section, hotkey/advanced control bar, Start/Stop, and footer metrics are always visible.
- Click, Repeat, and Position collapse behind a visible `Advanced` toggle.
- The window sizes itself to its content in each state so nothing clips.

Future direction:

- Mini always-on-top mode: a tiny floating bar (interval + start/stop) that stays over other windows, with the full window available on demand. Deferred for now; build the collapse machinery so it can reuse the same show/hide and resize path.

Acceptance checks:

- The default (collapsed) window is noticeably smaller than the previous 2×2 layout.
- The `Advanced` toggle reveals and hides Click, Repeat, and Position, and the window resizes to fit each state.
- Start/Stop remain visible in both states and at minimum size.
- No timing, click injection, repeat, hotkey, or stop behavior changes.

### 2. Hotkey Settings

Status: completed for runtime hotkey changes.

Goal: make `F6` visible as a setting rather than only status text.

Expected changes:

- Add a Hotkey Settings row with current hotkey display.
- Support changing the hotkey with validation and conflict feedback.
- Keep the active hotkey reflected in the Hotkey row, Start/Stop buttons, global listener, and focused-window fallback.

Acceptance checks:

- Global `F6` still works.
- Focused-window `F6` fallback still works when global registration is unavailable.
- A changed hotkey such as `P` works globally when Windows registers it.
- If Windows cannot register the active hotkey, the focused-window fallback uses the same active hotkey.

### 3. Record And Playback

Status: deferred and not visible in the current UI.

Goal: introduce macro recording carefully later, without confusing it with basic auto clicking.

Expected changes:

- Do not show Record and Playback controls until the macro behavior, data model, and safety rules are defined.
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

- Keep estimated CPS visible in the footer metrics strip.
- Keep jitter, CPS, CPU, uptime, and click count in a footer-style strip.
- Keep interval timing confidence out of the form unless it directly helps operation.

Acceptance checks:

- Stats update while clicking.
- UI remains responsive at fast intervals.
- Performance labels fit without overlap at minimum size.

### 6. Packaging And Distribution

Status: initial packaging path implemented.

Goal: make the app easy for a non-coder to run and straightforward to release.

Expected changes:

- Stay with the current Python/Tkinter runtime for near-term packaging.
- Keep the repo-owned PyInstaller path working through `Build-Exe.ps1`, `Build-Exe.bat`, and `PrecisionAutoClicker.spec`.
- Decide later whether to stay with Python/Tkinter long term or move to a more native Windows framework.
- Add app icon, version display, and basic release notes.

Acceptance checks:

- Packaged app still uses Windows-native APIs.
- The elevated-app input caveat remains documented.
- Release steps exist in repo docs before sharing widely.

## First Implementation Slice

Status: completed for the current Tkinter UI. Future work should continue with Hotkey Settings, Record And Playback, Profiles And Presets, Timing Confidence, or Packaging And Distribution.

Implemented scope:

- Update `ui.py` to align the visible layout with Option 1.
- Add numbered section headers.
- Replace mouse button and click type comboboxes with segmented controls.
- Remove the top status strip and keep minimal state feedback in the Hotkey row.
- Keep Hotkey Settings visible, but do not show Record & Playback until macro behavior is planned.
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
- Keep the app usable for a non-coder: visible labels and obvious defaults. The one sanctioned exception to "no hidden modes" is the labeled `Advanced` collapse — it must stay clearly visible and obvious in state; do not hide core controls behind unlabeled or non-obvious gestures.
