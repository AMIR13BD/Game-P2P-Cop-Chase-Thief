"""DecornerBrain: a mobility-first evade used only when the Thief is cornered on an open
board. It mirrors EvadeBrain's safety terms (avoid seal risk, stay in the largest
component, avoid articulation cells) but ranks legal-neighbour count (future mobility)
ABOVE raw distance, so it walks OUT of a low-degree corner instead of fleeing deeper into
it. This defeats an equal-speed herder that pins a pure distance-maximiser in a corner.

General and topology-only: it never inspects the opponent's identity or a fixed position."""

from ..domain.board import Board, Cell
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .connectivity import articulation_points
from .graph import distance_map, largest_component, reachable_area
from .moves import legal_steps


def _seal_risk(board: Board, cell: Cell) -> int:
    return 1 if len(board.neighbors(cell)) <= 1 else 0


class DecornerBrain(BrainBase):
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
                -_seal_risk(board, cell),
                1 if cell in big else 0,
                0 if cell in cut else 1,
                len(board.neighbors(cell)),  # mobility first: climb out of the corner
                dist.get(cell, 0),
                reachable_area(board, cell),
            )

        best = max(legal_steps(obs, board), key=score)
        return Action("STAY") if best[0] == "STAY" else Action("MOVE", best[0])

    def hint(self, obs: Observation) -> str:
        return "heading back toward the open blocks"
