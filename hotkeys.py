import ctypes
import threading

from win32_input import (
    MOD_NOREPEAT,
    MSG,
    VK_F6,
    WM_HOTKEY,
    WM_QUIT,
    kernel32,
    user32,
)


class HotkeyListener:
    def __init__(self, on_toggle) -> None:
        self.on_toggle = on_toggle
        self._thread: threading.Thread | None = None
        self._thread_id = 0
        self._ready = threading.Event()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(1.0)

    def stop(self) -> None:
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread:
            self._thread.join(timeout=0.5)

    def _run(self) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()
        registered = user32.RegisterHotKey(None, 1, MOD_NOREPEAT, VK_F6)
        self._ready.set()
        msg = MSG()
        try:
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_HOTKEY and msg.wParam == 1:
                    self.on_toggle()
        finally:
            if registered:
                user32.UnregisterHotKey(None, 1)
