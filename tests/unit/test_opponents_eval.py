"""P12: baseline/reference/held-out opponents are legal and deterministic; the
evaluation harness produces the required metrics; tournaments are reproducible and
champions are selected from held-out results."""

from thief_agent.domain.board import Board
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.evaluation import evaluate_matchup
from thief_agent.sim.metrics import percentile
from thief_agent.sim.opponents.registry import (
    HELD_OUT_OPPONENTS,
    TUNING_OPPONENTS,
    all_opponents,
    make_opponent,
)
from thief_agent.sim.tournament import run_tournament, select_champion
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import enforce
from thief_agent.strategy.registry import make_brain
from thief_agent.strategy.rng import make_rng

CFG = validate(DEFAULT_GAME_CONFIG)


def _rand_obs(rng, role):
    n = rng.randint(4, 7)
    cells = [(r, c) for r in range(n) for c in range(n)]
    barriers = frozenset(rng.sample(cells, rng.randint(0, n)))
    free = [c for c in cells if c not in barriers]
    pos = rng.choice(free)
    scent = {rng.choice(free): round(rng.random(), 3) for _ in range(rng.randint(0, 3))}
    return Observation(
        role=role,
        self_pos=pos,
        board_size=n,
        barriers=barriers,
        scent=scent,
        step=rng.randint(1, 30),
        max_barriers=14,
        barriers_used=rng.randint(0, 2),
    )


def test_tuning_and_held_out_are_disjoint():
    assert set(TUNING_OPPONENTS) & set(HELD_OUT_OPPONENTS) == set()
    assert len(all_opponents()) == len(TUNING_OPPONENTS) + len(HELD_OUT_OPPONENTS)


def test_all_opponents_emit_legal_actions_both_roles():
    rng = make_rng(6)
    for name in all_opponents():
        for role in ("police", "thief"):
            brain = make_opponent(name, make_rng(3))
            for _ in range(40):
                obs = _rand_obs(rng, role)
                board = Board(obs.board_size, set(obs.barriers))
                _, substituted = enforce(brain.decide(obs), obs, board, role)
                assert not substituted, (name, role)


def test_evaluate_matchup_reports_required_metrics():
    summary = evaluate_matchup(
        CFG,
        lambda r: make_brain("police", "hybrid", r),
        lambda r: make_opponent("reference", r),
        "police",
        seeds=[1, 2, 3],
    )
    for key in (
        "games",
        "capture_rate",
        "survival_rate",
        "avg_self_score",
        "illegal_actions",
        "diagonal_actions",
        "fallback_rate",
        "timeouts",
        "decision_ms_mean",
        "decision_ms_p50",
        "decision_ms_p95",
    ):
        assert key in summary
    assert summary["games"] == 3 and summary["illegal_actions"] == 0


_TIMING = {"decision_ms_mean", "decision_ms_p50", "decision_ms_p95", "timeouts"}


def _deterministic(tour):
    """Strip wall-clock-dependent fields so we can compare game logic reproducibly."""
    return {
        name: {o: {k: v for k, v in s.items() if k not in _TIMING} for o, s in per.items()}
        for name, per in tour["results"].items()
    }


def test_tournament_reproducible_and_bounded():
    a = run_tournament(CFG, "thief", seeds=[1, 2], opponents=TUNING_OPPONENTS)
    b = run_tournament(CFG, "thief", seeds=[1, 2], opponents=TUNING_OPPONENTS)
    assert _deterministic(a) == _deterministic(b)  # game logic is deterministic
    assert a["games"] == len(TUNING_OPPONENTS) * 2 * len(a["results"])


def test_champion_selected_from_held_out():
    champ = select_champion(CFG, "police", seeds=[1, 2, 3])
    assert champ["champion"] in ("greedy", "intercept", "barrier", "herd", "hybrid")
    assert champ["metric"] == "capture_rate" and champ["games"] > 0
    thief_champ = select_champion(CFG, "thief", seeds=[1, 2, 3])
    assert thief_champ["metric"] == "survival_rate"


def test_percentile_interpolates():
    assert percentile([], 0.5) == 0.0
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == 2.5
