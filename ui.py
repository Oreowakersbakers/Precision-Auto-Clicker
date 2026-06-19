import queue
import time
import tkinter as tk
from tkinter import messagebox, ttk

from click_engine import ClickEngine
from hotkeys import DEFAULT_HOTKEY, HotkeyListener, HotkeySpec, hotkey_from_keysym
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
        self._last_size: tuple[int, int] | None = None
        self._panel_item: int | None = None
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.content = tk.Frame(self.canvas, bg=fill, highlightthickness=0, bd=0)
        self._window = self.canvas.create_window(self._pad[0], self._pad[1], window=self.content, anchor="nw")
        self.bind("<Configure>", self._resize)

    def _resize(self, _event=None) -> None:
        width = max(self.winfo_width(), 1)
        height = max(self.winfo_height(), 1)
        left, top, right, bottom = self._pad
        if self._last_size != (width, height):
            self._last_size = (width, height)
            if self._panel_item is not None:
                self.canvas.delete(self._panel_item)
            self._panel_item = self._rounded_rect(
                1,
                1,
                width - 2,
                height - 2,
                self._radius,
                fill=self._fill,
                outline=self._outline,
                tags="panel",
            )
            self.canvas.tag_lower(self._panel_item)
        self.canvas.coords(self._window, left, top)
        self.canvas.itemconfigure(self._window, width=max(width - left - right, 1), height=max(height - top - bottom, 1))

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs) -> int:
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
        return self.canvas.create_polygon(points, smooth=True, splinesteps=16, **kwargs)


