# Agent Instructions

Detailed docs live under `docs/`. Read the smallest useful set for the task:

- Always read `docs/SPEC.md` before behavior, UI, timing, hotkey, repeat, click injection, stop/close, safety, or packaging changes.
- Read `docs/ARCHITECTURE.md` before architecture, threading, timing, Win32 input, hotkey lifecycle, packaging, or module-boundary changes.
- Read `docs/TEST_PLAN.md` before changing behavior or validation expectations.
- Read `docs/CHANGELOG.md` when preparing a user-facing change or release note.
- Use `docs/RELEASE_TEMPLATE.md` as the format source when drafting release
  notes; fill its placeholders rather than inventing a new structure.
- Read `docs/ROADMAP.md` when changing future direction, staged UI work, or deferred features.
- Read `docs/RESEARCH.md` only when historical OP Auto Clicker context or prior product research is relevant.

## Working Rules

- Keep changes small and tied to the user's request.
- Use the existing Python/Tkinter and Win32 `ctypes` structure unless the user approves a larger rewrite.
- Use `apply_patch` for manual file edits.
- Do not silently change product meaning, timing behavior, hotkey behavior, click injection, repeat semantics, or stop/close behavior.
- If behavior changes, update `docs/SPEC.md`, `docs/TEST_PLAN.md`, and `docs/CHANGELOG.md` in the same change.
- If architecture changes, update `docs/ARCHITECTURE.md`.
- If future product direction or staged UI work changes, update `docs/ROADMAP.md`.
- Keep `docs/CHANGELOG.md` focused on the current release cycle; move older detailed entries to an archive when it becomes hard to scan.
- Preserve the elevated-app caveat unless the implementation actually changes that Windows limitation.

## Validation Expectations

At minimum, run:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m py_compile .\auto_clicker.py
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -c "import auto_clicker; print('import ok')"
```

For UI work, also launch the app and manually confirm the affected screen state.

## Git Notes

- `git` may not be on `PATH` in this environment.
- If `git` is unavailable, use GitHub Desktop's bundled Git:

```powershell
& "$env:LOCALAPPDATA\GitHubDesktop\app-3.5.12\resources\app\git\cmd\git.exe" status --short
```

## Safety Notes

- Do not test real clicking over destructive controls.
- Do not build stealth, bypass, evasion, or security-circumvention behavior.
- Do not add persistence, autostart, background operation, or network behavior without explicit user approval.
