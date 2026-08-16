"""The one Tk drawing primitive shared by the live GUI and the replay viewer.

Kept deliberately dumb: it renders whatever cell colours and markers it is handed. All
decisions about what a cell means live in the pure view-models (`live_model`,
`replay_model`) and in `palette`, so this file needs no test of its own beyond being
importable -- and a headless CI never has to construct it."""

import tkinter as tk

from . import palette


class GridCanvas(tk.Canvas):
    """A square board canvas with per-cell fill colours, markers and barrier hatching."""

    def __init__(self, master, size: int, cell_px: int = 56, **kwargs) -> None:
        self.size = size
        self.cell_px = cell_px
        side = size * cell_px + 1
        super().__init__(
            master,
            width=side,
            height=side,
            bg=palette.BG,
            highlightthickness=0,
            **kwargs,
        )

    def _bbox(self, row: int, col: int) -> tuple[int, int, int, int]:
        x0 = col * self.cell_px
        y0 = row * self.cell_px
        return x0, y0, x0 + self.cell_px, y0 + self.cell_px

    def render(self, fills=None, markers=None, barriers=(), labels=None, buckets=None) -> None:
        """Repaint the whole board. `markers` maps cell -> (text, colour)."""
        self.delete("all")
        fills = fills or {}
        markers = markers or {}
        labels = labels or {}
        self._buckets = buckets or {}
        barrier_set = {tuple(b) for b in barriers}
        for row in range(self.size):
            for col in range(self.size):
                self._cell(row, col, fills, markers, labels, barrier_set)

    def _cell(self, row, col, fills, markers, labels, barrier_set) -> None:
        cell = (row, col)
        x0, y0, x1, y1 = self._bbox(row, col)
        fill = palette.BARRIER if cell in barrier_set else fills.get(cell, palette.HEAT_RAMP[0])
        self.create_rectangle(x0, y0, x1, y1, fill=fill, outline=palette.GRID_LINE)
        if cell in barrier_set:
            self.create_line(x0, y0, x1, y1, fill=palette.BG, width=2)
            self.create_line(x0, y1, x1, y0, fill=palette.BG, width=2)
            return
        label = labels.get(cell)
        if label:
            self.create_text(
                x1 - 6,
                y1 - 5,
                text=label,
                fill=palette.label_color(getattr(self, "_buckets", {}).get(cell, 0)),
                font=("DejaVu Sans", 8, "bold"),
                anchor="se",
            )
        marker = markers.get(cell)
        if marker:
            self._marker(x0, y0, x1, y1, marker)

    def _marker(self, x0, y0, x1, y1, marker) -> None:
        text, colour = marker
        pad = self.cell_px * 0.18
        self.create_oval(x0 + pad, y0 + pad, x1 - pad, y1 - pad, fill=colour, outline=palette.BG)
        self.create_text(
            (x0 + x1) / 2,
            (y0 + y1) / 2,
            text=text,
            fill="#10141a",
            font=("DejaVu Sans", max(9, self.cell_px // 4), "bold"),
        )


def heat_fills(buckets) -> dict:
    """Cell -> colour for a {cell: 0-9} belief bucket map."""
    return {tuple(cell): palette.heat_color(value) for cell, value in (buckets or {}).items()}


def bucket_labels(buckets, minimum: int = 1) -> dict:
    """Small numeric bucket labels, drawn only where there is belief mass worth reading."""
    return {
        tuple(cell): str(value)
        for cell, value in (buckets or {}).items()
        if isinstance(value, int) and value >= minimum
    }