class PrecisionConsole(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Precision Auto Clicker")
        self.geometry("720x440")
        self.minsize(700, 440)
        self.configure(bg="#f3f5f8")

        self.events: queue.Queue[str] = queue.Queue()
        self.engine = ClickEngine(self._queue_stats)
        self.hotkey = DEFAULT_HOTKEY
        self.hotkeys = HotkeyListener(lambda: self.events.put("toggle"), self.hotkey)
        self._focused_hotkey_sequence = ""

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
        self.status_detail = tk.StringVar(value="")
        self.hotkey_title = tk.StringVar(value="")
        self.hotkey_display = tk.StringVar(value="")
        self.start_button_text = tk.StringVar(value="")
        self.stop_button_text = tk.StringVar(value="")
        self.cps = tk.StringVar(value="10.0 CPS")
        self.interval_summary = tk.StringVar(value="Total: 100 milliseconds (0.100 s)")
        self.clicks = tk.StringVar(value="0 clicks")
        self.actual = tk.StringVar(value="Actual -- ms")
        self.jitter = tk.StringVar(value="Jitter -- ms")
        self.cpu = tk.StringVar(value="CPU idle")
        self.uptime = tk.StringVar(value="Uptime 00:00:00")
        self._started_at: float | None = None
        self._rendered_running: bool | None = None

        self._build_styles()
        self._refresh_hotkey_labels("toggle")
        self._build_ui()
        self.after(100, self._drain_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._bind_focused_hotkey()
        if not self.hotkeys.start():
            self.status_detail.set(self._global_hotkey_unavailable_message())

    def _build_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 9), background="#f3f5f8")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Soft.TFrame", background="#f3f5f8")
        style.configure("Muted.TLabel", background="#f3f5f8", foreground="#5f6775")
        style.configure("Panel.TLabel", background="#ffffff", foreground="#1f2937")
        style.configure("Section.TLabel", font=("Segoe UI Semibold", 10), background="#ffffff", foreground="#111827")
        style.configure("Help.TLabel", background="#ffffff", foreground="#4b5563")
        style.configure("Stat.TLabel", background="#ffffff", foreground="#4b5563")
        style.configure("StrongStat.TLabel", font=("Segoe UI Semibold", 9), background="#ffffff", foreground="#111827")
        style.configure("Primary.TButton", font=("Segoe UI Semibold", 11), padding=(18, 11))
        style.configure("Danger.TButton", font=("Segoe UI Semibold", 11), padding=(18, 11))
        style.map("Primary.TButton", background=[("active", "#075bbd"), ("pressed", "#064f9f")])
        style.configure("Primary.TButton", background="#0969da", foreground="#ffffff", bordercolor="#0969da")
        style.configure("Danger.TButton", background="#ffffff", foreground="#1f2937", bordercolor="#cfd6df")
        style.configure("TButton", padding=(9, 5), background="#ffffff", bordercolor="#d8dde6")
        style.configure("TSpinbox", arrowsize=12, padding=(6, 4))
        style.configure("TRadiobutton", background="#ffffff")
        style.configure("Segment.TButton", padding=(10, 5), background="#ffffff", bordercolor="#bfc7d2")
        style.configure(
            "SelectedSegment.TButton",
            font=("Segoe UI Semibold", 9),
            padding=(10, 5),
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
        outer = ttk.Frame(self, style="Soft.TFrame", padding=10)
        outer.pack(fill="both", expand=True)

        metrics_panel = RoundedPanel(outer, bg="#f3f5f8", padding=(12, 8, 12, 8))
        metrics_panel.pack(side="bottom", fill="x", pady=(8, 0))
        metrics_panel.configure(height=36)
        metrics_panel.pack_propagate(False)
        metrics = metrics_panel.content
        for col, var in enumerate((self.jitter, self.cps, self.cpu, self.uptime, self.clicks)):
            metrics.columnconfigure(col, weight=1, uniform="metrics")
            ttk.Label(metrics, textvariable=var, style="Stat.TLabel").grid(row=0, column=col, sticky="w", padx=(0, 10))

        actions = ttk.Frame(outer, style="Soft.TFrame")
        actions.pack(side="bottom", fill="x", pady=(8, 0))
        self.start_button = ttk.Button(actions, textvariable=self.start_button_text, style="Primary.TButton", command=self.start_clicking)
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.stop_button = ttk.Button(actions, textvariable=self.stop_button_text, style="Danger.TButton", command=self.stop_clicking)
        self.stop_button.pack(side="left", fill="x", expand=True)

        main_panel = RoundedPanel(outer, bg="#f3f5f8", padding=12)
        main_panel.pack(side="top", fill="both", expand=True)
        main = main_panel.content
        main.columnconfigure(0, weight=1, uniform="main")
        main.columnconfigure(1, weight=1, uniform="main")

        self._section_interval(main).grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        self._section_repeat(main).grid(row=0, column=1, sticky="nsew", pady=(0, 12))
        self._section_click(main).grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 12))
        self._section_position(main).grid(row=1, column=1, sticky="nsew", pady=(0, 12))
        self._section_planned(main).grid(row=2, column=0, columnspan=2, sticky="ew")

    def _section_header(self, parent, number: str, title: str) -> None:
        parent.columnconfigure(7, weight=1)
        header = tk.Frame(parent, bg="#ffffff", highlightthickness=0, bd=0)
        header.grid(row=0, column=0, columnspan=8, sticky="ew", pady=(0, 7))
        header.columnconfigure(2, weight=1)
        badge = tk.Canvas(
            header,
            width=24,
            height=24,
            bg="#ffffff",
            highlightthickness=0,
            bd=0,
        )
        badge.create_oval(2, 2, 22, 22, outline="#0969da", width=1.4, fill="#ffffff")
        badge.create_text(12, 12, text=number, fill="#075bbd", font=("Segoe UI Semibold", 8))
        badge.grid(row=0, column=0, sticky="w")
        ttk.Label(header, text=title, style="Section.TLabel").grid(row=0, column=1, sticky="w", padx=(8, 10))
        line = tk.Frame(header, bg="#dce2ea", height=1, highlightthickness=0, bd=0)
        line.grid(row=0, column=2, sticky="ew", pady=(2, 0))

    def _segmented(self, parent, row: int, variable: tk.StringVar, values: tuple[str, ...]) -> None:
        holder = ttk.Frame(parent, style="Panel.TFrame")
        holder.grid(row=row, column=1, sticky="ew", pady=3)
        for idx, value in enumerate(values):
            holder.columnconfigure(idx, weight=1, uniform=f"seg{row}")
            button = ttk.Button(
                holder,
                text=value,
                style="Segment.TButton",
                command=lambda selected=value: self._select_segment(variable, selected),
            )
            button.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 3, 0))
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
        self._section_header(frame, "1", "Interval")
        for idx, (label, var, width) in enumerate(
            (("hours", self.hours, 5), ("mins", self.minutes, 5), ("secs", self.seconds, 5), ("milliseconds", self.milliseconds, 7))
        ):
            spin = ttk.Spinbox(frame, from_=0, to=99999, textvariable=var, width=width, justify="right", command=self._update_cps)
            spin.grid(row=1, column=idx, sticky="ew", padx=(0, 8))
            spin.bind("<KeyRelease>", lambda _event: self._update_cps())
            ttk.Label(frame, text=label.title(), style="Panel.TLabel").grid(row=2, column=idx, sticky="w", pady=(3, 0))
            frame.columnconfigure(idx, weight=1, uniform="interval")
        return frame

    def _section_click(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        self._section_header(frame, "2", "Click")
        ttk.Label(frame, text="Button", style="Panel.TLabel").grid(row=1, column=0, sticky="w", pady=3, padx=(0, 10))
        self._segmented(frame, 1, self.button, ("Left", "Right", "Middle"))
        ttk.Label(frame, text="Type", style="Panel.TLabel").grid(row=2, column=0, sticky="w", pady=3, padx=(0, 10))
        self._segmented(frame, 2, self.click_type, ("Single", "Double", "Triple"))
        frame.columnconfigure(1, weight=1)
        return frame

    def _section_repeat(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        self._section_header(frame, "3", "Repeat")
        ttk.Radiobutton(frame, text="Repeat until stopped", value="until", variable=self.repeat_mode).grid(row=1, column=0, columnspan=3, sticky="w", pady=6)
        ttk.Radiobutton(frame, text="Repeat exact count", value="count", variable=self.repeat_mode).grid(row=2, column=0, sticky="w", pady=6)
        ttk.Spinbox(frame, from_=1, to=999999, textvariable=self.repeat_count, width=8, justify="right").grid(row=2, column=1, sticky="w", padx=8)
        ttk.Label(frame, text="times", style="Panel.TLabel").grid(row=2, column=2, sticky="w")
        return frame

    def _section_position(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        self._section_header(frame, "4", "Position")
        ttk.Radiobutton(frame, text="Current cursor location", value="current", variable=self.position_mode).grid(row=1, column=0, columnspan=4, sticky="w", pady=(2, 8))
        ttk.Radiobutton(frame, text="Fixed location", value="fixed", variable=self.position_mode).grid(row=2, column=0, columnspan=4, sticky="w", pady=(2, 8))
        ttk.Button(frame, text="Pick location", command=self.pick_location).grid(row=3, column=0, sticky="w", padx=(22, 14))
        ttk.Label(frame, text="X", style="Panel.TLabel").grid(row=3, column=1, sticky="e")
        ttk.Spinbox(frame, from_=-99999, to=99999, textvariable=self.x_pos, width=8, justify="right").grid(row=3, column=2, padx=(6, 12))
        ttk.Label(frame, text="Y", style="Panel.TLabel").grid(row=3, column=3, sticky="e")
        ttk.Spinbox(frame, from_=-99999, to=99999, textvariable=self.y_pos, width=8, justify="right").grid(row=3, column=4, padx=(6, 0))
        frame.columnconfigure(4, weight=1)
        return frame

    def _section_planned(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame")
        frame.columnconfigure(1, weight=1)
        hotkeys = ttk.Frame(frame, style="Panel.TFrame")
        hotkeys.grid(row=0, column=0, columnspan=3, sticky="ew")
        ttk.Label(hotkeys, text="Hotkey", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(hotkeys, textvariable=self.hotkey_display, style="StrongStat.TLabel").grid(row=0, column=1, sticky="w", padx=(12, 10))
        ttk.Button(hotkeys, text="Change...", command=self._hotkey_note).grid(row=0, column=2, sticky="w", padx=(0, 14))
        ttk.Label(hotkeys, textvariable=self.status_detail, style="Help.TLabel").grid(row=0, column=3, sticky="ew")
        hotkeys.columnconfigure(3, weight=1)
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
        latest_stats: EngineStats | None = None
        while True:
            try:
                event = self.events.get_nowait()
            except queue.Empty:
                break
            if isinstance(event, tuple) and event[0] == "stats":
                latest_stats = event[1]
                continue
            if latest_stats is not None:
                self._apply_stats(latest_stats)
                latest_stats = None
            if event == "toggle":
                self._toggle_clicking()
        if latest_stats is not None:
            self._apply_stats(latest_stats)
        self.after(100, self._drain_events)

    def _toggle_clicking(self) -> None:
        if self.engine.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def _on_hotkey_key(self, _event) -> str | None:
        if not self.hotkeys.registered:
            self._toggle_clicking()
            return "break"
        return None

    def _apply_stats(self, stats: EngineStats) -> None:
        self.clicks.set(f"{stats.clicks:,} clicks")
        self.actual.set(f"Actual {stats.actual_ms:.2f} ms" if stats.clicks else "Actual -- ms")
        self.jitter.set(f"Jitter {stats.jitter_ms:.2f} ms" if stats.clicks else "Jitter -- ms")
        self.cpu.set(f"CPU {stats.cpu_hint}")
        if stats.running != self._rendered_running:
            self._rendered_running = stats.running
            if stats.running:
                self.status.set("Running")
                self.status_summary.set("Clicking active")
                self._refresh_hotkey_labels("stop")
            else:
                self.status.set("Ready")
                self.status_summary.set("Clicking inactive")
                self._refresh_hotkey_labels("toggle")

        if stats.running:
            if self._started_at is not None:
                self.uptime.set(f"Uptime {self._format_uptime(time.perf_counter() - self._started_at)}")
        else:
            self._started_at = None
            self.uptime.set("Uptime 00:00:00")

    def _format_uptime(self, seconds: float) -> str:
        total_seconds = max(int(seconds), 0)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _hotkey_note(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Change Hotkey")
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.configure(bg="#ffffff")
        dialog.grab_set()
        dialog.columnconfigure(0, weight=1)
        ttk.Label(dialog, text="Press a new start / stop hotkey", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 6)
        )
        ttk.Label(dialog, text="Supported: A-Z, 0-9, F1-F12. Escape cancels.", style="Help.TLabel").grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 14)
        )
        preview = tk.StringVar(value=f"Current: {self.hotkey.display}")
        ttk.Label(dialog, textvariable=preview, style="StrongStat.TLabel").grid(row=2, column=0, sticky="w", padx=18, pady=(0, 18))

        def cancel(_event=None) -> str:
            dialog.destroy()
            return "break"

        def capture(event) -> str:
            if event.keysym == "Escape":
                return cancel()
            spec = hotkey_from_keysym(event.keysym)
            if spec is None:
                preview.set("Use A-Z, 0-9, or F1-F12")
                return "break"
            dialog.destroy()
            self._set_hotkey(spec)
            return "break"

        dialog.bind("<KeyPress>", capture)
        dialog.bind("<Escape>", cancel)
        dialog.after(50, dialog.focus_force)

    def _set_hotkey(self, hotkey: HotkeySpec) -> None:
        if hotkey == self.hotkey:
            self._refresh_hotkey_labels("stop" if self.engine.running else "toggle")
            return
        self.hotkeys.stop()
        self._unbind_focused_hotkey()
        self.hotkey = hotkey
        self.hotkeys = HotkeyListener(lambda: self.events.put("toggle"), self.hotkey)
        self._bind_focused_hotkey()
        registered = self.hotkeys.start()
        self._refresh_hotkey_labels("stop" if self.engine.running else "toggle")
        if not registered:
            self.status_detail.set(self._global_hotkey_unavailable_message())
            messagebox.showwarning(
                "Hotkeys",
                f"Windows did not register global {self.hotkey.display} for this app (error {self.hotkeys.error_code}). "
                f"{self.hotkey.display} still works while this app window has focus.",
            )

    def _refresh_hotkey_labels(self, mode: str) -> None:
        display = self.hotkey.display
        self.hotkey_title.set(f"Hotkey: {display}")
        self.hotkey_display.set(display)
        self.start_button_text.set(f"Start ({display})")
        self.stop_button_text.set(f"Stop ({display})")
        if mode == "stop":
            self.status_detail.set(f"{display} stops the clicker")
        else:
            self.status_detail.set(f"{display} toggles start/stop")

    def _bind_focused_hotkey(self) -> None:
        self._focused_hotkey_sequence = self.hotkey.tk_sequence
        self.bind_all(self._focused_hotkey_sequence, self._on_hotkey_key)

    def _unbind_focused_hotkey(self) -> None:
        if self._focused_hotkey_sequence:
            self.unbind_all(self._focused_hotkey_sequence)
            self._focused_hotkey_sequence = ""

    def _global_hotkey_unavailable_message(self) -> str:
        return f"Global {self.hotkey.display} unavailable ({self.hotkeys.error_code}); app-focused {self.hotkey.display} still works"

    def _on_close(self) -> None:
        self.engine.stop()
        self.hotkeys.stop()
        self.destroy()
