# Precision Auto Clicker

A clean, lightweight Windows auto clicker built for predictable repetitive clicking. Precision Auto Clicker keeps the familiar OP Auto Clicker-style workflow, then adds a clearer interface, configurable hotkey, fixed-position clicking, and live timing feedback.

The app is local-only: no accounts, no cloud sync, no network behavior, no autostart, and no background persistence.

## Why Use It

- Simple start/stop flow with a global hotkey, defaulting to `F6`
- Clear interval controls for hours, minutes, seconds, and milliseconds
- Left, right, and middle mouse buttons
- Single, double, and triple click modes
- Repeat forever or stop after an exact physical click count
- Current cursor or fixed X/Y click position
- Live stats for click count, estimated CPS, jitter, CPU hint, and uptime
- Native Windows input through Win32 `SendInput`
- Source-available build path with PyInstaller

## Download

The recommended public download path is GitHub Releases.

Until the first release is published, build from source:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-Exe.ps1
```

The packaged app is written to:

```text
dist\Precision Auto Clicker\Precision Auto Clicker.exe
```

Optional single-file build:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-Exe.ps1 -OneFile
```

## Run From Source

From PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Start-AutoClicker.ps1
```

You can also double-click `Start-AutoClicker.bat`.

The launcher resolves Codex's bundled Python runtime first, then falls back to `py -3` and `python`.

## Safety Notes

- Do not test real clicking over destructive controls.
- The app does not start clicking on launch.
- Stop works from the button, the active hotkey, repeat completion, and app close.
- Synthetic input may not reach elevated or higher-integrity applications unless Precision Auto Clicker is running at the same integrity level.
- This project does not include stealth, bypass, evasion, persistence, autostart, or network behavior.

## Build Requirements

- Windows
- Python 3 with Tkinter
- PyInstaller for packaged builds

`Build-Exe.ps1` installs PyInstaller automatically if it is missing from the selected Python environment.

## Development Checks

Run the core checks before publishing a release:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m py_compile .\auto_clicker.py .\models.py .\win32_input.py .\timing.py .\click_engine.py .\hotkeys.py .\ui.py
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -c "import auto_clicker, models, win32_input, timing, click_engine, hotkeys, ui; print('import ok')"
```

See `TEST_PLAN.md` for manual QA and optional synthetic engine checks.

## Release Checklist

1. Run the development checks.
2. Build the EXE with `Build-Exe.ps1`.
3. Launch the packaged app from `dist`.
4. Confirm Start/Stop, active hotkey, repeat count, and fixed-position behavior using a safe click target.
5. Zip `dist\Precision Auto Clicker`.
6. Publish the zip on GitHub Releases with release notes from `CHANGELOG.md`.
7. Include a SHA256 checksum for the uploaded zip.

## Project Docs

These files are the source of truth for behavior and future changes:

- `SPEC.md`
- `ARCHITECTURE.md`
- `TEST_PLAN.md`
- `CHANGELOG.md`
- `RESEARCH.md`
- `ROADMAP.md`
- `AGENTS.md`

Behavior changes should update the relevant docs in the same change.

## License

Precision Auto Clicker is released under the MIT License. See `LICENSE` for details.
