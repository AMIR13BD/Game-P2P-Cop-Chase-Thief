"""AntiSqueezeBrain: a Thief that optimises SURVIVAL TOPOLOGY, not raw distance.

Measured failure of the distance-first evader against the Orcai-MJ Cop: every loss
was barrier-driven -- their Rule-46 pounce (a wall dropped on our cell from an
adjacent Cop) or Rule-47 enclosure -- and never a chase. Maximising Manhattan
distance walks into the board edge, where a shrinking component and a one-wall seal
do the rest. So distance becomes a hard constraint, and the objective becomes the
shape of the space we keep.

Hard constraints, in order (each tier applies only while a legal move survives it):
  0. never step onto a cell the Cop may occupy;
  1. never end within one step of any plausible Cop cell -- exactly the pounce range,
     since a barrier turn does not move the Cop and it may wall its own cell or any
     of the four beside it;
  2. never accept a cell whose component ONE further wall could collapse.

Objective over the survivors: worst-case reachable area after the Cop's best single
wall (the anti-squeeze term), current area with the Cop blocked, safe exits,
vertex-disjoint routes to the frontier, open degree, corner clearance while the Cop
still holds walls, and anti-loop history -- which also denies their stall detector
the repeated position pair that unlocks their squeeze. Distance is a tie-break only.

The Cop cell comes from ``CopLocator`` (public scent + the public Barrier Law).
Correcting the objective is what makes that signal safe to use: fed to a distance-first
policy, a sharper Cop estimate merely sharpens the flight into the corner.
Deterministic under a fixed seed; every action still clears the firewall.
"""

from collections import Counter, deque

from ..domain.board import Board, Cell
from .base import Action, BrainBase, Observation
from .connectivity import articulation_points
from .cop_locate import CopLocator
from .disjoint import edge_cells, vertex_disjoint_paths
from .graph import distance_map, reachable_area
from .moves import legal_steps
from .variation import micro_variation

DIST_CAP = 8

DEFAULT_WEIGHTS = {
    "seal": 4.0,  # worst-case area after the Cop's best single wall (primary)
    "area": 1.0,  # area right now, Cop treated as blocked
    "exits": 6.0,  # neighbours that are themselves out of pounce range
    "routes": 3.0,  # vertex-disjoint escape routes to the frontier
    "degree": 2.0,  # open neighbours
    "artic": 8.0,  # penalty: standing on a cut vertex
    "corner": 3.0,  # penalty: corner proximity while walls remain
    "dist": 2.0,  # mild tie-break only -- never the objective
    "revisit": 4.0,
    "recent": 10.0,
    "stay": 6.0,
}


def _cop_wall_targets(board: Board, cops: set[Cell]) -> set[Cell]:
    """Every cell the Cop could legally wall next turn (its own cell or one beside it)."""
    out: set[Cell] = set()
    for c in cops:
        if board.in_bounds(c) and c not in board.barriers:
            out.add(c)
        for n in board.neighbors(c):
            out.add(n)
    return out


class AntiSqueezeBrain(BrainBase):
    def __init__(self, rng, horizon: int = 35, weights: dict | None = None, seed: int = 0,
                 cop_start: Cell = (0, 0)) -> None:
        super().__init__(rng)
        self.horizon = horizon
        self.seed = seed
        self.w = dict(DEFAULT_WEIGHTS)
        if weights:
            self.w.update(weights)
        self._start = tuple(cop_start)
        self.locator: CopLocator | None = None
        self._recent: deque[Cell] = deque(maxlen=6)
        self._visits: Counter[Cell] = Counter()

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        if self.locator is None:
            self.locator = CopLocator(obs.board_size, self._start)
        cops = self.locator.update(dict(obs.scent), frozenset(obs.barriers), board)
        self._recent.append(obs.self_pos)
        self._visits[obs.self_pos] += 1

        far = board.size * board.size
        dmaps = [distance_map(board, c) for c in cops]

        def cop_dist(cell: Cell) -> int:
            return min((dm.get(cell, far) for dm in dmaps), default=far)

        walls = _cop_wall_targets(board, cops)

        def worst_area(cell: Cell) -> int:
            """Reachable area after the single wall that hurts us most."""
            worst = far
            for wall in walls:
                if wall == cell:
                    continue  # a wall ON us is the pounce, excluded by tier 1
                trial = Board(board.size, board.barriers | {wall} | set(cops))
                worst = min(worst, reachable_area(trial, cell))
            return worst if worst != far else reachable_area(board, cell)

        steps = legal_steps(obs, board)
        pool = [dc for dc in steps if dc[1] not in cops] or steps
        safe = [dc for dc in pool if cop_dist(dc[1]) >= 2] or pool
        # Tier 2: refuse a cell one wall could collapse, while a roomier one remains.
        roomy = [dc for dc in safe if worst_area(dc[1]) >= 4]
        safe = roomy or safe

        edges = edge_cells(board)
        cut = articulation_points(board)
        recent = set(self._recent)
        n = board.size

        # NO endgame branch, deliberately: the earlier evader switched near the threshold
        # to a score without the corner/STAY penalties, parked in a corner and was walled
        # in (R47) -- the only losses left once the pounce was closed.
        walls_left = len(board.barriers) < obs.max_barriers

        def score(dc: tuple[str, Cell]) -> float:
            direction, cell = dc
            cd = min(cop_dist(cell), DIST_CAP)
            degree = len(board.neighbors(cell))
            seal = worst_area(cell)
            corner = max(0, 2 - min(cell[0], cell[1], n - 1 - cell[0], n - 1 - cell[1]))
            exits = sum(cop_dist(x) >= 2 for x in board.neighbors(cell))
            w = self.w
            value = (
                w["seal"] * seal
                + w["area"] * reachable_area(Board(n, board.barriers | set(cops)), cell)
                + w["exits"] * exits
                + w["routes"] * vertex_disjoint_paths(board, cell, edges)
                + w["degree"] * degree
                + w["dist"] * cd
                - w["artic"] * (cell in cut)
                - w["corner"] * corner * walls_left
                - w["revisit"] * self._visits[cell]
                - w["recent"] * (cell in recent)
                - w["stay"] * (direction == "STAY")
            )
            return value + micro_variation(self.seed, obs.step, cell, direction)

        best = max(safe, key=score)
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "keeping to the crowded main roads"
