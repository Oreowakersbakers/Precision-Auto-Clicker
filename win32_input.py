import ctypes


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
winmm = ctypes.WinDLL("winmm", use_last_error=True)

DWORD = ctypes.c_uint32
UINT = ctypes.c_uint
LONG = ctypes.c_long
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
HANDLE = ctypes.c_void_p
LPVOID = ctypes.c_void_p

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

WAIT_OBJECT_0 = 0x00000000
WAIT_FAILED = 0xFFFFFFFF
INFINITE = 0xFFFFFFFF
CREATE_WAITABLE_TIMER_HIGH_RESOLUTION = 0x00000002
TIMER_MODIFY_STATE = 0x0002
SYNCHRONIZE = 0x00100000

WM_HOTKEY = 0x0312
WM_QUIT = 0x0012
MOD_NOREPEAT = 0x4000


class POINT(ctypes.Structure):
    _fields_ = [("x", LONG), ("y", LONG)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", LONG),
        ("dy", LONG),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", DWORD), ("u", INPUT_UNION)]


class LARGE_INTEGER(ctypes.Structure):
    _fields_ = [("QuadPart", ctypes.c_longlong)]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", HANDLE),
        ("message", UINT),
        ("wParam", ctypes.c_size_t),
        ("lParam", ctypes.c_ssize_t),
        ("time", DWORD),
        ("pt", POINT),
    ]


user32.SendInput.argtypes = (UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = UINT
user32.SetCursorPos.argtypes = (ctypes.c_int, ctypes.c_int)
user32.SetCursorPos.restype = ctypes.c_bool
user32.GetCursorPos.argtypes = (ctypes.POINTER(POINT),)
user32.GetCursorPos.restype = ctypes.c_bool
user32.RegisterHotKey.argtypes = (HANDLE, ctypes.c_int, UINT, UINT)
user32.RegisterHotKey.restype = ctypes.c_bool
user32.UnregisterHotKey.argtypes = (HANDLE, ctypes.c_int)
user32.UnregisterHotKey.restype = ctypes.c_bool
user32.GetMessageW.argtypes = (ctypes.POINTER(MSG), HANDLE, UINT, UINT)
user32.GetMessageW.restype = ctypes.c_int
user32.PostThreadMessageW.argtypes = (DWORD, UINT, ctypes.c_size_t, ctypes.c_ssize_t)
user32.PostThreadMessageW.restype = ctypes.c_bool

kernel32.GetCurrentThreadId.argtypes = ()
kernel32.GetCurrentThreadId.restype = DWORD
kernel32.CreateEventW.argtypes = (LPVOID, ctypes.c_bool, ctypes.c_bool, ctypes.c_wchar_p)
kernel32.CreateEventW.restype = HANDLE
kernel32.SetEvent.argtypes = (HANDLE,)
kernel32.SetEvent.restype = ctypes.c_bool
kernel32.ResetEvent.argtypes = (HANDLE,)
kernel32.ResetEvent.restype = ctypes.c_bool
kernel32.CreateWaitableTimerExW.argtypes = (LPVOID, ctypes.c_wchar_p, DWORD, DWORD)
kernel32.CreateWaitableTimerExW.restype = HANDLE
kernel32.SetWaitableTimer.argtypes = (
    HANDLE,
    ctypes.POINTER(LARGE_INTEGER),
    ctypes.c_long,
    LPVOID,
    LPVOID,
    ctypes.c_bool,
)
kernel32.SetWaitableTimer.restype = ctypes.c_bool
kernel32.WaitForSingleObject.argtypes = (HANDLE, DWORD)
kernel32.WaitForSingleObject.restype = DWORD
kernel32.WaitForMultipleObjects.argtypes = (DWORD, ctypes.POINTER(HANDLE), ctypes.c_bool, DWORD)
kernel32.WaitForMultipleObjects.restype = DWORD
kernel32.CloseHandle.argtypes = (HANDLE,)
kernel32.CloseHandle.restype = ctypes.c_bool

winmm.timeBeginPeriod.argtypes = (UINT,)
winmm.timeBeginPeriod.restype = UINT
winmm.timeEndPeriod.argtypes = (UINT,)
winmm.timeEndPeriod.restype = UINT

BUTTON_FLAGS = {
    "Left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
    "Right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
    "Middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
}
INPUT_SIZE = ctypes.sizeof(INPUT)
_CLICK_PACKET_CACHE: dict[tuple[str, int], ctypes.Array] = {}


class PartialClickError(OSError):
    """Raised when ``SendInput`` injected only part of a click packet.

    ``completed`` is the number of whole (down+up) clicks that landed before the
    partial failure, so the engine can still count them. Subclasses ``OSError``
    so the click loop's existing ``except OSError`` handling catches it unchanged.
    """

    def __init__(self, completed: int, *args: object) -> None:
        super().__init__(*args)
        self.completed = completed


def _click_packet(button: str, multiplier: int):
    count = max(multiplier, 1)
    key = (button, count)
    packet = _CLICK_PACKET_CACHE.get(key)
    if packet is not None:
        return packet

    down, up = BUTTON_FLAGS[button]
    packet = (INPUT * (count * 2))()
    for idx in range(count):
        packet[idx * 2].type = INPUT_MOUSE
        packet[idx * 2].u.mi = MOUSEINPUT(0, 0, 0, down, 0, 0)
        packet[idx * 2 + 1].type = INPUT_MOUSE
        packet[idx * 2 + 1].u.mi = MOUSEINPUT(0, 0, 0, up, 0, 0)
    _CLICK_PACKET_CACHE[key] = packet
    return packet


def _release_button(button: str) -> None:
    # Send a lone button-UP. Idempotent: an UP on an already-released button is
    # an OS no-op, so this is safe to fire unconditionally after a partial send.
    up_flag = BUTTON_FLAGS[button][1]
    release = INPUT()
    release.type = INPUT_MOUSE
    release.u.mi = MOUSEINPUT(0, 0, 0, up_flag, 0, 0)
    user32.SendInput(1, ctypes.byref(release), INPUT_SIZE)


def send_click(button: str, multiplier: int, fixed_position: tuple[int, int] | None) -> int:
    if button not in BUTTON_FLAGS:
        # Fail loud instead of silently injecting a Left click. OSError keeps the
        # engine's "only OSError is caught" stop-and-report contract intact.
        raise OSError(f"unknown mouse button: {button!r}")

    if fixed_position is not None:
        ctypes.set_last_error(0)
        if not user32.SetCursorPos(int(fixed_position[0]), int(fixed_position[1])):
            error = ctypes.get_last_error()
            raise OSError(error, "SetCursorPos failed; click was not sent")

    inputs = _click_packet(button, multiplier)
    ctypes.set_last_error(0)
    sent = user32.SendInput(len(inputs), inputs, INPUT_SIZE)
    if sent != len(inputs):
        error = ctypes.get_last_error()
        # A partial send may leave the button physically down; release it before
        # raising, and carry the count of whole clicks that did land.
        _release_button(button)
        raise PartialClickError(
            int(sent // 2),
            error,
            f"SendInput sent {int(sent)} of {len(inputs)} input events",
        )
    return int(sent // 2)


def get_cursor_position() -> tuple[int, int]:
    point = POINT()
    if not user32.GetCursorPos(ctypes.byref(point)):
        raise OSError(ctypes.get_last_error())
    return int(point.x), int(point.y)
