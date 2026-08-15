"""Locate the pursuing Cop from the data the protocol legally puts on the wire.

The Thief never receives a Cop coordinate, but two public channels pin it down:

* SCENT. The Cop broadcasts its whole decaying field every turn. One turn of that
  field is ``tau <- decay * min(cap, tau_prev + K(d))`` for the agreed 5x5 kernel K,
  so given the PREVIOUS broadcast we can predict the next one for every hypothetical
  Cop cell and keep the hypothesis with the smallest error. Maximum likelihood beats
  a raw argmax (which saturates: many cells sit pinned at the cap) and beats a plain
  delta peak (which collapses when the Cop stands still on an already-saturated cell).

* BARRIERS. Rule 15 makes every wall public, and the Barrier Law puts it on the
  Cop's own cell or one orthogonally adjacent -- so a freshly declared barrier
  confines the Cop to at most five cells. That is an exact geometric constraint, and
  it is intersected with the scent estimate whenever a wall appears.

Motion is bounded too: a Cop moves at most one orthogonal step per turn (and none at
all on a barrier turn), so the hypothesis set is grown by one ring each turn and then
re-filtered. Everything here is derived from received public messages only.
"""

from ..domain.board import Board, Cell
from ..domain.smell import KERNEL, MAX_INTENSITY

SEPARATION = 0.12  # scent-error slack below which two Cop hypotheses are not separable


def _predict(prev: dict, centre: Cell, size: int, rho: float) -> dict:
    """The field a Cop standing on `centre` would broadcast next, given `prev`."""
    out = dict(prev)
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            cell = (centre[0] + dr, centre[1] + dc)
            if 0 <= cell[0] < size and 0 <= cell[1] < size:
                out[cell] = min(MAX_INTENSITY, prev.get(cell, 0.0) + KERNEL[(abs(dr), abs(dc))])
    return {c: v * (1.0 - rho) for c, v in out.items()}


def _error(pred: dict, actual: dict) -> float:
    return sum(abs(pred.get(c, 0.0) - actual.get(c, 0.0)) for c in set(pred) | set(actual))


class CopLocator:
    """Maximum-likelihood tracker for a scent-emitting agent.

    ``barrier_law`` applies the Rule-15/Barrier-Law constraint and must be used ONLY
    for a Cop: a Thief declares no walls, so a new barrier is evidence about the
    opponent, not about the agent being tracked. ``start=None`` begins with a
    board-wide prior, which is what to use when no start term may be assumed.
    """

    def __init__(
        self, size: int, start: Cell | None, rho: float = 0.1, barrier_law: bool = True
    ) -> None:
        self.size = size
        self.rho = rho
        self.barrier_law = barrier_law
        if start is None:
            self.candidates = {(r, c) for r in range(size) for c in range(size)}
            self.best: Cell = (0, 0)
        else:
            self.candidates = {tuple(start)}
            self.best = tuple(start)
        self._prev_scent: dict = {}
        self._prev_barriers: frozenset = frozenset()

    def _grow(self, board: Board) -> set[Cell]:
        """One turn of Cop motion: stay put, or step to a passable orthogonal neighbour."""
        out: set[Cell] = set()
        for c in self.candidates:
            out.add(c)
            out.update(board.neighbors(c))
        return out or {self.best}

    def update(self, scent: dict, barriers: frozenset, board: Board) -> set[Cell]:
        """Fold one received message into the estimate; returns the plausible Cop cells."""
        new_walls = set(barriers) - set(self._prev_barriers)
        pool = self._grow(board)

        if new_walls and self.barrier_law:  # the wall sits on the Cop's cell or beside it
            allowed: set[Cell] = set()
            for wall in new_walls:
                allowed.add(wall)
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nb = (wall[0] + dr, wall[1] + dc)
                    if board.in_bounds(nb):
                        allowed.add(nb)
            pool = (pool & allowed) or allowed

        # A barrier cell is NOT evidence of absence: the Barrier Law lets the Cop wall
        # the cell it is standing on (target SELF), so it can legally occupy a wall of
        # its own making. Filtering those out loses the true cell outright.
        if scent:
            scored = [
                (_error(_predict(self._prev_scent, c, self.size, self.rho), scent), c)
                for c in sorted(pool)
            ]
            floor = min(s for s, _ in scored)
            # Keep every hypothesis the evidence cannot separate from the best. The
            # slack matters: the opponent's emitter need not be bit-identical to the
            # agreed kernel, and a locator that collapses to one cell is CONFIDENTLY
            # wrong ~19% of the time -- which, for a hard safety constraint, is worse
            # than carrying two or three cells and treating them all as dangerous.
            pool = {c for s, c in scored if s <= floor + SEPARATION}
            self.best = min((s, c) for s, c in scored if c in pool)[1]
        elif pool:
            self.best = min(pool)

        self.candidates = pool
        self._prev_scent = dict(scent)
        self._prev_barriers = frozenset(barriers)
        return set(pool)

    @property
    def certain(self) -> bool:
        return len(self.candidates) == 1
