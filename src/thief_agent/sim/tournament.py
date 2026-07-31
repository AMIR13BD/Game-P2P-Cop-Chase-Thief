"""Deterministic, time-bounded tournaments (P12): every portfolio strategy versus
every opponent over a fixed seed set, plus champion selection validated on the
held-out opponents only (never the tuning set) to avoid overfitting."""

from ..strategy.registry import portfolio
from .evaluation import evaluate_matchup
from .opponents.registry import HELD_OUT_OPPONENTS, all_opponents


def run_tournament(cfg, role, seeds, opponents=None, budget_s=0.05) -> dict:
    """Round-robin: portfolio[role] vs each opponent. Returns results + game count."""
    opponents = opponents if opponents is not None else all_opponents()
    results: dict[str, dict] = {}
    games = 0
    for name, factory in portfolio(role).items():
        per: dict[str, dict] = {}
        for oname, ofactory in opponents.items():
            summary = evaluate_matchup(cfg, factory, ofactory, role, seeds, budget_s)
            per[oname] = summary
            games += summary["games"]
        results[name] = per
    return {"role": role, "results": results, "games": games, "seeds": list(seeds)}


def select_champion(cfg, role, seeds, budget_s=0.05) -> dict:
    """Pick the strategy with the best held-out primary metric (capture rate for
    Police, survival rate for Thief). Selection uses held-out opponents only."""
    metric = "capture_rate" if role == "police" else "survival_rate"
    tour = run_tournament(cfg, role, seeds, HELD_OUT_OPPONENTS, budget_s)
    best_name, best_score, best_per = None, -1.0, {}
    for name, per in tour["results"].items():
        avg = sum(o[metric] for o in per.values()) / max(len(per), 1)
        if avg > best_score:
            best_name, best_score, best_per = name, avg, per
    return {
        "role": role,
        "champion": best_name,
        "metric": metric,
        "score": round(best_score, 3),
        "games": tour["games"],
        "per_opponent": best_per,
    }
