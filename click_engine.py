import threading
import time

from models import ClickSettings, EngineStats
from timing import HighResolutionSleeper, TimerResolution
from win32_input import send_click


STATS_PUBLISH_INTERVAL_SECONDS = 0.05
FINAL_CORRECTION_WINDOW_SECONDS = 0.00025


class ClickEngine:
    def __init__(self, on_stats) -> None:
        self.on_stats = on_stats
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
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

    def _run(self, settings: ClickSettings) -> None:
        sleeper = HighResolutionSleeper()
        self._timer_resolution.begin()
        interval = max(settings.interval_seconds, 0.001)
        next_tick = time.perf_counter()
        sent_total = 0
        last_tick = next_tick
        last_stats_publish = next_tick
        jitter_samples: list[float] = []

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

                sent = send_click(settings.button, settings.click_multiplier, settings.fixed_position)
                sent_total += sent
                jitter_samples.append(abs(actual - interval * 1000.0))
                if len(jitter_samples) > 32:
                    jitter_samples.pop(0)

                self._stats = EngineStats(
                    running=True,
                    clicks=sent_total,
                    actual_ms=actual,
                    jitter_ms=sum(jitter_samples) / len(jitter_samples),
                    drift_ms=drift,
                    cpu_hint="low" if interval >= 0.01 else "high precision",
                )
                if fired_at - last_stats_publish >= STATS_PUBLISH_INTERVAL_SECONDS:
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
            self._stats.running = False
            self.on_stats(self._stats)
