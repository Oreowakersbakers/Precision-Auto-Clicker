import queue
import tkinter as tk
from tkinter import messagebox, ttk

from click_engine import ClickEngine
from hotkeys import HotkeyListener
from models import ClickSettings, EngineStats
from win32_input import get_cursor_position


class PrecisionConsole(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Precision Auto Clicker")
        self.geometry("780x640")
        self.minsize(760, 620)
        self.configure(bg="#f6f7f8")

        self.events: queue.Queue[str] = queue.Queue()
        self.engine = ClickEngine(self._queue_stats)
        self.hotkeys = HotkeyListener(lambda: self.events.put("toggle"))

        self.hours = tk.IntVar(value=0)
        self.minutes = tk.IntVar(value=0)
        self.seconds = tk.IntVar(value=0)
        self.milliseconds = tk.IntVar(value=100)
        self.button = tk.StringVar(value="Left")
        self.click_type = tk.StringVar(value="Single")
        self.repeat_mode = tk.StringVar(value="until")
        self.repeat_count = tk.IntVar(value=1)
        self.position_mode = tk.StringVar(value="current")
        self.x_pos = tk.IntVar(value=0)
        self.y_pos = tk.IntVar(value=0)
        self.status = tk.StringVar(value="Ready")
        self.status_detail = tk.StringVar(value="F6 toggles start/stop")
        self.cps = tk.StringVar(value="10.0 CPS")
        self.clicks = tk.StringVar(value="0 clicks")
        self.actual = tk.StringVar(value="Actual -- ms")
        self.jitter = tk.StringVar(value="Jitter -- ms")
        self.drift = tk.StringVar(value="Drift -- ms")
        self.cpu = tk.StringVar(value="CPU idle")

        self._build_styles()
        self._build_ui()
        self.after(100, self._drain_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind_all("<F6>", self._on_f6_key)
        if not self.hotkeys.start():
            self.status_detail.set(f"Global F6 unavailable ({self.hotkeys.error_code}); app-focused F6 still works")

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), background="#f6f7f8")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Soft.TFrame", background="#f6f7f8")
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 18), background="#f6f7f8", foreground="#171a1f")
        style.configure("Muted.TLabel", background="#f6f7f8", foreground="#6b7280")
        style.configure("Panel.TLabel", background="#ffffff", foreground="#1f2937")
        style.configure("Section.TLabel", font=("Segoe UI Semibold", 11), background="#ffffff", foreground="#111827")
        style.configure("Stat.TLabel", background="#ffffff", foreground="#4b5563")
        style.configure("Primary.TButton", font=("Segoe UI Semibold", 11), padding=(20, 12))
        style.configure("Danger.TButton", font=("Segoe UI Semibold", 11), padding=(20, 12))
        style.map("Primary.TButton", background=[("active", "#0f7a4f")])
        style.configure("Primary.TButton", background="#12805c", foreground="#ffffff", bordercolor="#12805c")
        style.configure("Danger.TButton", background="#ffffff", foreground="#9f1239", bordercolor="#e5e7eb")
        style.configure("TButton", padding=(12, 8), background="#ffffff", bordercolor="#d8dde6")
        style.configure("TSpinbox", arrowsize=13, padding=(7, 5))
        style.configure("TCombobox", padding=(7, 5))
        style.configure("TRadiobutton", background="#ffffff")

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, style="Soft.TFrame", padding=16)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="Soft.TFrame")
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text="Precision Auto Clicker", style="Title.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.status_detail, style="Muted.TLabel").pack(side="right", pady=(8, 0))

        status_bar = ttk.Frame(outer, style="Panel.TFrame", padding=(14, 10))
        status_bar.pack(fill="x", pady=(0, 10))
        self._status_dot = tk.Canvas(status_bar, width=10, height=10, highlightthickness=0, bg="#ffffff")
        self._status_dot.create_oval(1, 1, 9, 9, fill="#22c55e", outline="")
        self._status_dot.pack(side="left", padx=(0, 8))
        ttk.Label(status_bar, textvariable=self.status, style="Panel.TLabel", font=("Segoe UI Semibold", 10)).pack(side="left")
        ttk.Separator(status_bar, orient="vertical").pack(side="left", fill="y", padx=16)
        ttk.Label(status_bar, text="Profile", style="Stat.TLabel").pack(side="left")
        ttk.Combobox(status_bar, values=("Default", "QA testing", "Clicker game"), width=14, state="readonly").pack(side="left", padx=(8, 16))
        ttk.Label(status_bar, text="Hotkey F6", style="Stat.TLabel").pack(side="left", padx=(0, 16))
        ttk.Label(status_bar, textvariable=self.cps, style="Stat.TLabel").pack(side="right")

        actions = ttk.Frame(outer, style="Soft.TFrame")
        actions.pack(side="bottom", fill="x", pady=(12, 0))
        self.start_button = ttk.Button(actions, text="Start  F6", style="Primary.TButton", command=self.start_clicking)
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.stop_button = ttk.Button(actions, text="Stop  F6", style="Danger.TButton", command=self.stop_clicking)
        self.stop_button.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(actions, text="Hotkeys", command=self._hotkey_note).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(actions, text="Record & Playback", command=self._macro_note).pack(side="left", fill="x", expand=True)

        main = ttk.Frame(outer, style="Panel.TFrame", padding=14)
        main.pack(side="top", fill="both", expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)

        self._section_interval(main).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        self._section_click(main).grid(row=1, column=0, sticky="nsew", padx=(0, 18), pady=(0, 14))
        self._section_repeat(main).grid(row=1, column=1, sticky="nsew", pady=(0, 14))
        self._section_position(main).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        self._section_performance(main).grid(row=3, column=0, columnspan=2, sticky="ew")

    def _section_interval(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        ttk.Label(frame, text="Click interval", style="Section.TLabel").grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))
        for idx, (label, var, width) in enumerate(
            (("hours", self.hours, 5), ("mins", self.minutes, 5), ("secs", self.seconds, 5), ("milliseconds", self.milliseconds, 7))
        ):
            spin = ttk.Spinbox(frame, from_=0, to=99999, textvariable=var, width=width, justify="right", command=self._update_cps)
            spin.grid(row=1, column=idx * 2, sticky="ew", padx=(0, 6))
            spin.bind("<KeyRelease>", lambda _event: self._update_cps())
            ttk.Label(frame, text=label, style="Panel.TLabel").grid(row=1, column=idx * 2 + 1, sticky="w", padx=(0, 18))
        frame.columnconfigure(6, weight=1)
        return frame

    def _section_click(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        ttk.Label(frame, text="Click options", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(frame, text="Mouse button", style="Panel.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Combobox(frame, values=("Left", "Right", "Middle"), textvariable=self.button, width=16, state="readonly").grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Label(frame, text="Click type", style="Panel.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Combobox(frame, values=("Single", "Double", "Triple"), textvariable=self.click_type, width=16, state="readonly").grid(row=2, column=1, sticky="ew", pady=6)
        frame.columnconfigure(1, weight=1)
        return frame

    def _section_repeat(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        ttk.Label(frame, text="Click repeat", style="Section.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        ttk.Radiobutton(frame, text="Repeat", value="count", variable=self.repeat_mode).grid(row=1, column=0, sticky="w", pady=6)
        ttk.Spinbox(frame, from_=1, to=999999, textvariable=self.repeat_count, width=8, justify="right").grid(row=1, column=1, sticky="w", padx=8)
        ttk.Label(frame, text="times", style="Panel.TLabel").grid(row=1, column=2, sticky="w")
        ttk.Radiobutton(frame, text="Repeat until stopped", value="until", variable=self.repeat_mode).grid(row=2, column=0, columnspan=3, sticky="w", pady=6)
        return frame

    def _section_position(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        ttk.Label(frame, text="Cursor position", style="Section.TLabel").grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))
        ttk.Radiobutton(frame, text="Current location", value="current", variable=self.position_mode).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(frame, text="Fixed point", value="fixed", variable=self.position_mode).grid(row=1, column=1, sticky="w", padx=(20, 8))
        ttk.Button(frame, text="Pick location", command=self.pick_location).grid(row=1, column=2, sticky="w", padx=(0, 14))
        ttk.Label(frame, text="X", style="Panel.TLabel").grid(row=1, column=3, sticky="e")
        ttk.Spinbox(frame, from_=-99999, to=99999, textvariable=self.x_pos, width=8, justify="right").grid(row=1, column=4, padx=(6, 12))
        ttk.Label(frame, text="Y", style="Panel.TLabel").grid(row=1, column=5, sticky="e")
        ttk.Spinbox(frame, from_=-99999, to=99999, textvariable=self.y_pos, width=8, justify="right").grid(row=1, column=6, padx=(6, 0))
        frame.columnconfigure(7, weight=1)
        return frame

    def _section_performance(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        ttk.Label(frame, text="Live performance", style="Section.TLabel").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 8))
        for col, var in enumerate((self.clicks, self.actual, self.jitter, self.drift, self.cpu)):
            ttk.Label(frame, textvariable=var, style="Stat.TLabel").grid(row=1, column=col, sticky="w", padx=(0, 24))
        return frame

    def _settings(self) -> ClickSettings:
        interval = (
            max(self.hours.get(), 0) * 3600
            + max(self.minutes.get(), 0) * 60
            + max(self.seconds.get(), 0)
            + max(self.milliseconds.get(), 0) / 1000.0
        )
        if interval <= 0:
            raise ValueError("Set an interval of at least 1 millisecond.")
        multiplier = {"Single": 1, "Double": 2, "Triple": 3}.get(self.click_type.get(), 1)
        repeat = None if self.repeat_mode.get() == "until" else max(self.repeat_count.get(), 1)
        fixed = None
        if self.position_mode.get() == "fixed":
            fixed = (self.x_pos.get(), self.y_pos.get())
        return ClickSettings(interval, self.button.get(), multiplier, repeat, fixed)

    def _update_cps(self) -> None:
        try:
            interval = (
                max(self.hours.get(), 0) * 3600
                + max(self.minutes.get(), 0) * 60
                + max(self.seconds.get(), 0)
                + max(self.milliseconds.get(), 0) / 1000.0
            )
            self.cps.set(f"{1 / interval:.1f} CPS" if interval > 0 else "-- CPS")
        except tk.TclError:
            self.cps.set("-- CPS")

    def start_clicking(self) -> None:
        try:
            settings = self._settings()
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Check settings", str(exc))
            return
        self.engine.start(settings)
        self.status.set("Running")
        self.status_detail.set("Click engine active")
        self._status_dot.itemconfigure(1, fill="#f59e0b")

    def stop_clicking(self) -> None:
        self.engine.stop()
        self.status.set("Stopping")
        self.status_detail.set("Waiting for engine")

    def pick_location(self) -> None:
        self.status_detail.set("Move your cursor. Capturing position in 2 seconds...")
        self.after(2000, self._capture_location)

    def _capture_location(self) -> None:
        try:
            x, y = get_cursor_position()
        except OSError:
            messagebox.showerror("Position", "Could not read cursor position.")
            return
        self.x_pos.set(x)
        self.y_pos.set(y)
        self.position_mode.set("fixed")
        self.status_detail.set(f"Fixed point set to X {x}, Y {y}")

    def _queue_stats(self, stats: EngineStats) -> None:
        self.events.put(("stats", stats))

    def _drain_events(self) -> None:
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "toggle":
                self._toggle_clicking()
            elif isinstance(event, tuple) and event[0] == "stats":
                self._apply_stats(event[1])
        self.after(100, self._drain_events)

    def _toggle_clicking(self) -> None:
        if self.engine.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def _on_f6_key(self, _event) -> str | None:
        if not self.hotkeys.registered:
            self._toggle_clicking()
            return "break"
        return None

    def _apply_stats(self, stats: EngineStats) -> None:
        self.clicks.set(f"{stats.clicks:,} clicks")
        self.actual.set(f"Actual {stats.actual_ms:.2f} ms" if stats.clicks else "Actual -- ms")
        self.jitter.set(f"Jitter {stats.jitter_ms:.2f} ms" if stats.clicks else "Jitter -- ms")
        self.drift.set(f"Drift {stats.drift_ms:.2f} ms" if stats.clicks else "Drift -- ms")
        self.cpu.set(f"CPU {stats.cpu_hint}")
        if stats.running:
            self.status.set("Running")
            self.status_detail.set("F6 stops the clicker")
            self._status_dot.itemconfigure(1, fill="#f59e0b")
        else:
            self.status.set("Ready")
            self.status_detail.set("F6 toggles start/stop")
            self._status_dot.itemconfigure(1, fill="#22c55e")

    def _hotkey_note(self) -> None:
        if self.hotkeys.registered:
            message = "F6 toggles start and stop globally. More editable hotkeys are planned next."
        else:
            message = (
                f"Windows did not register global F6 for this app (error {self.hotkeys.error_code}). "
                "F6 still works while this app window has focus."
            )
        messagebox.showinfo("Hotkeys", message)

    def _macro_note(self) -> None:
        messagebox.showinfo("Record & Playback", "This MVP focuses on the Precision Console. Macro recording is the next build layer.")

    def _on_close(self) -> None:
        self.engine.stop()
        self.hotkeys.stop()
        self.destroy()
