"""Faithful local model of the Orcai-MJ public Thief policy and the belief it acts on.

Reimplemented from their published source (identical tree in orcai-mj-thief and
orcai-mj-cop): ``strategy/heuristic.py::RingRunnerThief`` and ``domain/belief.py``.
Two properties make that policy PREDICTABLE rather than merely guessable:

* The ring term outweighs distance. It scores each legal neighbour with
  ``d(cell, hunter) - 3*|ring(cell) - 1|`` where ``ring = min(r, c, N-1-r, N-1-c)``.
  Two neighbours of one cell differ in Manhattan distance by at most 2, so a ring-1
  move always beats a ring-0 or ring-2 move. Once the Thief reaches the loop one
  cell inside the border it can NEVER leave while any ring-1 neighbour is passable
  -- a 16-cell cycle on the agreed 7x7 board.
* The "hunter" cell it scores against is its own BELIEF argmax, and that belief is
  driven by the scent WE emit and the barriers WE declare. Both are ours, so their
  belief is reproducible on our side exactly.

Legality: nothing here reads a true opponent coordinate, opponent internals or any
future information. The model is seeded from the SIGNED ``thief_start`` term and
rolled forward from our own outbound messages, exactly as a human analyst could do
with the opponent's public repository. Deterministic and allocation-light.
"""

import math

from ..constants import DELTAS, ORTHO
from ..domain.board import Board, Cell

# Their published coefficients (heuristic.py). Named so a change in their repo is a
# one-line change here rather than a rewrite.
RING_WEIGHT = 3
DISTANCE_WEIGHT = 1
PREFERRED_RING = 1
SMELL_TRUST = 4.0  # their game.toml [belief] smell_trust_weight, both roles


def ring_of(cell: Cell, size: int) -> int:
    """Their ring index: distance to the nearest board edge."""
    return min(cell[0], cell[1], size - 1 - cell[0], size - 1 - cell[1])


def ring_cells(size: int, ring: int = PREFERRED_RING) -> set[Cell]:
    """Every cell on a given ring -- the Thief's attractor loop for ring 1."""
    return {(r, c) for r in range(size) for c in range(size) if ring_of((r, c), size) == ring}


def ringrunner_next(pos: Cell, hunter: Cell, board: Board) -> Cell:
    """The cell their RingRunnerThief moves to from `pos` believing the cop is at `hunter`.

    Mirrors their loop exactly: iterate N, S, E, W over passable neighbours, keep the
    first strict maximum (so ties fall to the earliest direction), and HOLD in place
    when walled in. They never play STAY voluntarily.
    """
    best: Cell | None = None
    best_score: int | None = None
    for d in ORTHO:
        dr, dc = DELTAS[d]
        cell = (pos[0] + dr, pos[1] + dc)
        if not board.passable(cell):
            continue
        dist = abs(cell[0] - hunter[0]) + abs(cell[1] - hunter[1])
        score = DISTANCE_WEIGHT * dist - RING_WEIGHT * abs(
            ring_of(cell, board.size) - PREFERRED_RING
        )
        if best_score is None or score > best_score:
            best, best_score = cell, score
    return best if best is not None else pos


class OrcaiBelief:
    """Replica of their ``BeliefGrid``: the distribution THEY hold over OUR cell.

    Reproduced operation for operation (uniform prior, 5-cell diffusion that respects
    barriers, exponential scent fusion, argmax scanned row-major with a strict '>' so
    ties resolve to the lowest (row, col)).
    """

    def __init__(self, size: int, trust: float = SMELL_TRUST) -> None:
        self.size = size
        self.trust = trust
        n = size * size
        self.grid = [[1.0 / n for _ in range(size)] for _ in range(size)]

    def most_likely(self) -> Cell:
        best, best_p = (0, 0), -1.0
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] > best_p:
                    best, best_p = (r, c), self.grid[r][c]
        return best

    def diffuse(self, barriers) -> None:
        blocked = set(barriers or ())
        new = [[0.0] * self.size for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                p = self.grid[r][c]
                if p <= 0:
                    continue
                cells = [] if (r, c) in blocked else [(r, c)]
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size and (nr, nc) not in blocked:
                        cells.append((nr, nc))
                if not cells:
                    continue
                share = p / len(cells)
                for nr, nc in cells:
                    new[nr][nc] += share
        self.grid = new
        self._normalize()

    def fuse(self, scent: dict) -> None:
        """Their ``update_from_smell``: posterior proportional to prior * exp(trust*intensity)."""
        for (r, c), intensity in scent.items():
            if 0 <= r < self.size and 0 <= c < self.size:
                self.grid[r][c] *= math.exp(self.trust * intensity)
        self._normalize()

    def _normalize(self) -> None:
        total = sum(sum(row) for row in self.grid)
        if total > 0:
            self.grid = [[v / total for v in row] for row in self.grid]
