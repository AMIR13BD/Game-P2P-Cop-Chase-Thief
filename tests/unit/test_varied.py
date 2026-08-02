"""Scenario-diverse harness: distinct contract-valid scenarios, paired deterministic
evaluation, barrier instrumentation, and bootstrap CIs (corrected evidence path)."""

from thief_agent.sim.scenarios import distance_bucket, generate, start_class
from thief_agent.sim.selfplay import BaselineMeta
from thief_agent.sim.stats import paired_diff_ci, rate_ci
from thief_agent.sim.varied import evaluate
from thief_agent.strategy.meta import MetaController


def _fac(cls, role):
    return lambda rng, h: cls(role, rng, horizon=h, epsilon=0.0)


def test_scenarios_distinct_and_contract_valid():
    scn = generate(120, seed=1)
    assert len({str(s["cfg"]) for s in scn}) == 120  # all distinct configs
    for s in scn:
        c = s["cfg"]
        assert c["grid_size"] >= 7 and c["max_barriers"] >= 14 and c["max_moves"] >= 35
        assert c["cop_start"] != c["thief_start"]  # never the same cell


def test_start_classification_and_buckets():
    assert start_class((0, 0), 7) == "corner"
    assert start_class((0, 3), 7) == "edge"
    assert start_class((3, 3), 7) == "center"
    assert distance_bucket(0, 7) == "near" and distance_bucket(12, 7) == "far"


def test_evaluate_deterministic_and_diverse():
    scn = generate(60, seed=2)
    a = evaluate(scn, _fac(BaselineMeta, "police"), _fac(BaselineMeta, "thief"), "police")
    b = evaluate(scn, _fac(BaselineMeta, "police"), _fac(BaselineMeta, "thief"), "police")
    assert a["rate"] == b["rate"]  # deterministic
    assert a["unique_trajectories"] > 40  # distinct scenarios -> distinct trajectories
    assert a["technical"] == 0 and a["illegal"] == 0
    assert set(a["by_grid"]) and set(a["by_distance"])


def test_barrier_instrumentation():
    scn = generate(40, seed=3)
    r = evaluate(scn, _fac(MetaController, "police"), _fac(BaselineMeta, "thief"), "police", True)
    bm = r["barrier"]
    assert bm["barriers_per_game"] > 0 and 0.0 <= bm["useful_rate"] <= 1.0
    assert bm["self_obstruction"] == 0  # planner never places a self-obstructing cut


def test_bootstrap_cis():
    assert rate_ci([1] * 40) == [1.0, 1.0]
    lo, hi = paired_diff_ci([0, 0, 1, 1], [1, 1, 1, 1])
    assert lo <= 0.5 <= hi
