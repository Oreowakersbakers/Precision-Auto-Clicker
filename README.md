# Precision Auto Clicker

A clean, lightweight Windows auto clicker built for predictable repetitive clicking. Precision Auto Clicker keeps the familiar OP Auto Clicker-style workflow, then adds a clearer interface, configurable hotkey, fixed-position clicking, and live timing feedback.

<p align="center">
  <img src="assets/new%20UI.png" alt="Precision Auto Clicker main window" width="480">
</p>

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

The easiest way to get it is from GitHub Releases. Grab the latest
`Precision Auto Clicker.exe` and run it. It is a single self-contained file,
so there is nothing to unzip or install.

To build from source instead, the simplest option is the single-file
executable:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-Exe.ps1 -OneFile
```

The packaged app is written to:

```text
dist\Precision Auto Clicker.exe
```

Both build modes use `PrecisionAutoClicker.spec`, so they share the same
analysis settings. To produce the folder bundle instead (a lightweight `.exe`
beside its dependencies, in `dist\Precision Auto Clicker\`), drop the flag:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-Exe.ps1
```

## Run From Source

From PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Start-AutoClicker.ps1
```

You can also double-click `Start-AutoClicker.bat`.

The launcher automatically finds your installed Python (`py -3` or `python`).

## Safety Notes

- Do not test real clicking over destructive controls.
- The app does not start clicking on launch.
- Stop works from the button, the active hotkey, repeat completion, and app close.
- Synthetic input may not reach elevated or higher-integrity applications unless Precision Auto Clicker is running at the same integrity level.
- This project does not include stealth, bypass, evasion, persistence, autostart, or network behavior.

## Is This Safe? (SmartScreen & Antivirus)

You may see security warnings the first time you run a downloaded build. This is
expected for a small, independently published tool, and does not mean the app is
malicious:

- **Windows SmartScreen** may show an "unrecognized app" / "unknown publisher"
  prompt. The executable is not code-signed with a paid certificate, so Windows
  has no reputation record for it yet. Choose **More info → Run anyway** if you
  trust the source.
- **Antivirus flags (false positives).** Auto clickers send synthetic mouse
  input, and the app is packaged with PyInstaller, so some antivirus engines may
  heuristically flag it as a "potentially unwanted application." This is a common
  false positive for tools of this type.

Because the project is source-available, you do not have to take the binary on
trust:

- Review the code in this repository. It is local-only with no network calls.
- Build the executable yourself from source (see **Download** above) instead of
  using a prebuilt binary.
- Verify a downloaded build against the SHA256 checksum published with each release.

## Build Requirements

- Windows
- Python 3 with Tkinter
- PyInstaller for packaged builds

`Build-Exe.ps1` installs PyInstaller automatically if it is missing from the selected Python environment.

## Development Checks

Run the core checks before publishing a release:

```powershell
python -m py_compile .\auto_clicker.py .\models.py .\win32_input.py .\timing.py .\click_engine.py .\hotkeys.py .\ui.py
python -c "import auto_clicker, models, win32_input, timing, click_engine, hotkeys, ui; print('import ok')"
```

If `python` is not on your `PATH`, use the Python launcher (`py -3`) instead.

For automated checks, run the headless engine smoke tests:

```powershell
python -m pytest tests
```

If pytest is not installed, the suite also runs standalone:

```powershell
python tests\test_click_engine.py
```

See `docs/TEST_PLAN.md` for manual QA and optional synthetic engine checks.

## Release Checklist

1. Run the development checks.
2. Build the single-file EXE with `Build-Exe.ps1 -OneFile`.
3. Launch `dist\Precision Auto Clicker.exe`.
4. Confirm Start/Stop, active hotkey, repeat count, and fixed-position behavior using a safe click target.
5. Publish `dist\Precision Auto Clicker.exe` on GitHub Releases with release notes from `docs/CHANGELOG.md`.
6. Include a SHA256 checksum for the uploaded `.exe`.

## Project Docs

These files are the source of truth for behavior and future changes. Detailed
docs live under `docs/`; `AGENTS.md` stays at the project root:

- `docs/SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/TEST_PLAN.md`
- `docs/CHANGELOG.md`
- `docs/RESEARCH.md`
- `docs/ROADMAP.md`
- `AGENTS.md`

Behavior changes should update the relevant docs in the same change.

## License

Precision Auto Clicker is released under the MIT License. See `LICENSE` for details.
