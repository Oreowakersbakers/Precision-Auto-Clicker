from dataclasses import dataclass


@dataclass(frozen=True)
class ClickSettings:
    interval_seconds: float
    button: str
    click_multiplier: int
    repeat_count: int | None
    fixed_position: tuple[int, int] | None


@dataclass
class EngineStats:
    running: bool = False
    clicks: int = 0
    actual_ms: float = 0.0
    jitter_ms: float = 0.0
    drift_ms: float = 0.0
    cpu_hint: str = "low"
    error_message: str = ""
