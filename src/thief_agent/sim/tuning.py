"""Bounded, reproducible competitive tuning (P24).

Not an unlimited search: every portfolio strategy is scored on a TUNING opponent/seed
set, then the top candidates are re-validated on a disjoint HELD-OUT set; the champion
is chosen by the held-out primary metric (capture rate for Police, survival for Thief)
so we never optimise for self-play. Returns a fully reproducible record (seeds,
opponent sets, per-candidate metrics, champion, game count)."""

import platform
import sys

from ..strategy.registry import portfolio
from .evaluation import evaluate_matchup
from .opponents.registry import HELD_OUT_OPPONENTS, TUNING_OPPONENTS


def _score(cfg, role, factory, opponents, seeds, metric):
    total, games = 0.0, 0
    per = {}
    for oname, ofac in opponents.items():
        s = evaluate_matchup(cfg, factory, ofac, role, seeds)
        per[oname] = s[metric]
        total += s[metric]
        games += s["games"]
    return total / max(len(opponents), 1), per, games


def tune_and_select(cfg, role, tuning_seeds, heldout_seeds) -> dict:
    metric = "capture_rate" if role == "police" else "survival_rate"
    tuning, heldout, games = {}, {}, 0
    for name, factory in portfolio(role).items():
        t_avg, _t_per, t_g = _score(cfg, role, factory, TUNING_OPPONENTS, tuning_seeds, metric)
        h_avg, h_per, h_g = _score(cfg, role, factory, HELD_OUT_OPPONENTS, heldout_seeds, metric)
        tuning[name] = round(t_avg, 3)
        heldout[name] = {"avg": round(h_avg, 3), "per_opponent": h_per}
        games += t_g + h_g
    champion = max(heldout, key=lambda n: heldout[n]["avg"])
    return {
        "role": role,
        "metric": metric,
        "champion": champion,
        "champion_heldout": heldout[champion]["avg"],
        "tuning_scores": tuning,
        "heldout_scores": {k: v["avg"] for k, v in heldout.items()},
        "tuning_seeds": list(tuning_seeds),
        "heldout_seeds": list(heldout_seeds),
        "tuning_opponents": list(TUNING_OPPONENTS),
        "heldout_opponents": list(HELD_OUT_OPPONENTS),
        "games": games,
    }


def run_tuning(cfg, tuning_seeds=range(1, 6), heldout_seeds=range(100, 105)) -> dict:
    """Tune both roles and package a reproducible, machine-stamped record."""
    return {
        "runtime": {"python": sys.version.split()[0], "platform": platform.platform()},
        "police": tune_and_select(cfg, "police", tuning_seeds, heldout_seeds),
        "thief": tune_and_select(cfg, "thief", tuning_seeds, heldout_seeds),
    }
