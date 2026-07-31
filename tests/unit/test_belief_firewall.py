import dataclasses

from thief_agent.domain.board import Board
from thief_agent.strategy.base import Action, Observation
from thief_agent.strategy.belief import BeliefMap
from thief_agent.strategy.firewall import enforce, is_legal
from thief_agent.strategy.rng import make_rng


def _obs(**kw):
    base = {
        "role": "police",
        "self_pos": (0, 0),
        "board_size": 7,
        "barriers": frozenset(),
        "scent": {},
        "last_hint": "",
        "step": 1,
        "max_barriers": 14,
        "barriers_used": 0,
    }
    base.update(kw)
    return Observation(**base)


def test_belief_normalized_and_zero_on_barriers():
    b = Board(7, {(1, 1)})
    bm = BeliefMap(b)
    bm.update({(3, 3): 0.9})
    assert abs(bm.total() - 1.0) < 1e-9
    assert (1, 1) not in bm.dist
    assert bm.argmax() == (3, 3)


def test_deterministic_rng():
    a = [make_rng(5).random() for _ in range(3)]
    b = [make_rng(5).random() for _ in range(3)]
    assert a == b


def test_firewall_rejects_diagonal_and_substitutes():
    b = Board(7)
    obs = _obs()
    bad = Action("MOVE", "NE")
    assert not is_legal(bad, obs, b, "police")
    legal, sub = enforce(bad, obs, b, "police")
    assert sub and is_legal(legal, obs, b, "police")


def test_observation_has_no_opponent_position():
    fields = {f.name for f in dataclasses.fields(Observation)}
    assert "opponent_pos" not in fields and "thief_pos" not in fields
