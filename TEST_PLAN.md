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

Optional packaging check:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Build-Exe.ps1
```

## Manual QA Checklist

- Launch with `.\Start-AutoClicker.ps1`.
- If PowerShell blocks scripts, launch with `Start-AutoClicker.bat` or run PowerShell with `-ExecutionPolicy Bypass`.
- Optionally run `.\Build-Exe.ps1` and confirm `dist\Precision Auto Clicker\Precision Auto Clicker.exe` is produced.
- Confirm the window opens titled `Precision Auto Clicker`.
- Confirm there is no separate in-window title header or top status strip.
- Confirm numbered sections are visible in order: `1 Interval`, `2 Click`, `3 Repeat`, `4 Position`.
- Confirm numbered section badges are circular and each section title has a light divider line.
- Confirm the numbered sections do not show helper description text under their headings.
- Confirm the Interval section does not repeat the interval total under the spinboxes.
- Confirm Button and Type use compact segmented controls, and the selected values map to the same left/right/middle and single/double/triple options.
- Confirm the compact Hotkey row is visible on launch, with the Change button next to the active hotkey and minimal state feedback after it.
- Confirm no Record & Playback row or macro buttons are visible.
- Confirm Start and Stop are the largest bottom actions and are visible on launch.
- Confirm the footer metrics strip shows jitter, CPS, CPU, uptime, and click count.
- Resize to the minimum allowed size and confirm the bottom action row remains visible.
- Maximize and restore the window; confirm layout remains coherent.
- Press Start and confirm status changes to Running.
- Press Stop and confirm status returns to Ready after the engine stops.
- Press `F6` to start and `F6` again to stop.
- Open Hotkey Settings, choose `P`, and confirm the Hotkey row and Start/Stop buttons all show `P`.
- Press `P` to start and `P` again to stop.
- If the app reports the active global hotkey is unavailable, focus the app window and confirm the focused active-hotkey fallback still starts and stops.
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
- If testing a packaged build, launch the EXE from `dist` and repeat the hotkey, repeat, and position checks in a safe target area.

## Regression Areas

- Bottom button visibility after UI edits.
- Global hotkey registration.
- Runtime hotkey rebinding.
- Global hotkey registration failure feedback and focused-window active-hotkey fallback.
- Worker thread stop behavior.
- Footer timing metric reporting.
- Current-location vs fixed-position clicking.

## Do Not Automate Blindly

Automated tests should not generate real clicks unless they use a deliberately safe sandbox target. Prefer import, settings validation, timer construction, and pure helper tests for automated coverage.
