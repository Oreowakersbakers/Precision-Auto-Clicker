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
import hotkeys
from models import ClickSettings
from win32_input import PartialClickError


def _run_engine(settings, *, stop_after=None, send=None, calls=None):
    """Run the engine with send_click mocked, returning (frames, send_count).

    ``send`` overrides the default counting stub (e.g. to raise or to sleep);
    it receives (button, multiplier, fixed_position). ``calls`` is an optional
    list that each call tuple is appended to for pass-through assertions.
    """
    sent = {"count": 0}

    def fake_send(button, multiplier, fixed_position):
        if calls is not None:
            calls.append((button, multiplier, fixed_position))
        if send is not None:
            result = send(button, multiplier, fixed_position)
            sent["count"] += result
            return result
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


def test_send_click_error_stops_engine_and_reports_partial_count():
    # send_click raises on the 4th call; the engine must stop on its own and
    # report exactly the 3 successful clicks that preceded the failure (the
    # exception fires before sent_total is accumulated for the 4th).
    state = {"calls": 0}

    def flaky(button, multiplier, fixed_position):
        state["calls"] += 1
        if state["calls"] >= 4:
            raise OSError(5, "SendInput failed")
        return multiplier

    frames, send_count = _run_engine(
        ClickSettings(0.001, "Left", 1, None, None), send=flaky
    )

    final = frames[-1]
    assert final.running is False
    assert final.clicks == 3
    assert send_count == 3
    # str(OSError(5, ...)) -> "[Errno 5] SendInput failed", so match a substring.
    assert "SendInput failed" in final.error_message


def test_partial_send_counts_clicks_that_landed():
    # A PartialClickError carries the whole clicks that landed before the
    # failure; the engine must add them to the final total rather than drop the
    # packet entirely. Here calls 1-2 land 1 click each, then call 3 fails after
    # 2 of its clicks landed -> final count is 4.
    state = {"calls": 0}

    def flaky(button, multiplier, fixed_position):
        state["calls"] += 1
        if state["calls"] == 3:
            raise PartialClickError(2, 5, "SendInput sent 5 of 6 input events")
        return multiplier

    frames, _ = _run_engine(ClickSettings(0.001, "Left", 1, None, None), send=flaky)

    final = frames[-1]
    assert final.running is False
    assert final.clicks == 4
    assert "SendInput sent 5 of 6" in final.error_message


def test_stats_fields_are_computed_not_zeroed():
    # Coarse 10 ms interval -> cpu_hint "low"; the computed timing fields must
    # carry real values (not the dataclass zero-defaults) in both a live frame
    # and the frozen final frame.
    frames, _ = _run_engine(ClickSettings(0.01, "Left", 1, 20, None))

    live = [f for f in frames if f.running]
    assert live, "engine should publish at least one in-loop stats frame"
    sample = live[-1]
    assert sample.cpu_hint == "low"
    assert sample.actual_ms > 0.0
    assert sample.jitter_ms >= 0.0

    final = frames[-1]
    assert final.running is False
    assert final.cpu_hint == "low"
    assert final.actual_ms > 0.0  # frozen on real telemetry, not reset to zero


def test_cpu_hint_marks_high_precision_below_threshold():
    # Sub-10 ms interval must report "high precision" (a pure interval threshold).
    frames, _ = _run_engine(ClickSettings(0.001, "Left", 1, 300, None))

    live = [f for f in frames if f.running]
    assert live, "engine should publish at least one in-loop stats frame"
    assert all(f.cpu_hint == "high precision" for f in live)


def test_hotkey_from_keysym_exact_codes():
    a = hotkeys.hotkey_from_keysym("a")
    assert a is not None and a.vk_code == 0x41 and a.display == "A"

    five = hotkeys.hotkey_from_keysym("5")
    assert five is not None and five.vk_code == 0x35

    f1 = hotkeys.hotkey_from_keysym("F1")
    assert f1 is not None and f1.vk_code == 0x70

    f12 = hotkeys.hotkey_from_keysym("F12")
    assert f12 is not None and f12.vk_code == 0x7B

    for bad in ("F0", "F13", "!", ""):
        assert hotkeys.hotkey_from_keysym(bad) is None, bad

    # A bare "F" is the *letter* F (matched by the A-Z branch), not an
    # incomplete F-key, so it is a valid letter hotkey rather than None.
    f_letter = hotkeys.hotkey_from_keysym("F")
    assert f_letter is not None and f_letter.vk_code == 0x46 and f_letter.display == "F"

    # strip + case folding path resolves to the default F6 hotkey.
    f6 = hotkeys.hotkey_from_keysym(" f6 ")
    assert f6 is not None and f6.vk_code == 0x75 == hotkeys.DEFAULT_HOTKEY.vk_code


def test_button_and_fixed_position_pass_through():
    # Guards click_engine's send_click(button, multiplier, fixed_position) call
    # against dropped or swapped arguments.
    calls = []
    frames, send_count = _run_engine(
        ClickSettings(0.001, "Left", 1, 5, (640, 480)), calls=calls
    )

    assert calls, "engine should fire at least once"
    assert all(button == "Left" for button, _, _ in calls)
    assert all(fixed_position == (640, 480) for _, _, fixed_position in calls)


def test_drift_resync_does_not_burst_after_stall():
    # A count-based assertion is insufficient here: with repeat_count the total
    # is hard-capped regardless of the resync guard, so a count check would pass
    # even if the guard were removed. We must assert on cadence instead.
    interval = 0.01
    stall = interval * 50
    times = []
    state = {"calls": 0}

    def stalling(button, multiplier, fixed_position):
        times.append(time.perf_counter())
        state["calls"] += 1
        if state["calls"] == 1:
            # Simulate a deschedule on the very first tick.
            time.sleep(stall)
        return multiplier

    frames, send_count = _run_engine(
        ClickSettings(interval, "Left", 1, None, None),
        stop_after=stall + interval * 20,
        send=stalling,
    )

    assert len(times) >= 2, "engine should keep firing after the stall"
    stall_end = times[1]  # first click after the stalled first call returned
    burst = sum(1 for t in times[1:] if t <= stall_end + 0.002)
    # Without the resync guard the engine would try to "catch up" the ~50
    # missed ticks in a flood; the guard caps it to ~1 immediate click.
    assert burst <= 3, f"resync burst too large: {burst} clicks within 2ms"


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
