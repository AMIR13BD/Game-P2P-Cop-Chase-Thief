"""The self-play A/B harness is faithful: BaselineMeta re-declares the frozen selection
rules, the candidate MetaController selects differently, and the candidate Police captures
more than the baseline over a fixed seed set. Deterministic."""

from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.selfplay import BaselineMeta, run_matchup
from thief_agent.strategy.base import Observation
from thief_agent.strategy.meta import MetaController
from thief_agent.strategy.rng import make_rng

CFG = validate(DEFAULT_GAME_CONFIG)


def _obs(role, **kw):
    b = {
        "role": role,
        "self_pos": (3, 3),
        "board_size": 7,
        "barriers": frozenset(),
        "scent": {(0, 0): 0.9},
        "step": 3,
        "max_barriers": 14,
        "barriers_used": 0,
    }
    b.update(kw)
    return Observation(**b)


def test_baseline_encodes_frozen_rules():
    bt = BaselineMeta("thief", make_rng(2), horizon=35, epsilon=0.0)
    assert bt.select(_obs("thief", step=33))[0] == "endgame"  # frozen thief near-limit
    bp = BaselineMeta("police", make_rng(2), horizon=35, epsilon=0.0)
    assert bp.select(_obs("police", step=33))[0] == "hybrid"  # frozen police near-limit


def test_candidate_selection_differs():
    ct = MetaController("thief", make_rng(2), horizon=35, epsilon=0.0)
    assert ct.select(_obs("thief", step=33))[0] == "escape"  # candidate thief
    cp = MetaController("police", make_rng(2), horizon=35, epsilon=0.0)
    assert cp.select(_obs("police", step=3))[0] == "barrier"  # candidate police


def test_candidate_police_beats_baseline():
    seeds = list(range(1, 61))
    a = run_matchup(CFG, BaselineMeta, BaselineMeta, seeds, "police")
    b = run_matchup(CFG, MetaController, BaselineMeta, seeds, "police")
    assert b["capture_rate"] > a["capture_rate"]


def test_selfplay_deterministic():
    seeds = list(range(1, 21))
    r1 = run_matchup(CFG, MetaController, BaselineMeta, seeds, "police")["capture_rate"]
    r2 = run_matchup(CFG, MetaController, BaselineMeta, seeds, "police")["capture_rate"]
    assert r1 == r2
