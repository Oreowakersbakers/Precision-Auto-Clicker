# Agent Instructions

Read these files before changing behavior:

1. `SPEC.md`
2. `ARCHITECTURE.md`
3. `TEST_PLAN.md`
4. `CHANGELOG.md`
5. `RESEARCH.md`

## Working Rules

- Keep changes small and tied to the user's request.
- Use the existing Python/Tkinter and Win32 `ctypes` structure unless the user approves a larger rewrite.
- Use `apply_patch` for manual file edits.
- Do not silently change product meaning, timing behavior, hotkey behavior, click injection, repeat semantics, or stop/close behavior.
- If behavior changes, update `SPEC.md`, `TEST_PLAN.md`, and `CHANGELOG.md` in the same change.
- If architecture changes, update `ARCHITECTURE.md`.
- Preserve the elevated-app caveat unless the implementation actually changes that Windows limitation.

## Validation Expectations

At minimum, run:

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m py_compile .\auto_clicker.py
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -c "import auto_clicker; print('import ok')"
```

For UI work, also launch the app and manually confirm the affected screen state.

## Safety Notes

- Do not test real clicking over destructive controls.
- Do not build stealth, bypass, evasion, or security-circumvention behavior.
- Do not add persistence, autostart, background operation, or network behavior without explicit user approval.

