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

## Build An EXE

From PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-Exe.ps1
```

Or double-click:

- `Build-Exe.bat`

What this does:

- Resolves Python the same way as the source launcher.
- Installs `PyInstaller` automatically if it is missing.
- Builds a windowed PyInstaller app from `PrecisionAutoClicker.spec`.
- Writes the packaged app to `dist\Precision Auto Clicker\Precision Auto Clicker.exe`.

Optional single-file build:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-Exe.ps1 -OneFile
```

That writes:

- `dist\Precision Auto Clicker.exe`

Notes:

- Packaging does not remove the Windows integrity-level limitation for synthetic input.
- The built EXE should be tested against the same safe click targets used for source runs.

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
