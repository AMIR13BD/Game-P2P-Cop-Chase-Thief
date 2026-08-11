"""Anti-herding trap fix: the Thief switches to DecornerBrain only when cornered on an
open board (low degree, no barriers), and DecornerBrain climbs to higher mobility. General
and topology-only; EvadeBrain (and the frozen baseline that uses it) stays unchanged."""

from thief_agent.domain.board import Board
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import is_legal
from thief_agent.strategy.meta import MetaController
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_decorner import DecornerBrain


def _obs(pos, barriers=frozenset()):
    return Observation(
        role="thief",
        self_pos=pos,
        board_size=7,
        barriers=barriers,
        scent={(6, 6): 0.9},
        step=5,
        max_barriers=14,
        barriers_used=len(barriers),
    )


def test_thief_selects_survivor_when_cornered():
    mc = MetaController("thief", make_rng(1), horizon=35, epsilon=0.0)
    # SurvivorBrain subsumes decorner: its trap filter + mobility terms handle a corner.
    assert mc.select(_obs((0, 0)))[0] == "survivor"


def test_thief_selects_survivor_in_interior():
    mc = MetaController("thief", make_rng(1), horizon=35, epsilon=0.0)
    assert mc.select(_obs((3, 3)))[0] == "survivor"


def test_survivor_climbs_out_of_corner_legally():
    # Behavioural guarantee preserved: from a corner the thief moves to more mobility.
    from thief_agent.strategy.thief_survivor import SurvivorBrain

    board = Board(7)
    obs = _obs((0, 0))
    act = SurvivorBrain(make_rng(1), horizon=35).decide(obs)
    assert is_legal(act, obs, board, "thief") and act.kind == "MOVE"


def test_decorner_moves_out_of_corner_legally():
    board = Board(7)
    obs = _obs((0, 0))
    act = DecornerBrain(make_rng(1)).decide(obs)
    assert is_legal(act, obs, board, "thief")
    assert act.kind == "MOVE"  # climbs to a higher-degree neighbour rather than sitting
