# Precision Auto Clicker Spec

## Product Goal

Build a local Windows auto clicker that keeps the simplicity of OP Auto Clicker while improving clarity, timing quality, and operator confidence. Macro tooling remains a future direction and is not visible in the current UI.

## Target Users

- People who need repetitive mouse clicks for legitimate testing, QA, accessibility, productivity, or game-like personal workflows.
- Non-technical users who want an obvious start/stop flow and minimal setup.
- Power users who care about timing accuracy, hotkeys, fixed-position clicking, and repeat control.

## Current MVP Scope

- Native desktop window titled `Precision Auto Clicker`.
- Global start/stop hotkey toggles clicking; it defaults to `F6` and can be changed at runtime to a supported plain key.
- Click interval can be set in hours, minutes, seconds, and milliseconds.
- Mouse button can be left, right, or middle.
- Click type can be single, double, or triple.
- Repeat mode can be exact count or repeat until stopped.
- Cursor mode can use the current cursor location or a fixed X/Y point.
- Live performance shows total clicks, estimated CPS, jitter, CPU hint, and uptime.

## Product Principles

- The primary path should be readable top-to-bottom: interval, repeat, click options, cursor, hotkey feedback, performance, actions.
- Start and Stop must always be visible at the bottom of the main window at the supported minimum size.
- Defaults should be safe and understandable: current cursor location, left click, single click, repeat until stopped, `F6` toggle.
- Hotkey labels in the Hotkey row and Start/Stop buttons must reflect the active hotkey.
- The UI should explain state through labels and values, not through hidden behavior.
- Performance features should stay invisible until useful; users should not need to understand timers to use the app.

## Non-Goals For Now

- No cloud sync.
- No account system.
- No installer or auto-update system yet.
- No script marketplace.
- No bypass of Windows security or input-integrity protections.
- No stealth mode.

## Invariants

- Do not silently change the global start/stop hotkey behavior.
- Do not start clicking on app launch.
- Do not continue clicking after the user presses Stop, closes the app, or the repeat count is reached.
- Do not remove the elevated-app caveat: synthetic input may not reach higher-integrity apps.
- Do not change click injection, timer strategy, or repeat semantics without updating `ARCHITECTURE.md`, `TEST_PLAN.md`, and `CHANGELOG.md`.

## Acceptance Criteria

- At launch, the full action row is visible without resizing.
- At the minimum supported window size, the action row remains visible.
- The active hotkey toggles clicking globally while the app is open.
- Clicking runs on a worker thread and the UI remains responsive.
- Stop works from both the button and the active hotkey.
- Manual QA can verify exact repeat count, repeat-until-stopped, fixed position, and current position modes.
