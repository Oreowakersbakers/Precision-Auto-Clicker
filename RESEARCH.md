# Research Notes

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

The AI app-building workflow guide recommends keeping product meaning outside generated code through lightweight documents. This project now follows that pattern through `SPEC.md`, `ARCHITECTURE.md`, `TEST_PLAN.md`, `CHANGELOG.md`, and `AGENTS.md`.

