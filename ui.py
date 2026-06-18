import queue
import time
import tkinter as tk
from tkinter import messagebox, ttk

from click_engine import ClickEngine
from hotkeys import HotkeyListener
from models import ClickSettings, EngineStats
from win32_input import get_cursor_position


class RoundedPanel(tk.Frame):
    def __init__(
        self,
        parent,
        *,
        bg: str,
        fill: str = "#ffffff",
        outline: str = "#dde3ea",
        radius: int = 10,
        padding: int | tuple[int, int, int, int] = 12,
    ) -> None:
        super().__init__(parent, bg=bg, highlightthickness=0, bd=0)
        if isinstance(padding, int):
            self._pad = (padding, padding, padding, padding)
        else:
            self._pad = padding
        self._fill = fill
        self._outline = outline
        self._radius = radius
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.content = tk.Frame(self.canvas, bg=fill, highlightthickness=0, bd=0)
        self._window = self.canvas.create_window(self._pad[0], self._pad[1], window=self.content, anchor="nw")
        self.bind("<Configure>", self._resize)

    def _resize(self, _event=None) -> None:
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)
        left, top, right, bottom = self._pad
        self.canvas.delete("panel")
        self._rounded_rect(1, 1, width - 2, height - 2, self._radius, fill=self._fill, outline=self._outline, tags="panel")
        self.canvas.tag_lower("panel")
        self.canvas.coords(self._window, left, top)
        self.canvas.itemconfigure(self._window, width=max(width - left - right, 1), height=max(height - top - bottom, 1))

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs) -> None:
        points = (
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        )
        self.canvas.create_polygon(points, smooth=True, splinesteps=16, **kwargs)


