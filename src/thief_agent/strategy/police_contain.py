"""ContainBrain: belief-interception + value-positive barrier containment Police.

Equal-speed pursuit alone cannot catch an equal-speed evader on open ground, so
this brain wins by *shrinking* the Thief's reachable region. It locates the Thief
from received scent (fresh peak = its exact current cell, since the Police moves
first), captures on contact, and otherwise either (a) places a barrier that
measurably reduces the Thief's reachable component -- but only when close enough
that the cut actually constrains it, never walling empty corners -- or (b) steps to
the cell that most collapses the Thief's escape space (stands in the doorway) while
closing distance. Endgame raises aggression because capture (20) dwarfs survival (5)
for the Police. Deterministic; every action stays legal via the firewall."""

from ..domain.board import Board, Cell
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .fallback import safe_fallback
from .graph import distance_map, reachable_area
from .moves import legal_steps
from .police_barrier import best_barrier
from .variation import micro_variation


def _containment(board: Board, dest: Cell, target: Cell) -> int:
    """Thief reachable area if the Police stands on `dest` (dest treated as a wall)."""
    if dest == target:
        return 0
    trial = Board(board.size, board.barriers | {dest})
    return reachable_area(trial, target)


class ContainBrain(BrainBase):
    def __init__(self, rng, horizon: int = 35, seed: int = 0) -> None:
        super().__init__(rng)
        self.horizon = horizon
        self.seed = seed

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        target = belief.argmax()
        if target is None:
            return safe_fallback(obs, board)
        steps = legal_steps(obs, board)
        # Capture on contact: step onto the believed Thief cell if we can.
        for direction, cell in steps:
            if cell == target and direction != "STAY":
                return Action("MOVE", direction)
        # Value-positive containment barrier: best_barrier is internally gated on a
        # measurable reachable-area reduction (> tempo) and rejects self-obstruction, so
        # it never wastes a barrier on empty space -- the exact G2/G4/G6 failure mode.
        bar = best_barrier(obs, board, target)
        if bar is not None:
            return bar
        # Cornering pursuit: shortest-path closing is primary (robust from any start),
        # with a Chebyshev-axis bias so near-equal closers drive the Thief against a board
        # edge, and a containment term that exploits any nearby chokepoint or existing
        # barrier by collapsing the Thief's escape area. STAY is never a candidate.
        movers = [dc for dc in steps if dc[0] != "STAY"] or steps
        tdist = distance_map(board, target)
        far = board.size * board.size

        def score(dc: tuple[str, Cell]) -> float:
            direction, cell = dc
            axis = max(abs(cell[0] - target[0]), abs(cell[1] - target[1]))
            total = tdist.get(cell, far)
            contain = _containment(board, cell, target)
            # Shortest-path closing is primary (robust from any start); Chebyshev axis
            # and containment only bias among near-equal closers toward edge-cornering.
            value = -10.0 * total - 2.0 * axis - 0.25 * contain
            return value + micro_variation(self.seed, obs.step, cell, direction)

        best = max(movers, key=score)
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "setting up a roadblock ahead"
