# Precision Auto Clicker Test Plan

## Automated Checks

Run from PowerShell:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m py_compile .\auto_clicker.py .\models.py .\win32_input.py .\timing.py .\click_engine.py .\hotkeys.py .\ui.py
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -c "import auto_clicker, models, win32_input, timing, click_engine, hotkeys, ui; print('import ok')"
```

Optional synthetic click-engine performance check that avoids real click injection:

```powershell
@'
import time
import click_engine
from models import ClickSettings

seen = []
click_engine.send_click = lambda *_args: 1
engine = click_engine.ClickEngine(seen.append)
engine.start(ClickSettings(0.001, "Left", 1, 80, None))
deadline = time.perf_counter() + 2
while engine.running and time.perf_counter() < deadline:
    time.sleep(0.01)
print(seen[-1].clicks if seen else 0, len(seen), seen[-1].running if seen else None)
'@ | & "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Optional synthetic stop-latency check that avoids real click injection:

```powershell
@'
import time
import click_engine
from models import ClickSettings

seen = []
click_engine.send_click = lambda *_args: 1
engine = click_engine.ClickEngine(seen.append)
engine.start(ClickSettings(1.0, "Left", 1, None, None))
time.sleep(0.05)
started = time.perf_counter()
engine.stop()
deadline = time.perf_counter() + 1
while engine.running and time.perf_counter() < deadline:
    time.sleep(0.001)
elapsed_ms = (time.perf_counter() - started) * 1000
print(round(elapsed_ms, 2), engine.running, seen[-1].running if seen else None)
'@ | & "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Optional synthetic exact-repeat check that avoids real click injection:

```powershell
@'
import time
import click_engine
from models import ClickSettings

sent_packets = []
def fake_send(_button, multiplier, _fixed):
    sent_packets.append(multiplier)
    return multiplier

seen = []
click_engine.send_click = fake_send
engine = click_engine.ClickEngine(seen.append)
engine.start(ClickSettings(0.001, "Left", 3, 5, None))
deadline = time.perf_counter() + 1
while engine.running and time.perf_counter() < deadline:
    time.sleep(0.001)
print(seen[-1].clicks if seen else 0, sent_packets, engine.running)
'@ | & "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
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
- Confirm the numeric spinboxes are compact but still comfortably show typical 1- to 4-digit values for interval, repeat count, and fixed X/Y coordinates.
- Confirm no Record & Playback row or macro buttons are visible.
- Confirm Start and Stop are the largest bottom actions and are visible on launch.
- Confirm the footer metrics strip shows jitter, CPS, CPU, uptime, and click count.
- Resize to the minimum allowed size and confirm the narrower two-column layout remains coherent, the compact numeric inputs still read cleanly, and the bottom action row remains visible.
- Maximize and restore the window; confirm layout remains coherent.
- Press Start and confirm status changes to Running.
- Press Stop and confirm status returns to Ready after the engine stops.
- Press `F6` to start and `F6` again to stop.
- Open Hotkey Settings, choose `P`, and confirm the Hotkey row and Start/Stop buttons all show `P`.
- Press `P` to start and `P` again to stop.
- If the app reports the active global hotkey is unavailable, focus the app window and confirm the focused active-hotkey fallback still starts and stops.
- If the focused active-hotkey fallback is an alphanumeric key, focus a numeric or text field and confirm typing that key edits the field instead of toggling clicking.
- Enter an invalid numeric value, such as a blank interval field or repeat count `0`, and confirm Start shows a clear settings error without starting.
- Set interval to 100 ms and confirm live performance is roughly 10 CPS.
- Set interval to 10 ms and confirm UI remains responsive while running.
- Set interval to 1 ms only in a safe target area, or with click injection monkeypatched, and confirm the click count keeps advancing while the UI remains responsive.
- Test left, right, and middle click only in a safe target area.
- Test single, double, and triple click in a safe target area.
- Test repeat count with a small number and confirm it stops automatically.
- Test repeat count with Double or Triple selected and confirm the final click total does not exceed the requested exact count.
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
- Worker thread close cleanup and stop signal handle closure.
- Stop latency while a long waitable-timer sleep is pending.
- Footer timing metric reporting.
- Current-location vs fixed-position clicking.
- Fixed-position and `SendInput` failure handling.
- Numeric settings validation.

## Do Not Automate Blindly

Automated tests should not generate real clicks unless they use a deliberately safe sandbox target. Prefer import, settings validation, timer construction, and pure helper tests for automated coverage.
