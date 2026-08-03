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


def test_thief_decorners_when_cornered_no_barriers():
    mc = MetaController("thief", make_rng(1), horizon=35, epsilon=0.0)
    assert mc.select(_obs((0, 0)))[0] == "decorner"  # corner cell (degree 2), empty board


def test_thief_escapes_when_not_cornered():
    mc = MetaController("thief", make_rng(1), horizon=35, epsilon=0.0)
    assert mc.select(_obs((3, 3)))[0] == "escape"  # interior cell


def test_decorner_not_selected_when_barriers_present():
    mc = MetaController("thief", make_rng(1), horizon=35, epsilon=0.0)
    # cornered but walls exist -> stay barrier-aware (escape), do not decorner
    assert mc.select(_obs((0, 0), barriers=frozenset({(3, 3)})))[0] == "escape"


def test_decorner_moves_out_of_corner_legally():
    board = Board(7)
    obs = _obs((0, 0))
    act = DecornerBrain(make_rng(1)).decide(obs)
    assert is_legal(act, obs, board, "thief")
    assert act.kind == "MOVE"  # climbs to a higher-degree neighbour rather than sitting
