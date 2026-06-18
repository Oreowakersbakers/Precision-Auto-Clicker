# Changelog

## Unreleased

- Built the initial Windows desktop MVP with Tkinter, Win32 `SendInput`, global `F6`, dedicated click thread, high-resolution waitable timer support, fixed/current cursor modes, repeat modes, and live performance stats.
- Added source-of-truth project docs: `SPEC.md`, `ARCHITECTURE.md`, `TEST_PLAN.md`, `AGENTS.md`, and `RESEARCH.md`.
- Fixed the initial window sizing issue where the bottom action row could be clipped by pinning the action row to the bottom and increasing the supported minimum window height.
- Refactored the one-file MVP into focused modules for models, Win32 input, timing, click engine, hotkeys, UI, and the app entrypoint without changing user-facing behavior.
