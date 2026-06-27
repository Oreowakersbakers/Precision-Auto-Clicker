# Changelog Archive

Detailed entries move here when `CHANGELOG.md` becomes hard to scan. Keep the
main changelog focused on the active release cycle plus compact release
summaries.

## 1.0.0 - 2026-06-24

- Made the single-file build (`Build-Exe.ps1 -OneFile`) drive from
  `PrecisionAutoClicker.spec` via the `PAC_ONEFILE` switch, so folder and
  single-file builds share one source of truth for analysis settings instead of
  the one-file path bypassing the spec. Single-file is now the recommended
  distribution format.
- Fixed the uptime readout resetting to `00:00:00` on stop; it now freezes at
  the final elapsed time and holds until the next clicking session starts.
- Trimmed the click loop's hot path: stats objects are now built and jitter is
  averaged only when publishing, roughly 20 Hz, rather than on every tick, with
  a bounded deque for jitter samples and an accurate final click total on stop.
- Surfaced the application version (`1.0.0`) in the window title.
- Added headless smoke tests (`tests/test_click_engine.py`) covering clean stop
  and exact final click counts for repeat-count, until-stopped, and
  click-multiplier runs.
- Organized source-of-truth documentation under `docs/`, leaving `README.md`
  and `AGENTS.md` at the project root.
- Built the initial Windows desktop MVP with Tkinter, Win32 `SendInput`, global
  `F6`, dedicated click thread, high-resolution waitable timer support,
  fixed/current cursor modes, repeat modes, and live performance stats.
- Added source-of-truth project docs: `SPEC.md`, `ARCHITECTURE.md`,
  `TEST_PLAN.md`, `AGENTS.md`, and `RESEARCH.md`.
- Fixed the initial window sizing issue where the bottom action row could be
  clipped by pinning the action row to the bottom and increasing the supported
  minimum window height.
- Refactored the one-file MVP into focused modules for models, Win32 input,
  timing, click engine, hotkeys, UI, and the app entrypoint without changing
  user-facing behavior.
- Added visible feedback when Windows cannot register global `F6`, plus an
  app-focused `F6` fallback for that failure case.
- Added `ROADMAP.md` to capture future product steps, with Option 1 UI/UX
  alignment as the next implementation slice.
- Aligned the Tkinter UI with the Option 1 precision-console direction:
  numbered sections, segmented click controls, visible Hotkey Settings, larger
  Start/Stop actions, and a footer metrics strip.
- Refined the Option 1 visual alignment with circular section numbers, light
  divider rules beside section titles, and rounded panel surfaces.
- Fixed section heading divider alignment so each numbered section shows a
  consistent rule length.
- Implemented runtime hotkey changes for supported plain keys, with the active
  hotkey reflected in the Hotkey row, Start/Stop buttons, global listener, and
  focused-window fallback.
- Added a repo-owned PyInstaller packaging path with `Build-Exe.ps1`,
  `Build-Exe.bat`, and `PrecisionAutoClicker.spec` so Windows EXE builds are
  reproducible from the project root.
- Compacted the main window by removing the separate in-window title header,
  per-section helper descriptions, the duplicate interval total inside the
  Interval section, and excess vertical space below the lower settings row.
- Further compacted the main window by removing the top status strip, removing
  the visible Record & Playback row, normalizing smaller UI font sizes,
  tightening click segmented controls, and showing CPS instead of drift in the
  footer metrics.
- Moved the Hotkey Change button next to the active hotkey value so the compact
  Hotkey row reads as a single control group.
- Reduced the main window width while preserving the compact two-column layout
  and bottom action visibility.
- Reduced numeric spinbox widths for interval, repeat count, and fixed X/Y
  inputs, then lowered the launch and minimum window widths to make the app
  noticeably narrower without changing behavior.
- Improved fast-interval performance by throttling stats publication to roughly
  20 Hz plus final stop updates, narrowing the click loop's active correction
  window, caching reusable `SendInput` click packets, coalescing stale UI stats
  events, avoiding repeated state label writes, and reducing rounded panel
  redraw work.
- Reduced long-sleep wakeups by having the high-resolution sleeper wait on both
  the waitable timer and the engine stop signal, preserving stop responsiveness
  without polling every millisecond.
- Tightened click safety and edge cases: fixed-position failures no longer click
  at the current cursor, partial `SendInput` results stop the run with status
  feedback, exact repeat counts no longer overshoot with Double or Triple click
  types, app-focused alphanumeric hotkeys no longer toggle while typing into
  fields, Stop/close now clean up the stop signal, and invalid numeric settings
  show clear validation errors.
