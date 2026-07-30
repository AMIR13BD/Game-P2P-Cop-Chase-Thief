"""Discrete N x N board geometry with barriers. Orthogonal neighbors only."""

from ..constants import DELTAS, ORTHO

Cell = tuple[int, int]


class Board:
    def __init__(self, size: int, barriers: set[Cell] | None = None) -> None:
        self.size = size
        self.barriers: set[Cell] = set(barriers or ())

    def in_bounds(self, cell: Cell) -> bool:
        r, c = cell
        return 0 <= r < self.size and 0 <= c < self.size

    def passable(self, cell: Cell) -> bool:
        return self.in_bounds(cell) and cell not in self.barriers

    def neighbors(self, cell: Cell) -> list[Cell]:
        out: list[Cell] = []
        for d in ORTHO:
            dr, dc = DELTAS[d]
            nxt = (cell[0] + dr, cell[1] + dc)
            if self.passable(nxt):
                out.append(nxt)
        return out

    def add_barrier(self, cell: Cell) -> None:
        self.barriers.add(cell)

    def all_cells(self) -> list[Cell]:
        return [(r, c) for r in range(self.size) for c in range(self.size)]
