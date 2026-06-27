import threading
import time
from collections import deque

from models import ClickSettings, EngineStats
from timing import HighResolutionSleeper, StopSignal, TimerResolution
from win32_input import send_click


STATS_PUBLISH_INTERVAL_SECONDS = 0.05
FINAL_CORRECTION_WINDOW_SECONDS = 0.00025


class ClickEngine:
    def __init__(self, on_stats) -> None:
        self.on_stats = on_stats
        self._thread: threading.Thread | None = None
        self._stop_event = StopSignal()
        self._stats = EngineStats()
        self._timer_resolution = TimerResolution()

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, settings: ClickSettings) -> None:
        if self.running:
            return
        self._stop_event.clear()
        self._stats = EngineStats(running=True)
        self._thread = threading.Thread(target=self._run, args=(settings,), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def wait_for_stop(self, timeout: float | None = None) -> None:
        thread = self._thread
        if thread and thread is not threading.current_thread():
            thread.join(timeout=timeout)

    def close(self) -> None:
        self.stop()
        self.wait_for_stop(timeout=1.0)
        self._stop_event.close()

    def _run(self, settings: ClickSettings) -> None:
        sleeper = HighResolutionSleeper()
        self._timer_resolution.begin()
        interval = max(settings.interval_seconds, 0.001)
        next_tick = time.perf_counter()
        sent_total = 0
        last_tick = next_tick
        last_stats_publish = next_tick
        jitter_samples: deque[float] = deque(maxlen=32)
        error_message = ""

        try:
            while not self._stop_event.is_set():
                now = time.perf_counter()
                remaining = next_tick - now
                if remaining > FINAL_CORRECTION_WINDOW_SECONDS:
                    sleeper.sleep(max(remaining - FINAL_CORRECTION_WINDOW_SECONDS, 0), self._stop_event)
                while not self._stop_event.is_set() and time.perf_counter() < next_tick:
                    time.sleep(0)
                if self._stop_event.is_set():
                    break

                fired_at = time.perf_counter()
                drift = (fired_at - next_tick) * 1000.0
                actual = (fired_at - last_tick) * 1000.0 if sent_total else interval * 1000.0
                last_tick = fired_at

                click_multiplier = settings.click_multiplier
                if settings.repeat_count is not None:
                    remaining_clicks = settings.repeat_count - sent_total
                    if remaining_clicks <= 0:
                        break
                    click_multiplier = min(click_multiplier, remaining_clicks)

                try:
                    sent = send_click(settings.button, click_multiplier, settings.fixed_position)
                except OSError as exc:
                    error_message = str(exc)
                    break

                sent_total += sent
                jitter_samples.append(abs(actual - interval * 1000.0))

                if fired_at - last_stats_publish >= STATS_PUBLISH_INTERVAL_SECONDS:
                    self._stats = EngineStats(
                        running=True,
                        clicks=sent_total,
                        actual_ms=actual,
                        jitter_ms=sum(jitter_samples) / len(jitter_samples),
                        drift_ms=drift,
                        cpu_hint="low" if interval >= 0.01 else "high precision",
                        error_message=error_message,
                    )
                    self.on_stats(self._stats)
                    last_stats_publish = fired_at

                if settings.repeat_count is not None and sent_total >= settings.repeat_count:
                    break
                next_tick += interval

                if next_tick < time.perf_counter() - interval:
                    next_tick = time.perf_counter() + interval
        finally:
            sleeper.close()
            self._timer_resolution.end()
            # Publish a fresh object rather than mutating the last-queued one
            # (avoids a torn read on the UI thread), but carry the last live
            # telemetry forward so the stopped readout freezes on real values
            # instead of snapping back to zeros.
            last = self._stats
            self._stats = EngineStats(
                running=False,
                clicks=sent_total,
                actual_ms=last.actual_ms,
                jitter_ms=last.jitter_ms,
                drift_ms=last.drift_ms,
                cpu_hint=last.cpu_hint,
                error_message=error_message,
            )
            self.on_stats(self._stats)
