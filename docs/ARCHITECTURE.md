# Precision Auto Clicker Architecture

## Runtime

The app is currently a Python 3 desktop application using Tkinter for UI and `ctypes` for Win32 integration. This choice was made because `dotnet` was not available in the development environment and Tkinter ships with standard CPython on Windows.

Launcher:

- `Start-AutoClicker.ps1` resolves Python via the `py -3` launcher first.
- It falls back to `python` on `PATH`.

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
- The settings area is a single narrow column. The Interval section and the hotkey/advanced control bar are always visible; the Click, Repeat, and Position sections live in a collapsible `_advanced` frame toggled by the `Advanced` button.
- The action row and footer metrics strip are pinned to the bottom (packed bottom-up) and stay visible in both collapsed and expanded states.
- There is no dedicated status row. Transient feedback (fixed-point capture, click errors, global-hotkey-unavailable notice) is routed to the window title via `_set_status`, which appends `— <message>` to the base title and restores the plain title when cleared. This keeps the compact window free of a persistent status line; hard failures (invalid settings, cursor read failure, hotkey registration failure on change) still raise a message box.
- Footer metrics show jitter, estimated CPS, CPU hint, uptime, and click count as natural-width columns with a trailing spacer so the slim footer does not force a wide window.
- `_resize_to_content` sizes the window to fit each state. Because `RoundedPanel` is canvas-driven and does not report its content's true size, the main panel's height is pinned to its content's requested height (`pack_propagate(False)`) so Tk can compute the window height from real widget sizes, and the width is taken from the widest panel content (settings vs metrics). This keeps Start/Stop visible without clipping and adapts to font/DPI. `minsize` is updated to match on every toggle.

### `ClickEngine` (`click_engine.py`)

Runs clicking on a dedicated worker thread so the UI remains responsive. It accepts immutable `ClickSettings`, tracks performance stats, and reports those stats back through a queue. Internal click counts update on every sent click, while UI stats publication is throttled to roughly 20 Hz with a final update when the engine stops. Exact repeat counts are enforced as physical clicks, so the final double/triple packet may be reduced to avoid sending more clicks than requested.

Stop coordination uses a small stop signal wrapper backed by both Python `threading.Event` state and a Win32 manual-reset event handle. The Python state keeps the click loop checks readable, while the Win32 handle lets the high-resolution sleeper block until either the timer fires or Stop is requested. Pressing Stop signals the worker and returns immediately; the worker's final `running=False` stats frame drives the UI back to Ready, so a slow or wedged click injection cannot block the UI thread. Closing the app joins the worker and then closes the stop signal handle only once the worker has exited, so the handle is never freed while the sleeper may still be waiting on it.

### `HighResolutionSleeper` (`timing.py`)

Uses a high-resolution waitable timer when available. Timing uses `time.perf_counter()` for interval tracking. For sub-10 ms (high-CPS) intervals the click loop sleeps for most of each wait and reserves a small final busy-wait correction window for sub-millisecond accuracy. At or above a 10 ms interval the waitable timer is precise enough on its own, so the loop skips the busy-wait entirely and does not spin the CPU.

Longer sleeps wait on both the waitable timer and the click engine's stop signal through `WaitForMultipleObjects`, so Stop can interrupt a pending timer without polling every millisecond. If the Win32 stop event is unavailable, the sleeper falls back to the previous bounded 1 ms timer polling path.

### Win32 Input Layer (`win32_input.py`)

The app uses:

- `SendInput` for mouse injection.
- `SetCursorPos` for fixed-position mode.
- `GetCursorPos` for picking a fixed location.
- `RegisterHotKey` and `GetMessageW` for the active global start/stop hotkey.
- `timeBeginPeriod(1)` only while the click engine is active.

Mouse click packets are cached by button and multiplier so fast click loops do not rebuild the same `ctypes` `INPUT` arrays for every click. An unrecognized button name is rejected rather than defaulting to a left click. Fixed-position mode fails closed if `SetCursorPos` fails, so the app does not click at the current cursor location by mistake. `SendInput` must report the full packet length; a partial send releases the button (so it is not left physically down) and raises `PartialClickError`, which carries the count of whole clicks that landed so the stopped total stays accurate. Failed and partial sends stop the click run and surface the error in UI status. Button flags and the `SendInput` injection method remain unchanged.

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
