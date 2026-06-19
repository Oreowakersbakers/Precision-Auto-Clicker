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

## Major Components

### `PrecisionConsole` (`ui.py`)

Owns the Tkinter window, form state, validation, action buttons, status text, and live stat rendering.

Layout rules:

- Status strip sits at the top; the native window title carries the app name without a separate in-window title header.
- Action row is pinned to the bottom.
- Settings panel fills the remaining middle space.
- Minimum window size must fit the full current workflow.

### `ClickEngine` (`click_engine.py`)

Runs clicking on a dedicated worker thread so the UI remains responsive. It accepts immutable `ClickSettings`, tracks performance stats, and reports those stats back through a queue.

### `HighResolutionSleeper` (`timing.py`)

Uses a high-resolution waitable timer when available. Timing uses `time.perf_counter()` for interval tracking.

### Win32 Input Layer (`win32_input.py`)

The app uses:

- `SendInput` for mouse injection.
- `SetCursorPos` for fixed-position mode.
- `GetCursorPos` for picking a fixed location.
- `RegisterHotKey` and `GetMessageW` for the active global start/stop hotkey.
- `timeBeginPeriod(1)` only while the click engine is active.

## Threading Model

- Tkinter runs on the main thread.
- Hotkey listener runs on a daemon thread and posts events into a queue.
- Hotkey state is represented by `HotkeySpec`, which carries the UI display value, Win32 virtual-key code, and Tk focused-fallback binding.
- Runtime hotkey changes stop the existing listener, bind the new focused fallback sequence, and start a new listener.
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
