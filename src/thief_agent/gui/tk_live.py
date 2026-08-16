"""The windowed Live GUI (rulebook Chapter 7.3): belief heatmap + turn indicator.

Thin Tk assembly over `live_model.live_state`. The window owns no game logic at all: it is
handed a finished view-model and paints it, which is why the perspective is always correct
for whichever role produced the Observation."""

import tkinter as tk

from . import palette
from .live_model import legend_rows, live_state
from .tk_canvas import GridCanvas, bucket_labels, heat_fills

MARK = {"police": "P", "thief": "T"}


class LiveWindow:
    """Board + belief heatmap + green YOUR TURN / grey LOCKED banner for one agent."""

    def __init__(self, master, role: str, board_size: int, cell_px: int = 56) -> None:
        self.role = role
        master.configure(bg=palette.BG)
        self.banner = tk.Label(master, font=("DejaVu Sans", 15, "bold"), fg="#ffffff", pady=8)
        self.banner.pack(fill="x", padx=12, pady=(12, 6))
        body = tk.Frame(master, bg=palette.BG)
        body.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        self.canvas = GridCanvas(body, board_size, cell_px)
        self.canvas.pack(side="left")
        self.side = tk.Frame(body, bg=palette.PANEL)
        self.side.pack(side="left", fill="both", expand=True, padx=(12, 0))
        self._rows: list[tuple[tk.Label, tk.Label]] = []
        self.caption = tk.Label(
            master,
            font=("DejaVu Sans", 9),
            bg=palette.BG,
            fg=palette.MUTED,
            justify="left",
            anchor="w",
        )
        self.caption.pack(fill="x", padx=12, pady=(0, 10))
        self._legend(board_size)

    def _legend(self, board_size: int) -> None:
        tk.Label(
            self.side,
            text="BELIEF HEATMAP",
            font=("DejaVu Sans", 11, "bold"),
            bg=palette.PANEL,
            fg=palette.FG,
        ).pack(anchor="w", padx=12, pady=(12, 2))
        strip = tk.Canvas(self.side, width=200, height=18, bg=palette.PANEL, highlightthickness=0)
        for bucket in range(10):
            strip.create_rectangle(
                bucket * 20, 0, bucket * 20 + 20, 18, fill=palette.heat_color(bucket), outline=""
            )
        strip.pack(anchor="w", padx=12)
        tk.Label(
            self.side,
            text="cold  0 -> 9  peak",
            font=("DejaVu Sans", 8),
            bg=palette.PANEL,
            fg=palette.MUTED,
        ).pack(anchor="w", padx=12, pady=(1, 8))
        for _ in range(7):
            row = tk.Frame(self.side, bg=palette.PANEL)
            row.pack(fill="x", padx=12, pady=1)
            key = tk.Label(
                row, font=("DejaVu Sans", 9), bg=palette.PANEL, fg=palette.MUTED, anchor="w"
            )
            key.pack(side="left")
            val = tk.Label(
                row, font=("DejaVu Sans", 9, "bold"), bg=palette.PANEL, fg=palette.FG, anchor="e"
            )
            val.pack(side="right")
            self._rows.append((key, val))

    def render(self, state: dict) -> None:
        """Paint one live frame from a `live_model.live_state` dict."""
        text, colour = palette.banner_style(state["locked"])
        self.banner.configure(text=f"{text}   |   {state['status']}", bg=colour)
        marker = (MARK.get(state["role"], "?"), palette.self_color(state["role"]))
        self.canvas.render(
            fills=heat_fills(state["buckets"]),
            markers={state["self_pos"]: marker},
            barriers=state["barriers"],
            labels=bucket_labels(state["buckets"]),
            buckets=state["buckets"],
        )
        for (key, val), (label, value) in zip(self._rows, legend_rows(state), strict=False):
            key.configure(text=label)
            val.configure(text=value)
        self.caption.configure(
            text=(
                f"Shaded cells are P(opponent = cell) for the {state['opponent'].upper()}, from "
                f"received scent only.\nThe opponent's true cell is never drawn - "
                f"{MARK.get(state['role'], '?')} marks this agent."
            )
        )


def show(role: str, board_size: int, state: dict, title: str, hold_ms: int = 0):
    """Open the live window, paint `state`, and return the Tk root (caller runs the loop)."""
    root = tk.Tk()
    root.title(title)
    window = LiveWindow(root, role, board_size)
    window.render(state)
    root.update_idletasks()
    if hold_ms:
        root.after(hold_ms, root.destroy)
    return root


def render_state(obs, protocol_state: str = "MOVE", connected: bool = True) -> dict:
    """Convenience: Observation -> renderable state (same call the CLI uses)."""
    return live_state(obs, state=protocol_state, connected=connected)
