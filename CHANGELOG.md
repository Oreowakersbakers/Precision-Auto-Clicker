# Changelog

## Unreleased

- Built the initial Windows desktop MVP with Tkinter, Win32 `SendInput`, global `F6`, dedicated click thread, high-resolution waitable timer support, fixed/current cursor modes, repeat modes, and live performance stats.
- Added source-of-truth project docs: `SPEC.md`, `ARCHITECTURE.md`, `TEST_PLAN.md`, `AGENTS.md`, and `RESEARCH.md`.
- Fixed the initial window sizing issue where the bottom action row could be clipped by pinning the action row to the bottom and increasing the supported minimum window height.
- Refactored the one-file MVP into focused modules for models, Win32 input, timing, click engine, hotkeys, UI, and the app entrypoint without changing user-facing behavior.
- Added visible feedback when Windows cannot register global `F6`, plus an app-focused `F6` fallback for that failure case.
- Added `ROADMAP.md` to capture future product steps, with Option 1 UI/UX alignment as the next implementation slice.
- Aligned the Tkinter UI with the Option 1 precision-console direction: numbered sections, segmented click controls, a richer top status strip, visible Hotkey Settings and Record & Playback rows, larger Start/Stop actions, and a footer metrics strip.
- Refined the Option 1 visual alignment with circular section numbers, light divider rules beside section titles, and rounded panel surfaces.
