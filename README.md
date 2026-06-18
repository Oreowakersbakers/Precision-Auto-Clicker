# Precision Auto Clicker

A Windows desktop auto clicker prototype inspired by OP Auto Clicker's compact layout, with a cleaner Precision Console UI and a dedicated Win32 click engine.

## Source Of Truth

Future agents should read these before changing behavior:

- `SPEC.md`
- `ARCHITECTURE.md`
- `TEST_PLAN.md`
- `AGENTS.md`
- `RESEARCH.md`
- `ROADMAP.md`
- `CHANGELOG.md`

## Run

From PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Start-AutoClicker.ps1
```

You can also double-click `Start-AutoClicker.bat`.

The launcher uses Codex's bundled Python runtime when available, then falls back to `py` or `python`.

## MVP Features

- Global start/stop hotkey via `RegisterHotKey`, defaulting to `F6` with runtime plain-key changes
- Mouse injection via `SendInput`
- Dedicated click thread separate from the UI
- High-resolution waitable timer with `timeBeginPeriod(1)` active only while clicking
- Current-cursor and fixed-position click modes
- Left, right, and middle mouse buttons
- Single, double, and triple click actions
- Repeat-until-stopped or exact repeat count
- Live actual interval, jitter, drift, and click count readout

## Notes

Some elevated apps may ignore synthetic input from a non-elevated process because of Windows input integrity rules. Run the clicker at the same integrity level as the target app when testing legitimate workflows.
