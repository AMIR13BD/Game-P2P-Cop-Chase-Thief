"""P24 bounded tuning: reproducible, uses disjoint tuning/held-out sets, selects the
champion on held-out results, reports a bounded game count and runtime info. Plus the
latency-injected opponent wrapper."""

from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.opponents.latency import LatencyBrain, latency_opponent
from thief_agent.sim.tuning import run_tuning, tune_and_select
from thief_agent.strategy.production import baseline_brain

CFG = validate(DEFAULT_GAME_CONFIG)


def test_tune_and_select_is_reproducible_and_held_out():
    a = tune_and_select(CFG, "police", range(1, 3), range(50, 52))
    b = tune_and_select(CFG, "police", range(1, 3), range(50, 52))
    assert a == b  # deterministic (game logic; timing excluded from tuning metrics)
    assert a["champion"] in a["heldout_scores"]
    assert set(a["tuning_opponents"]).isdisjoint(a["heldout_opponents"])
    assert a["games"] > 0 and a["metric"] == "capture_rate"


def test_run_tuning_reports_both_roles_and_runtime():
    rec = run_tuning(CFG, tuning_seeds=range(1, 3), heldout_seeds=range(60, 62))
    assert rec["police"]["metric"] == "capture_rate"
    assert rec["thief"]["metric"] == "survival_rate"
    assert "python" in rec["runtime"] and "platform" in rec["runtime"]


def test_latency_opponent_preserves_action():
    plain = baseline_brain("thief", 1)
    wrapped = LatencyBrain(baseline_brain("thief", 1), delay_s=0.0)
    from thief_agent.strategy.base import Observation

    obs = Observation(
        role="thief",
        self_pos=(3, 3),
        board_size=7,
        barriers=frozenset(),
        scent={(0, 0): 0.9},
        step=1,
        max_barriers=14,
        barriers_used=0,
    )
    assert wrapped.decide(obs) == plain.decide(obs)  # latency never changes the move
    fac = latency_opponent(lambda r: baseline_brain("thief", 1), 0.0)
    assert isinstance(fac(None), LatencyBrain)
