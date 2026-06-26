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
- Invalid numeric settings are rejected with a settings error instead of being silently adjusted.

## Product Principles

- The window favors compactness through progressive disclosure: the Interval section, hotkey/advanced control bar, Start/Stop actions, and footer metrics are always visible, while Click, Repeat, and Position collapse behind a clearly labeled `Advanced` toggle. The default view stays small for the common "set interval, start" path.
- The primary path reads top-to-bottom in a single column: interval, hotkey/advanced control, then (when expanded) click options, repeat, cursor; with performance and actions pinned at the bottom.
- Progressive disclosure is collapse, not concealment: the `Advanced` toggle is always visible and labeled, defaults remain safe, and the current state is obvious. This is the one sanctioned exception to avoiding hidden controls.
- Start and Stop must always be visible at the bottom of the main window at the supported minimum size, in both collapsed and expanded states.
- The window sizes itself to its content in each state so no section clips; defaults should be safe and understandable: current cursor location, left click, single click, repeat until stopped, `F6` toggle.
- Hotkey labels in the Hotkey row and Start/Stop buttons must reflect the active hotkey.
- The UI should explain state through labels and values; aside from the labeled `Advanced` collapse, it should not rely on hidden behavior.
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
- Exact repeat count is a physical click limit; double and triple click types must not send clicks past that count.
- Fixed-position clicks must not send a click if Windows cannot move the cursor to the requested fixed point.
- Do not remove the elevated-app caveat: synthetic input may not reach higher-integrity apps.
- Do not change click injection, timer strategy, or repeat semantics without updating `ARCHITECTURE.md`, `TEST_PLAN.md`, and `CHANGELOG.md`.

## Acceptance Criteria

- At launch, the full action row is visible without resizing.
- At the minimum supported window size, the action row remains visible.
- The active hotkey toggles clicking globally while the app is open.
- Clicking runs on a worker thread and the UI remains responsive.
- Stop works from both the button and the active hotkey.
- Manual QA can verify exact repeat count, repeat-until-stopped, fixed position, and current position modes.
