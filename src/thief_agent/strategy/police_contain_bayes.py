"""ContainBayesBrain: ContainBrain's pursuit UNCHANGED, with a Bayesian belief-state filter
as its Thief-localisation front-end.

The bottleneck against strong distance/perimeter evaders is not the chase but LOCALISATION:
the additive received scent saturates (many cells pinned at the 0.9 cap), so a raw argmax /
delta peak mislocates the Thief and the Police chases a ghost. This filter maintains a
histogram belief over the Thief's cell and updates it each turn from (a) a MOTION model (the
Thief moves to one legal orthogonal neighbour or stays; barriers respected) and (b) a
kernel-shaped SCENT likelihood (the Thief's current cell just deposited the agreed 5x5 centre,
its neighbours ~0.62). The MAP estimate replaces ContainBrain's ``_locate`` output; every other
line of ContainBrain (capture-on-contact, value-gated barriers, cornering) is inherited verbatim.

Legality/info: the filter reads ONLY ``obs.scent`` (the received ``smell_grid``) and the public
board barriers — never a true Thief coordinate, opponent internals, or future information. It
models the agreed GAME PHYSICS (unit motion + pheromone kernel), not any opponent's strategy, so
it generalises to unknown Thieves. Deterministic and fast (a 49-cell histogram); firewall-legal."""

from ..domain.board import Board, Cell
from .police_contain import ContainBrain

_NB = ((-1, 0), (1, 0), (0, -1), (0, 1))


class ThiefBeliefFilter:
    """Histogram (Bayes) filter over the Thief's current cell. Uses only received scent +
    the public board; never the true position."""

    FRESH = 0.20  # a scent jump above this = a fresh centre deposit (a directed mover)

    def __init__(self, size: int, start: Cell | None = None) -> None:
        self.size = size
        cells = [(r, c) for r in range(size) for c in range(size)]
        if start is not None:
            self.b: dict[Cell, float] = {c: (1.0 if c == start else 0.0) for c in cells}
        else:
            p = 1.0 / len(cells)
            self.b = dict.fromkeys(cells, p)
        self._prev: dict[Cell, float] = {}

    def _neigh(self, c: Cell, bar: frozenset) -> list[Cell]:
        out = []
        for dr, dc in _NB:
            n = (c[0] + dr, c[1] + dc)
            if 0 <= n[0] < self.size and 0 <= n[1] < self.size and n not in bar:
                out.append(n)
        return out

    def step(self, scent: dict[Cell, float], bar: frozenset) -> Cell:
        # PREDICT: the Thief moved to one legal neighbour or stayed (uniform transition).
        pred = dict.fromkeys(self.b, 0.0)
        for c, p in self.b.items():
            if p <= 0.0:
                continue
            dests = [c] + self._neigh(c, bar)
            w = p / len(dests)
            for d in dests:
                pred[d] = pred.get(d, 0.0) + w
        # UPDATE: kernel-shaped scent likelihood — the Thief's cell is high AND its ring is warm.
        post: dict[Cell, float] = {}
        total = 0.0
        for c in pred:
            if c in bar:
                continue
            s = scent.get(c, 0.0)
            ring = [scent.get(n, 0.0) for n in self._neigh(c, bar)]
            lik = (0.05 + s) * (0.3 + (sum(ring) / len(ring) if ring else 0.0))
            post[c] = pred[c] * lik
            total += post[c]
        self.b = {c: v / total for c, v in post.items()} if total > 0.0 else pred
        map_cell = max(self.b, key=self.b.get)
        # HYBRID: a clear FRESH-emission peak (a directed mover — perimeter runner, fresh trail)
        # is tracked directly; only when the scent has SATURATED (no fresh peak — the
        # distance/escape/evade evaders) do we fall back to the diffuse Bayes MAP.
        best, best_delta = None, 0.0
        for c, v in scent.items():
            if c in bar:
                continue
            d = v - 0.9 * self._prev.get(c, 0.0)
            if d > best_delta:
                best_delta, best = d, c
        self._prev = dict(scent)
        return best if (best is not None and best_delta > self.FRESH) else map_cell


class ContainBayesBrain(ContainBrain):
    """ContainBrain with the Bayesian belief filter as its localisation front-end."""

    def __init__(self, rng, horizon: int = 35, seed: int = 0, thief_start: Cell = (3, 3)) -> None:
        super().__init__(rng, horizon=horizon, seed=seed)
        self._start = tuple(thief_start)
        self._filter: ThiefBeliefFilter | None = None

    def _locate(self, board: Board, scent: dict) -> Cell | None:
        if self._filter is None:  # seed at the agreed thief_start (a public, signed term)
            self._filter = ThiefBeliefFilter(board.size, start=self._start)
        return self._filter.step(dict(scent), frozenset(board.barriers))
