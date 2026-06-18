import ctypes
from dataclasses import dataclass
import threading

from win32_input import (
    MOD_NOREPEAT,
    MSG,
    WM_HOTKEY,
    WM_QUIT,
    kernel32,
    user32,
)


@dataclass(frozen=True)
class HotkeySpec:
    display: str
    vk_code: int
    tk_sequence: str


DEFAULT_HOTKEY = HotkeySpec("F6", 0x75, "<KeyPress-F6>")


def hotkey_from_keysym(keysym: str) -> HotkeySpec | None:
    key = keysym.strip()
    upper = key.upper()
    if len(upper) == 1 and "A" <= upper <= "Z":
        return HotkeySpec(upper, ord(upper), f"<KeyPress-{upper.lower()}>")
    if len(upper) == 1 and "0" <= upper <= "9":
        return HotkeySpec(upper, ord(upper), f"<KeyPress-{upper}>")
    if upper.startswith("F") and upper[1:].isdigit():
        number = int(upper[1:])
        if 1 <= number <= 12:
            return HotkeySpec(upper, 0x70 + number - 1, f"<KeyPress-{upper}>")
    return None


class HotkeyListener:
    def __init__(self, on_toggle, hotkey: HotkeySpec = DEFAULT_HOTKEY) -> None:
        self.on_toggle = on_toggle
        self.hotkey = hotkey
        self._thread: threading.Thread | None = None
        self._thread_id = 0
        self._ready = threading.Event()
        self.registered = False
        self.error_code = 0

    def start(self) -> bool:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._ready.wait(1.0)
        return self.registered

    def stop(self) -> None:
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread:
            self._thread.join(timeout=0.5)
        self._thread = None
        self._thread_id = 0
        self.registered = False

    def _run(self) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()
        ctypes.set_last_error(0)
        registered = user32.RegisterHotKey(None, 1, MOD_NOREPEAT, self.hotkey.vk_code)
        self.registered = bool(registered)
        self.error_code = 0 if registered else ctypes.get_last_error()
        self._ready.set()
        msg = MSG()
        try:
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_HOTKEY and msg.wParam == 1:
                    self.on_toggle()
        finally:
            if registered:
                user32.UnregisterHotKey(None, 1)
