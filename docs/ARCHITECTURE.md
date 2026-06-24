# Precision Auto Clicker Architecture

## Runtime

The app is currently a Python 3 desktop application using Tkinter for UI and `ctypes` for Win32 integration. This choice was made because `dotnet` was not available in the local environment and Tkinter was available in the bundled Codex Python runtime.

Launcher:

- `Start-AutoClicker.ps1` resolves Codex bundled Python first.
- It falls back to `py -3` and then `python`.

Main app entrypoint:

- `auto_clicker.py`

Modules:

- `models.py`: shared `ClickSettings` and `EngineStats` data models.
- `win32_input.py`: Win32 `ctypes` bindings, input structures, cursor helpers, and `SendInput` click injection.
- `timing.py`: high-resolution waitable timer sleeper and timer-resolution helpers.
- `click_engine.py`: worker thread click loop, repeat handling, timing stats, and stop coordination.
- `hotkeys.py`: configurable global `RegisterHotKey` listener, defaulting to `F6`.
- `ui.py`: Tkinter `PrecisionConsole` UI.
- `version.py`: single source of the application version string.

Tests:

- `tests/test_click_engine.py`: headless smoke tests for the click engine (mock `send_click`); runnable via `pytest` or directly.

## Major Components

### `PrecisionConsole` (`ui.py`)

Owns the Tkinter window, form state, validation, action buttons, status text, and live stat rendering.

Layout rules:

- The native window title carries the app name without a separate in-window title header or bulky top status strip.
- Action row is pinned to the bottom.
- Settings panel fills the remaining middle space.
- Minimal state and hotkey feedback live in the compact Hotkey row.
- Footer metrics show jitter, estimated CPS, CPU hint, uptime, and click count.
- Minimum window size must fit the full current workflow.

### `ClickEngine` (`click_engine.py`)

Runs clicking on a dedicated worker thread so the UI remains responsive. It accepts immutable `ClickSettings`, tracks performance stats, and reports those stats back through a queue. Internal click counts update on every sent click, while UI stats publication is throttled to roughly 20 Hz with a final update when the engine stops. Exact repeat counts are enforced as physical clicks, so the final double/triple packet may be reduced to avoid sending more clicks than requested.

Stop coordination uses a small stop signal wrapper backed by both Python `threading.Event` state and a Win32 manual-reset event handle. The Python state keeps the click loop checks readable, while the Win32 handle lets the high-resolution sleeper block until either the timer fires or Stop is requested. Stop briefly joins the worker after signaling it; closing the app also joins and closes the stop signal handle.

### `HighResolutionSleeper` (`timing.py`)

Uses a high-resolution waitable timer when available. Timing uses `time.perf_counter()` for interval tracking. The click loop sleeps for most of each wait and reserves a small final correction window for high-precision 1-2 ms intervals.

Longer sleeps wait on both the waitable timer and the click engine's stop signal through `WaitForMultipleObjects`, so Stop can interrupt a pending timer without polling every millisecond. If the Win32 stop event is unavailable, the sleeper falls back to the previous bounded 1 ms timer polling path.

### Win32 Input Layer (`win32_input.py`)

The app uses:

- `SendInput` for mouse injection.
- `SetCursorPos` for fixed-position mode.
- `GetCursorPos` for picking a fixed location.
- `RegisterHotKey` and `GetMessageW` for the active global start/stop hotkey.
- `timeBeginPeriod(1)` only while the click engine is active.

Mouse click packets are cached by button and multiplier so fast click loops do not rebuild the same `ctypes` `INPUT` arrays for every click. Fixed-position mode fails closed if `SetCursorPos` fails, so the app does not click at the current cursor location by mistake. `SendInput` must report the full packet length; failed or partial sends stop the click run and surface the error in UI status. Button flags and the `SendInput` injection method remain unchanged.

## Threading Model

- Tkinter runs on the main thread.
- Hotkey listener runs on a daemon thread and posts events into a queue.
- Hotkey state is represented by `HotkeySpec`, which carries the UI display value, Win32 virtual-key code, and Tk focused-fallback binding.
- Runtime hotkey changes stop the existing listener, bind the new focused fallback sequence, and start a new listener.
- The focused fallback only toggles when the global hotkey is unavailable. For alphanumeric hotkeys, the fallback does not toggle from text-entry controls so users can type into settings fields.
- Click engine runs on a daemon thread and posts stats into the same queue.
- UI updates happen only from the Tkinter main thread through `_drain_events`.

## Critical Boundaries

Changes to these areas require explicit planning and doc updates:

- Click timing strategy.
- Mouse injection method.
- Hotkey registration and lifecycle.
- Stop/close behavior.
- Repeat semantics.
- Any future macro recording or playback model.

## Known Platform Constraint

Windows may block synthetic input into elevated or higher-integrity applications when this app is not running at the same integrity level.
