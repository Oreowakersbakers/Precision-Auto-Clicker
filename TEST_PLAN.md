# Precision Auto Clicker Test Plan

## Automated Checks

Run from PowerShell:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m py_compile .\auto_clicker.py .\models.py .\win32_input.py .\timing.py .\click_engine.py .\hotkeys.py .\ui.py
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -c "import auto_clicker, models, win32_input, timing, click_engine, hotkeys, ui; print('import ok')"
```

Optional timer check:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -c "from timing import HighResolutionSleeper; s=HighResolutionSleeper(); print(bool(s.handle)); s.close()"
```

## Manual QA Checklist

- Launch with `.\Start-AutoClicker.ps1`.
- If PowerShell blocks scripts, launch with `Start-AutoClicker.bat` or run PowerShell with `-ExecutionPolicy Bypass`.
- Confirm the window opens titled `Precision Auto Clicker`.
- Confirm Start, Stop, Hotkeys, and Record & Playback are visible on launch.
- Resize to the minimum allowed size and confirm the bottom action row remains visible.
- Maximize and restore the window; confirm layout remains coherent.
- Press Start and confirm status changes to Running.
- Press Stop and confirm status returns to Ready after the engine stops.
- Press `F6` to start and `F6` again to stop.
- Set interval to 100 ms and confirm live performance is roughly 10 CPS.
- Set interval to 10 ms and confirm UI remains responsive while running.
- Test left, right, and middle click only in a safe target area.
- Test single, double, and triple click in a safe target area.
- Test repeat count with a small number and confirm it stops automatically.
- Test repeat until stopped and confirm Stop interrupts it.
- Test Pick location, wait 2 seconds, and confirm X/Y update.
- Test fixed-position mode in a safe target area.
- Close the app while stopped.
- Close the app while running and confirm clicking stops.

## Regression Areas

- Bottom button visibility after UI edits.
- Global hotkey registration.
- Worker thread stop behavior.
- Timing drift and jitter reporting.
- Current-location vs fixed-position clicking.

## Do Not Automate Blindly

Automated tests should not generate real clicks unless they use a deliberately safe sandbox target. Prefer import, settings validation, timer construction, and pure helper tests for automated coverage.
