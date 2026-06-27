# Research Notes

This is optional historical context. Use it when comparing against OP Auto
Clicker, revisiting early product assumptions, or explaining why the current
architecture and UX direction were chosen. It is not required reading for small
implementation changes.

## OP Auto Clicker Findings

OP Auto Clicker is popular because it is small, free, simple, familiar, and focused on one obvious job: set an interval, choose click options, choose repeat/cursor behavior, and press a hotkey.

Important reference points from prior research:

- SourceForge listing for Orphamiel/OP Auto Clicker showed heavy ongoing downloads and many reviews.
- The Android listing had millions of installs and a high rating.
- Public screenshots show a compact utility UI organized around click interval, click options, click repeat, cursor position, hotkey, and record/playback.

## Internals Findings

The likely historical implementation pattern is a C# WinForms-style utility using:

- Global hotkey registration.
- Timer-driven clicking.
- Win32 input injection.

The better-performing architecture for this project is:

- `SendInput` for reliable mouse event batching.
- `RegisterHotKey` for global start/stop.
- Dedicated worker thread so the UI does not block timing.
- `perf_counter`/QPC-style timing for measurement.
- High-resolution waitable timer when available.
- `timeBeginPeriod(1)` only while the click engine is active.

## UX Opportunities

- Keep the OP-style mental model because it is already familiar.
- Improve scan order with clearer grouping and a status-first header.
- Make Start and Stop prominent and always visible.
- Show timing quality as live performance instead of hiding it.
- Add future macro recording carefully, with a clear model and safety boundaries.

## Source-Of-Truth Decision

Product meaning lives in `SPEC.md`, implementation boundaries in
`ARCHITECTURE.md`, validation in `TEST_PLAN.md`, release history in
`CHANGELOG.md`, and future direction in `ROADMAP.md`. These notes are supporting
context, not a required source of truth.
