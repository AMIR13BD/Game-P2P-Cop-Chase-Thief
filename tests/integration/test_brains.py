from thief_agent.domain.board import Board
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import is_legal
from thief_agent.strategy.police_greedy import PoliceGreedyBrain
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_distance import ThiefDistanceBrain

ORTHO = {"N", "S", "E", "W"}


def _obs(role, pos, scent):
    return Observation(
        role=role,
        self_pos=pos,
        board_size=7,
        barriers=frozenset(),
        scent=scent,
        last_hint="",
        step=1,
        max_barriers=14,
        barriers_used=0,
    )


def test_police_greedy_legal_and_orthogonal():
    obs = _obs("police", (0, 0), {(3, 3): 0.9})
    act = PoliceGreedyBrain(make_rng(1)).decide(obs)
    assert is_legal(act, obs, Board(7), "police")
    assert act.kind in ("MOVE", "STAY", "BARRIER")
    if act.kind == "MOVE":
        assert act.direction in ORTHO


def test_thief_distance_moves_away():
    # police believed at (0,0); thief at (3,3) should not move toward it
    obs = _obs("thief", (3, 3), {(0, 0): 0.9})
    act = ThiefDistanceBrain(make_rng(1)).decide(obs)
    assert is_legal(act, obs, Board(7), "thief")
    if act.kind == "MOVE":
        assert act.direction in {"S", "E"}  # increases Manhattan distance from (0,0)
