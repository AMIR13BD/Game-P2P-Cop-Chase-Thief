"""Stigmergic scent: 5x5 radial emission (centre 0.9) with per-turn decay (0.10)."""

from .board import Board, Cell

Grid = dict[Cell, float]


def emit(grid: Grid, centre: Cell, board: Board, intensity: float, side: int) -> None:
    """Add a radial field around `centre` into `grid` (accumulate, capped at intensity)."""
    k = side // 2
    for dr in range(-k, k + 1):
        for dc in range(-k, k + 1):
            cell = (centre[0] + dr, centre[1] + dc)
            if not board.in_bounds(cell):
                continue
            cheb = max(abs(dr), abs(dc))
            val = intensity * (1.0 - cheb / (k + 1))
            if val <= 0:
                continue
            grid[cell] = min(intensity, max(grid.get(cell, 0.0), val))


def decay(grid: Grid, rho: float) -> Grid:
    """Shrink every cell to (1-rho) of its value; drop negligible traces."""
    out: Grid = {}
    for cell, val in grid.items():
        nv = max(0.0, (1.0 - rho) * val)
        if nv > 1e-6:
            out[cell] = nv
    return out
