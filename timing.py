import ctypes
import threading

from win32_input import (
    CREATE_WAITABLE_TIMER_HIGH_RESOLUTION,
    HANDLE,
    INFINITE,
    LARGE_INTEGER,
    SYNCHRONIZE,
    TIMER_MODIFY_STATE,
    WAIT_FAILED,
    WAIT_OBJECT_0,
    kernel32,
    winmm,
)


class TimerResolution:
    def __init__(self) -> None:
        self.active = False

    def begin(self) -> None:
        if winmm.timeBeginPeriod(1) == 0:
            self.active = True

    def end(self) -> None:
        if self.active:
            winmm.timeEndPeriod(1)
            self.active = False


class StopSignal:
    def __init__(self) -> None:
        self._event = threading.Event()
        self.handle = kernel32.CreateEventW(None, True, False, None)

    def set(self) -> None:
        self._event.set()
        if self.handle:
            kernel32.SetEvent(self.handle)

    def clear(self) -> None:
        self._event.clear()
        if self.handle:
            kernel32.ResetEvent(self.handle)

    def is_set(self) -> bool:
        return self._event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        return self._event.wait(timeout)

    def close(self) -> None:
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None


class HighResolutionSleeper:
    def __init__(self) -> None:
        self.handle = kernel32.CreateWaitableTimerExW(
            None,
            None,
            CREATE_WAITABLE_TIMER_HIGH_RESOLUTION,
            TIMER_MODIFY_STATE | SYNCHRONIZE,
        )

    def close(self) -> None:
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None

    def sleep(self, seconds: float, stop_event: threading.Event | StopSignal) -> None:
        if seconds <= 0:
            return
        if not self.handle:
            stop_event.wait(seconds)
            return
        due_time = LARGE_INTEGER(-int(seconds * 10_000_000))
        if not kernel32.SetWaitableTimer(self.handle, ctypes.byref(due_time), 0, None, None, False):
            stop_event.wait(seconds)
            return
        stop_handle = getattr(stop_event, "handle", None)
        if stop_handle:
            handles = (HANDLE * 2)(self.handle, stop_handle)
            result = kernel32.WaitForMultipleObjects(2, handles, False, INFINITE)
            if result in (WAIT_OBJECT_0, WAIT_OBJECT_0 + 1):
                return
            if result == WAIT_FAILED:
                stop_event.wait(seconds)
            return

        while not stop_event.is_set():
            result = kernel32.WaitForSingleObject(self.handle, 1)
            if result == WAIT_OBJECT_0:
                return
