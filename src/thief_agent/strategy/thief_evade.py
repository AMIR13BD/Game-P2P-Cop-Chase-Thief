"""EvadeBrain: avoid self-trapping geometry -- corners, articulation cells, small
components -- and cells the Police could seal next turn (barrier-threat forecast).
Complements EscapeBrain, which focuses on raw distance and mobility."""

from ..domain.board import Board, Cell
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .connectivity import articulation_points
from .graph import distance_map, largest_component, reachable_area
from .moves import legal_steps


def seal_risk(board: Board, cell: Cell) -> int:
    """1 if the cell has <=1 escape (one Police barrier could trap it), else 0."""
    return 1 if len(board.neighbors(cell)) <= 1 else 0


class EvadeBrain(BrainBase):
    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        threat = belief.argmax()
        cut = articulation_points(board)
        big = largest_component(board)
        dist = distance_map(board, threat) if threat is not None else {}

        def score(dc):
            cell = dc[1]
            return (
                -seal_risk(board, cell),
                1 if cell in big else 0,
                0 if cell in cut else 1,
                dist.get(cell, 0),
                reachable_area(board, cell),
            )

        best = max(legal_steps(obs, board), key=score)
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "avoiding the narrow alleys tonight"
