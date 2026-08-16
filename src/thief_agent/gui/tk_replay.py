"""The windowed Replay Viewer (rulebook Chapter 7.4): stepper + integrity badge.

Previous/Next walk the reconstructed frames of an audited log. The badge text and colour
come from `ReplayModel.verified`, which is `replay_verify.replay_status` -- a real
per-record SHA-256 recomputation. The window has no way to display VERIFIED OK unless the
verifier actually verified the log."""

import tkinter as tk

from . import palette
from .replay_panel import info_text, trail_fills
from .tk_canvas import GridCanvas

MARK = {"police": ("P", palette.SELF_POLICE), "thief": ("T", palette.SELF_THIEF)}


class ReplayWindow:
    """Board frame viewer with Previous/Next controls and the cryptographic verdict."""

    def __init__(self, master, models, cell_px: int = 56) -> None:
        self.models = list(models)
        self.pos = 0
        master.configure(bg=palette.BG)
        self.master = master
        self.badge = tk.Label(master, font=("DejaVu Sans", 15, "bold"), fg="#ffffff", pady=8)
        self.badge.pack(fill="x", padx=12, pady=(12, 6))
        size = self.models[0].board_size if self.models else 7
        body = tk.Frame(master, bg=palette.BG)
        body.pack(fill="both", expand=True, padx=12)
        self.canvas = GridCanvas(body, size, cell_px)
        self.canvas.pack(side="left")
        self.info = tk.Label(
            body,
            font=("DejaVu Sans", 10),
            bg=palette.PANEL,
            fg=palette.FG,
            justify="left",
            anchor="nw",
            padx=14,
            pady=12,
            width=30,
        )
        self.info.pack(side="left", fill="both", expand=True, padx=(12, 0))
        self._controls(master)
        self.render()

    def _controls(self, master) -> None:
        bar = tk.Frame(master, bg=palette.BG)
        bar.pack(fill="x", padx=12, pady=10)
        self.prev_btn = tk.Button(
            bar, text="◀  Previous", width=14, command=self.on_prev, font=("DejaVu Sans", 10)
        )
        self.prev_btn.pack(side="left")
        self.next_btn = tk.Button(
            bar, text="Next  ▶", width=14, command=self.on_next, font=("DejaVu Sans", 10)
        )
        self.next_btn.pack(side="left", padx=(8, 0))
        self.sub_btn = tk.Button(
            bar, text="Sub-game ↻", width=14, command=self.on_sub, font=("DejaVu Sans", 10)
        )
        self.sub_btn.pack(side="left", padx=(8, 0))
        self.step_lbl = tk.Label(
            bar, font=("DejaVu Sans", 11, "bold"), bg=palette.BG, fg=palette.FG
        )
        self.step_lbl.pack(side="right")

    @property
    def model(self):
        return self.models[self.pos] if self.models else None

    def on_prev(self) -> None:
        if self.model:
            self.model.step_back()
        self.render()

    def on_next(self) -> None:
        if self.model:
            self.model.step_forward()
        self.render()

    def on_sub(self) -> None:
        if self.models:
            self.pos = (self.pos + 1) % len(self.models)
        self.render()

    def render(self) -> None:
        if not self.model:
            self.badge.configure(text="NO REPLAYABLE LOGS", bg=palette.TAMPERED_RED)
            return
        frame = self.model.current()
        bg, fg = palette.integrity_style(frame["verified"])
        self.badge.configure(text=frame["integrity"], bg=bg, fg=fg)
        markers = {}
        for role in ("police", "thief"):
            cell = frame.get(role)
            if cell is not None:
                markers[tuple(cell)] = MARK[role]
        self.canvas.render(fills=trail_fills(frame), markers=markers, barriers=frame["barriers"])
        self.step_lbl.configure(
            text=f"frame {frame['index'] + 1} / {frame['total']}   (step {frame['step']})"
        )
        self.prev_btn.configure(state="normal" if frame["has_prev"] else "disabled")
        self.next_btn.configure(state="normal" if frame["has_next"] else "disabled")
        self.info.configure(text=info_text(frame, len(self.models)))


def show(models, title: str, hold_ms: int = 0):
    """Open the replay window over loaded models; caller runs the Tk main loop."""
    root = tk.Tk()
    root.title(title)
    ReplayWindow(root, models)
    root.update_idletasks()
    if hold_ms:
        root.after(hold_ms, root.destroy)
    return root
