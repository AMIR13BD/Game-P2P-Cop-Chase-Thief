"""P16 meta-controller: deterministic under seed, always legal (firewall enforced),
records strategy + reason, controlled exploration, and role-appropriate selection."""

from thief_agent.domain.board import Board
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import enforce
from thief_agent.strategy.meta import MetaController
from thief_agent.strategy.rng import make_rng


def _obs(role, **kw):
    base = {
        "role": role,
        "self_pos": (3, 3),
        "board_size": 7,
        "barriers": frozenset(),
        "scent": {(0, 0): 0.9},
        "step": 3,
        "max_barriers": 14,
        "barriers_used": 0,
    }
    base.update(kw)
    return Observation(**base)


def test_meta_deterministic_same_seed():
    o = _obs("police")
    a = [MetaController("police", make_rng(11)).decide(o) for _ in range(3)]
    assert a[0] == a[1] == a[2]


def test_meta_logs_strategy_and_reason():
    mc = MetaController("thief", make_rng(5))
    mc.decide(_obs("thief"))
    entry = mc.log[-1]
    assert entry["strategy"] in {"distance", "escape", "evade", "entropy", "endgame", "hybrid"}
    assert isinstance(entry["reason"], str) and entry["reason"]
    assert entry["fallback"] is False


def test_meta_actions_always_legal_in_game():
    cfg = validate(DEFAULT_GAME_CONFIG)
    res = run_sub_game(
        MetaController("police", make_rng(3), horizon=cfg["survival_threshold"]),
        MetaController("thief", make_rng(4), horizon=cfg["survival_threshold"]),
        {**cfg, "sub_game_number": 1},
        "grp",
        DevTestSigner(),
        "0" * 40,
    )
    assert res["illegal"] == 0 and res["diagonal"] == 0


def test_controlled_exploration_bounded_and_logged():
    mc = MetaController("thief", make_rng(1), epsilon=1.0)  # always explore
    for _ in range(20):
        act = mc.decide(_obs("thief", step=10))
        board = Board(7)
        _, sub = enforce(act, _obs("thief", step=10), board, "thief")
        assert not sub  # exploration never yields an illegal action
    assert all(e["explored"] for e in mc.log)


def test_thief_prefers_escape_when_safe():
    mc = MetaController("thief", make_rng(2), horizon=35, epsilon=0.0)
    name, _reason, _ = mc.select(_obs("thief", step=33))  # safe open board -> distance+mobility
    assert name == "escape"


def test_police_prefers_barrier_when_budget_remains():
    mc = MetaController("police", make_rng(2), horizon=35, epsilon=0.0)
    name, _reason, _ = mc.select(_obs("police", step=3))  # target visible, barriers remain
    assert name == "barrier"


def test_police_falls_back_when_barriers_exhausted():
    mc = MetaController("police", make_rng(2), horizon=35, epsilon=0.0)
    name, _reason, _ = mc.select(_obs("police", step=3, barriers_used=14, max_barriers=14))
    assert name in {"hybrid", "herd", "intercept"}  # no budget -> pursuit/compression


def test_no_exploration_when_epsilon_zero():
    mc = MetaController("police", make_rng(9), epsilon=0.0)
    for _ in range(10):
        mc.decide(_obs("police", step=8))
    assert not any(e["explored"] for e in mc.log)
