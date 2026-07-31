"""EscapeBrain: preserve distance from the inferred pursuer while maximising future
mobility and keeping multiple escape routes open. Uses only received scent to locate
the threat (never a hidden position). Deterministic tie-breaking."""

from ..domain.board import Board
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .disjoint import edge_cells, vertex_disjoint_paths
from .graph import distance_map, reachable_area
from .moves import legal_steps


def _action(step) -> Action:
    return Action("STAY") if step[0] == "STAY" else Action("MOVE", step[0])


class EscapeBrain(BrainBase):
    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        belief = BeliefMap(board)
        belief.update(obs.scent)
        threat = belief.argmax()
        steps = legal_steps(obs, board)
        if threat is None:  # no signal: head for the most open space
            return _action(max(steps, key=lambda dc: reachable_area(board, dc[1])))
        dist = distance_map(board, threat)
        edges = edge_cells(board)

        def score(dc):
            cell = dc[1]
            routes = vertex_disjoint_paths(board, cell, edges)
            return (dist.get(cell, -1), len(board.neighbors(cell)), routes)

        return _action(max(steps, key=score))

    def hint(self, obs: Observation) -> str:
        return "keeping to the crowded main roads"
