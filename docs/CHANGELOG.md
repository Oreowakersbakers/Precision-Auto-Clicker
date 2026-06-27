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

### Post-review hardening

Follow-up fixes from the code review's lower-priority findings. The five
top-priority items were addressed earlier in this cycle.

- Timing: the final busy-wait correction now runs only for sub-10 ms (high-CPS)
  intervals. Coarse intervals rely on the high-resolution waitable timer alone,
  which removes a small idle CPU spin with no change to high-CPS accuracy.
- Stop: pressing Stop no longer briefly joins the worker on the UI thread, so a
  slow or wedged click injection can no longer freeze the window. The worker's
  final `running=False` stats frame drives the return to Ready.
- Close: the stop-signal handle is released only after the worker has actually
  exited, avoiding a close-during-wait race on the handle.
- Click injection: a partial `SendInput` now reports how many whole clicks
  landed before failing, so the stopped click total stays accurate; an
  unrecognized mouse button is rejected with a clear error instead of silently
  falling back to a left click.
- UI state: Start is disabled while clicking and Stop is disabled while stopped;
  a repeat Start no longer resets the uptime origin mid-run; re-pressing
  `Pick location` restarts the 2 s countdown instead of stacking captures.
- Engine setup: the high-resolution sleeper and timer resolution are acquired
  inside the guarded block so they are always released on the way out.
- Tests: added coverage for partial-send click counting and for the computed
  timing/`cpu_hint` stats fields.

## 1.0.0 - 2026-06-24

- Initial Windows desktop MVP with Tkinter, Win32 `SendInput`, configurable
  hotkey, repeat and cursor modes, live stats, PyInstaller packaging,
  source-of-truth docs, focused modules, smoke tests, and the compact
  precision-console UI.
- Detailed 1.0.0 history lives in `docs/CHANGELOG_ARCHIVE.md`.
