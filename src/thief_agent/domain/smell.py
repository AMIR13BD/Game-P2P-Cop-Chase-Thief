"""Stigmergic scent: the fixed 5x5 radial kernel from the PDF, edge-clipped, with
the documented update tau_next = max(0, (1-rho)*tau_old + delta) capped at 0.9."""

from .board import Board, Cell

Grid = dict[Cell, float]
MAX_INTENSITY = 0.9

# value keyed by (|row_offset|, |col_offset|) from the emitter (exact PDF matrix)
KERNEL: dict[tuple[int, int], float] = {
    (0, 0): 0.90,
    (0, 1): 0.62,
    (1, 0): 0.62,
    (1, 1): 0.42,
    (0, 2): 0.20,
    (2, 0): 0.20,
    (1, 2): 0.14,
    (2, 1): 0.14,
    (2, 2): 0.04,
}


def emission_delta(centre: Cell, board: Board) -> Grid:
    """The 5x5 kernel deposited around `centre`, clipped to in-bounds cells only."""
    delta: Grid = {}
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            cell = (centre[0] + dr, centre[1] + dc)
            if board.in_bounds(cell):
                delta[cell] = KERNEL[(abs(dr), abs(dc))]
    return delta


def decay(grid: Grid, rho: float) -> Grid:
    """Pure decay: multiply every cell by (1-rho); drop negligible traces."""
    out: Grid = {}
    for cell, val in grid.items():
        nv = max(0.0, (1.0 - rho) * val)
        if nv > 1e-9:
            out[cell] = nv
    return out


def step_update(grid: Grid, centre: Cell, board: Board, rho: float) -> Grid:
    """One turn: tau_next = min(0.9, max(0, (1-rho)*tau_old + delta)) over all cells."""
    delta = emission_delta(centre, board)
    out: Grid = {}
    for cell in set(grid) | set(delta):
        nv = max(0.0, (1.0 - rho) * grid.get(cell, 0.0) + delta.get(cell, 0.0))
        nv = min(MAX_INTENSITY, nv)
        if nv > 1e-9:
            out[cell] = nv
    return out
