# Changelog

Keep this file focused on the active release cycle plus recent releases. When it
becomes hard to scan, move older detailed entries into `docs/CHANGELOG_ARCHIVE.md`
and leave a compact version heading here with the release date and a one-line
summary.

## 1.1.0 - 2026-06-27

- Trimmed the project documentation workflow so agents read the docs relevant to
  the current change instead of treating every document as mandatory context.
- Marked research notes as optional historical context and pruned the roadmap so
  it emphasizes future direction over completed implementation history.
- Restructured the main window for compactness via progressive disclosure: the
  default view now shows only the Interval section, the Hotkey/Advanced control
  bar, and the bottom Start/Stop and metrics rows. The Click, Repeat, and
  Position sections are collapsed behind a visible `Advanced` toggle and
  revealed on demand. No click, timing, hotkey, repeat, or stop behavior
  changed.
- Switched the settings area from a fixed 2x2 grid to a single narrow column,
  and made the window size itself to its content in each state so Start/Stop stay
  visible without clipping and the layout adapts to font/DPI.
- Compacted the footer metrics strip to natural-width columns with a trailing
  spacer so the slim footer no longer forces a wide window.
- Removed the persistent status line, including the redundant "F6 toggles
  start/stop" hint. Transient feedback now rides in the window title bar via
  `_set_status`, reclaiming a full row in the compact view. Hard failures still
  raise a message box.

## 1.0.0 - 2026-06-24

- Initial Windows desktop MVP with Tkinter, Win32 `SendInput`, configurable
  hotkey, repeat and cursor modes, live stats, PyInstaller packaging,
  source-of-truth docs, focused modules, smoke tests, and the compact
  precision-console UI.
- Detailed 1.0.0 history lives in `docs/CHANGELOG_ARCHIVE.md`.