class PrecisionConsole(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Precision Auto Clicker")
        self.geometry("900x720")
        self.minsize(860, 720)
        self.configure(bg="#f3f5f8")

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
        self.status_summary = tk.StringVar(value="Clicking inactive")
        self.status_detail = tk.StringVar(value="F6 toggles start/stop")
        self.cps = tk.StringVar(value="10.0 CPS")
        self.interval_summary = tk.StringVar(value="Total: 100 milliseconds (0.100 s)")
        self.clicks = tk.StringVar(value="0 clicks")
        self.actual = tk.StringVar(value="Actual -- ms")
        self.jitter = tk.StringVar(value="Jitter -- ms")
        self.drift = tk.StringVar(value="Drift -- ms")
        self.cpu = tk.StringVar(value="CPU idle")
        self.uptime = tk.StringVar(value="Uptime 00:00:00")
        self._started_at: float | None = None

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
        style.configure(".", font=("Segoe UI", 10), background="#f3f5f8")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Soft.TFrame", background="#f3f5f8")
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 17), background="#f3f5f8", foreground="#171a1f")
        style.configure("Muted.TLabel", background="#f3f5f8", foreground="#5f6775")
        style.configure("Panel.TLabel", background="#ffffff", foreground="#1f2937")
        style.configure("Section.TLabel", font=("Segoe UI Semibold", 12), background="#ffffff", foreground="#111827")
        style.configure("Help.TLabel", background="#ffffff", foreground="#4b5563")
        style.configure("Stat.TLabel", background="#ffffff", foreground="#4b5563")
        style.configure("StrongStat.TLabel", font=("Segoe UI Semibold", 10), background="#ffffff", foreground="#111827")
        style.configure("Primary.TButton", font=("Segoe UI Semibold", 12), padding=(22, 14))
        style.configure("Danger.TButton", font=("Segoe UI Semibold", 12), padding=(22, 14))
        style.map("Primary.TButton", background=[("active", "#075bbd"), ("pressed", "#064f9f")])
        style.configure("Primary.TButton", background="#0969da", foreground="#ffffff", bordercolor="#0969da")
        style.configure("Danger.TButton", background="#ffffff", foreground="#1f2937", bordercolor="#cfd6df")
        style.configure("TButton", padding=(12, 8), background="#ffffff", bordercolor="#d8dde6")
        style.configure("TSpinbox", arrowsize=13, padding=(7, 5))
        style.configure("TRadiobutton", background="#ffffff")
        style.configure("Segment.TButton", padding=(18, 8), background="#ffffff", bordercolor="#bfc7d2")
        style.configure(
            "SelectedSegment.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(18, 8),
            background="#eef5ff",
            foreground="#075bbd",
            bordercolor="#0969da",
        )
        style.map(
            "Segment.TButton",
            background=[("active", "#eef5ff"), ("pressed", "#ddeaff")],
            foreground=[("active", "#075bbd")],
        )

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, style="Soft.TFrame", padding=14)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="Soft.TFrame")
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text="Precision Auto Clicker", style="Title.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.status_detail, style="Muted.TLabel").pack(side="right", pady=(8, 0))

        status_panel = RoundedPanel(outer, bg="#f3f5f8", padding=(14, 10, 14, 10))
        status_panel.pack(fill="x", pady=(0, 12))
        status_panel.configure(height=64)
        status_panel.pack_propagate(False)
        status_bar = status_panel.content
        for col in range(4):
            status_bar.columnconfigure(col, weight=1, uniform="status")
        self._status_cell(status_bar, 0, self.status, self.status_summary, dot=True)
        self._status_cell(status_bar, 1, "Hotkey: F6", "Toggle Start / Stop")
        self._status_cell(status_bar, 2, "Profile: Default", "No macros loaded")
        self._status_cell(status_bar, 3, self.cps, self.interval_summary)

        metrics_panel = RoundedPanel(outer, bg="#f3f5f8", padding=(14, 10, 14, 10))
        metrics_panel.pack(side="bottom", fill="x", pady=(10, 0))
        metrics_panel.configure(height=42)
        metrics_panel.pack_propagate(False)
        metrics = metrics_panel.content
        for col, var in enumerate((self.jitter, self.drift, self.cpu, self.uptime, self.clicks)):
            metrics.columnconfigure(col, weight=1, uniform="metrics")
            ttk.Label(metrics, textvariable=var, style="Stat.TLabel").grid(row=0, column=col, sticky="w", padx=(0, 14))

        actions = ttk.Frame(outer, style="Soft.TFrame")
        actions.pack(side="bottom", fill="x", pady=(10, 0))
        self.start_button = ttk.Button(actions, text="Start (F6)", style="Primary.TButton", command=self.start_clicking)
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.stop_button = ttk.Button(actions, text="Stop (F6)", style="Danger.TButton", command=self.stop_clicking)
        self.stop_button.pack(side="left", fill="x", expand=True)

        main_panel = RoundedPanel(outer, bg="#f3f5f8", padding=14)
        main_panel.pack(side="top", fill="both", expand=True)
        main = main_panel.content
        main.columnconfigure(0, weight=1, uniform="main")
        main.columnconfigure(1, weight=1, uniform="main")

        self._section_interval(main).grid(row=0, column=0, sticky="nsew", padx=(0, 18), pady=(0, 16))
        self._section_repeat(main).grid(row=0, column=1, sticky="nsew", pady=(0, 16))
        self._section_click(main).grid(row=1, column=0, sticky="nsew", padx=(0, 18), pady=(0, 16))
        self._section_position(main).grid(row=1, column=1, sticky="nsew", pady=(0, 16))
        self._section_planned(main).grid(row=2, column=0, columnspan=2, sticky="ew")

    def _status_cell(self, parent, column: int, title: str | tk.StringVar, subtitle: str | tk.StringVar, dot: bool = False) -> None:
        cell = ttk.Frame(parent, style="Panel.TFrame")
        cell.grid(row=0, column=column, sticky="ew", padx=(0, 18 if column < 3 else 0))
        if dot:
            self._status_dot = tk.Canvas(cell, width=12, height=12, highlightthickness=0, bg="#ffffff")
            self._status_dot.create_oval(2, 2, 10, 10, fill="#22c55e", outline="")
            self._status_dot.grid(row=0, column=0, rowspan=2, sticky="n", padx=(0, 10), pady=(3, 0))
        text_col = 1 if dot else 0
        if isinstance(title, tk.StringVar):
            ttk.Label(cell, textvariable=title, style="StrongStat.TLabel").grid(row=0, column=text_col, sticky="w")
        else:
            ttk.Label(cell, text=title, style="StrongStat.TLabel").grid(row=0, column=text_col, sticky="w")
        if isinstance(subtitle, tk.StringVar):
            ttk.Label(cell, textvariable=subtitle, style="Stat.TLabel").grid(row=1, column=text_col, sticky="w")
        else:
            ttk.Label(cell, text=subtitle, style="Stat.TLabel").grid(row=1, column=text_col, sticky="w")

    def _section_header(self, parent, number: str, title: str, helper: str) -> None:
        badge = tk.Canvas(
            parent,
            width=24,
            height=24,
            bg="#ffffff",
            highlightthickness=0,
            bd=0,
        )
        badge.create_oval(2, 2, 22, 22, outline="#0969da", width=1.4, fill="#ffffff")
        badge.create_text(12, 12, text=number, fill="#075bbd", font=("Segoe UI Semibold", 9))
        badge.grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Label(parent, text=title, style="Section.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 10), pady=(0, 6))
        line = tk.Frame(parent, bg="#dce2ea", height=1, highlightthickness=0, bd=0)
        line.grid(row=0, column=2, columnspan=2, sticky="ew", pady=(2, 6))
        parent.columnconfigure(2, weight=1)
        ttk.Label(parent, text=helper, style="Help.TLabel").grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 10))

    def _segmented(self, parent, row: int, variable: tk.StringVar, values: tuple[str, ...]) -> None:
        holder = ttk.Frame(parent, style="Panel.TFrame")
        holder.grid(row=row, column=1, sticky="ew", pady=6)
        for idx, value in enumerate(values):
            holder.columnconfigure(idx, weight=1, uniform=f"seg{row}")
            button = ttk.Button(
                holder,
                text=value,
                style="Segment.TButton",
                command=lambda selected=value: self._select_segment(variable, selected),
            )
            button.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 4, 0))
            self._paint_segment(button, variable.get() == value)
            variable.trace_add("write", lambda *_args, b=button, v=variable, option=value: self._paint_segment(b, v.get() == option))

    def _select_segment(self, variable: tk.StringVar, value: str) -> None:
        variable.set(value)

    def _paint_segment(self, button: ttk.Button, selected: bool) -> None:
        if selected:
            button.configure(style="SelectedSegment.TButton")
        else:
            button.configure(style="Segment.TButton")

    def _section_interval(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        self._section_header(frame, "1", "Interval", "Set the time between clicks")
        for idx, (label, var, width) in enumerate(
            (("hours", self.hours, 5), ("mins", self.minutes, 5), ("secs", self.seconds, 5), ("milliseconds", self.milliseconds, 7))
        ):
            spin = ttk.Spinbox(frame, from_=0, to=99999, textvariable=var, width=width, justify="right", command=self._update_cps)
            spin.grid(row=2, column=idx, sticky="ew", padx=(0, 8))
            spin.bind("<KeyRelease>", lambda _event: self._update_cps())
            ttk.Label(frame, text=label.title(), style="Panel.TLabel").grid(row=3, column=idx, sticky="w", pady=(3, 0))
            frame.columnconfigure(idx, weight=1, uniform="interval")
        ttk.Label(frame, textvariable=self.interval_summary, style="Stat.TLabel").grid(row=4, column=0, columnspan=4, sticky="w", pady=(8, 0))
        return frame

    def _section_click(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        self._section_header(frame, "2", "Click", "Select mouse button and click type")
        ttk.Label(frame, text="Button", style="Panel.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        self._segmented(frame, 2, self.button, ("Left", "Right", "Middle"))
        ttk.Label(frame, text="Click type", style="Panel.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        self._segmented(frame, 3, self.click_type, ("Single", "Double", "Triple"))
        frame.columnconfigure(1, weight=1)
        return frame

    def _section_repeat(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        self._section_header(frame, "3", "Repeat", "Choose how the clicking repeats")
        ttk.Radiobutton(frame, text="Repeat until stopped", value="until", variable=self.repeat_mode).grid(row=2, column=0, columnspan=3, sticky="w", pady=6)
        ttk.Radiobutton(frame, text="Repeat exact count", value="count", variable=self.repeat_mode).grid(row=3, column=0, sticky="w", pady=6)
        ttk.Spinbox(frame, from_=1, to=999999, textvariable=self.repeat_count, width=8, justify="right").grid(row=3, column=1, sticky="w", padx=8)
        ttk.Label(frame, text="times", style="Panel.TLabel").grid(row=3, column=2, sticky="w")
        return frame

    def _section_position(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        self._section_header(frame, "4", "Position", "Select where clicks occur")
        ttk.Radiobutton(frame, text="Current cursor location", value="current", variable=self.position_mode).grid(row=2, column=0, columnspan=4, sticky="w", pady=(2, 8))
        ttk.Radiobutton(frame, text="Fixed location", value="fixed", variable=self.position_mode).grid(row=3, column=0, columnspan=4, sticky="w", pady=(2, 8))
        ttk.Button(frame, text="Pick location", command=self.pick_location).grid(row=4, column=0, sticky="w", padx=(22, 14))
        ttk.Label(frame, text="X", style="Panel.TLabel").grid(row=4, column=1, sticky="e")
        ttk.Spinbox(frame, from_=-99999, to=99999, textvariable=self.x_pos, width=8, justify="right").grid(row=4, column=2, padx=(6, 12))
        ttk.Label(frame, text="Y", style="Panel.TLabel").grid(row=4, column=3, sticky="e")
        ttk.Spinbox(frame, from_=-99999, to=99999, textvariable=self.y_pos, width=8, justify="right").grid(row=4, column=4, padx=(6, 0))
        frame.columnconfigure(4, weight=1)
        return frame

    def _section_planned(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.columnconfigure(0, weight=1, uniform="planned")
        frame.columnconfigure(1, weight=1, uniform="planned")
        hotkeys = ttk.Frame(frame, style="Panel.TFrame")
        hotkeys.grid(row=0, column=0, sticky="ew", padx=(0, 18))
        ttk.Label(hotkeys, text="Hotkey Settings", style="Section.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        ttk.Label(hotkeys, text="Customize start / stop hotkey", style="Help.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(hotkeys, text="F6", style="StrongStat.TLabel").grid(row=1, column=1, sticky="ew", padx=14)
        ttk.Button(hotkeys, text="Change...", command=self._hotkey_note).grid(row=1, column=2, sticky="e")
        hotkeys.columnconfigure(1, weight=1)

        macros = ttk.Frame(frame, style="Panel.TFrame")
        macros.grid(row=0, column=1, sticky="ew")
        ttk.Label(macros, text="Record & Playback", style="Section.TLabel").grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        ttk.Label(macros, text="Planned macro tools", style="Help.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Button(macros, text="Record", command=self._macro_note).grid(row=1, column=1, sticky="e", padx=(14, 8))
        ttk.Button(macros, text="Playback", command=self._macro_note).grid(row=1, column=2, sticky="e")
        macros.columnconfigure(0, weight=1)
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
            total_ms = interval * 1000
            if total_ms >= 1000:
                readable = f"{interval:.3f} seconds"
            else:
                readable = f"{total_ms:.0f} milliseconds"
            self.interval_summary.set(f"Total: {readable} ({interval:.3f} s)" if interval > 0 else "Total: --")
        except tk.TclError:
            self.cps.set("-- CPS")
            self.interval_summary.set("Total: --")

    def start_clicking(self) -> None:
        try:
            settings = self._settings()
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Check settings", str(exc))
            return
        self.engine.start(settings)
        self.status.set("Running")
        self.status_summary.set("Clicking active")
        self.status_detail.set("Click engine active")
        self._started_at = time.perf_counter()
        self._status_dot.itemconfigure(1, fill="#f59e0b")

    def stop_clicking(self) -> None:
        self.engine.stop()
        self.status.set("Stopping")
        self.status_summary.set("Stop requested")
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
            self.status_summary.set("Clicking active")
            self.status_detail.set("F6 stops the clicker")
            if self._started_at is not None:
                self.uptime.set(f"Uptime {self._format_uptime(time.perf_counter() - self._started_at)}")
            self._status_dot.itemconfigure(1, fill="#f59e0b")
        else:
            self.status.set("Ready")
            self.status_summary.set("Clicking inactive")
            self.status_detail.set("F6 toggles start/stop")
            self._started_at = None
            self.uptime.set("Uptime 00:00:00")
            self._status_dot.itemconfigure(1, fill="#22c55e")

    def _format_uptime(self, seconds: float) -> str:
        total_seconds = max(int(seconds), 0)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

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
