"""Headless smoke tests for the click engine.

These mock out the real Win32 ``send_click`` so the engine loop can be
exercised without moving the cursor or emitting real input. They guard the
two properties most likely to regress silently: the engine stops cleanly,
and the final published frame reports the exact number of clicks sent.

Run with: pytest
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click_engine
from models import ClickSettings


def _run_engine(settings, *, stop_after=None):
    """Run the engine with send_click mocked, returning (frames, send_count)."""
    sent = {"count": 0}

    def fake_send(button, multiplier, fixed_position):
        sent["count"] += multiplier
        return multiplier

    original = click_engine.send_click
    click_engine.send_click = fake_send
    try:
        frames = []
        engine = click_engine.ClickEngine(frames.append)
        engine.start(settings)
        if stop_after is not None:
            time.sleep(stop_after)
            engine.stop()
        engine.wait_for_stop(timeout=5.0)
    finally:
        click_engine.send_click = original
    return frames, sent["count"]


def test_repeat_count_run_reports_exact_total():
    # 250 single clicks at a 1ms interval exercises the high-CPS hot loop.
    frames, send_count = _run_engine(ClickSettings(0.001, "Left", 1, 250, None))

    assert send_count == 250
    assert frames, "engine should publish at least one stats frame"
    final = frames[-1]
    assert final.running is False
    assert final.clicks == 250


def test_until_stopped_final_frame_matches_sends():
    # Manual stop mid-run: the final frame must not under-report the count
    # even when the stop lands between throttled stats publishes.
    frames, send_count = _run_engine(
        ClickSettings(0.002, "Left", 1, None, None), stop_after=0.3
    )

    assert send_count > 0
    final = frames[-1]
    assert final.running is False
    assert final.clicks == send_count


def test_multiplier_does_not_overshoot_repeat_count():
    # Triple-click with an odd repeat count must stop exactly at the target.
    frames, send_count = _run_engine(ClickSettings(0.001, "Left", 3, 10, None))

    assert send_count == 10
    assert frames[-1].clicks == 10


if __name__ == "__main__":
    # Allow running without pytest: `python tests/test_click_engine.py`
    failures = 0
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            try:
                func()
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    raise SystemExit(1 if failures else 0)
