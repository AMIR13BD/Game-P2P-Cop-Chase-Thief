#!/usr/bin/env python3
"""One-at-a-time (OAT) parameter sensitivity sweep over the real game engine.

Varies a single Appendix-F parameter at a time around the agreed baseline, replays the
production brains through `sim.evaluation.evaluate_matchup`, and records the Cop's
capture rate with a Wilson 95% interval. Nothing is simulated approximately: every point
is a real six-sub-game-engine run under a fixed seed set, so the numbers are reproducible.

    uv run python scripts/param_sweep.py --seeds 200 --out docs/research/oat_sensitivity.csv
"""

import argparse
import csv
import math
import pathlib

from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.evaluation import evaluate_matchup
from thief_agent.sim.opponents.registry import make_opponent
from thief_agent.strategy.production import make_gameplay_brain

# One-at-a-time grid. Baseline value first in each list is not assumed - the agreed
# Appendix-F value is marked in the output so the notebook can highlight it.
SWEEP: dict[str, list] = {
    "grid_size": [5, 7, 9, 11, 13],
    "max_barriers": [7, 14, 20, 28],
    "max_moves": [25, 35, 45, 60],
    "pheromone_decay": [0.05, 0.10, 0.20, 0.40],
}
BASELINE = {"grid_size": 7, "max_barriers": 14, "max_moves": 35, "pheromone_decay": 0.10}


def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval - correct for proportions near 0 or 1, unlike normal CI."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def variant(base: dict, key: str, value) -> dict:
    """Baseline config with exactly one parameter changed (survival tracks max_moves)."""
    cfg = dict(base)
    cfg[key] = value
    if key == "max_moves":
        cfg["survival_threshold"] = value
    return cfg


def measure(cfg: dict, seeds: list[int], opponent: str) -> dict:
    """Cop capture rate and decision latency against one opponent thief on `cfg`."""
    if opponent == "self":
        opp = lambda rng: make_gameplay_brain("thief", 2, baseline=False)  # noqa: E731
    else:
        opp = lambda rng: make_opponent(opponent, rng)  # noqa: E731
    return evaluate_matchup(
        cfg,
        lambda rng: make_gameplay_brain("police", 1, baseline=False),
        opp,
        "police",
        seeds,
    )


def sweep(seeds: list[int], opponents: list[str]) -> list[dict]:
    base = validate(DEFAULT_GAME_CONFIG)
    rows: list[dict] = []
    for opponent in opponents:
        for key, values in SWEEP.items():
            for value in values:
                stats = measure(variant(base, key, value), seeds, opponent)
                rate = stats["capture_rate"]
                lo, hi = wilson(round(rate * len(seeds)), len(seeds))
                rows.append(
                    {
                        "opponent": opponent,
                        "parameter": key,
                        "value": value,
                        "is_baseline": int(BASELINE[key] == value),
                        "seeds": len(seeds),
                        "capture_rate": round(rate, 4),
                        "ci_lo": round(lo, 4),
                        "ci_hi": round(hi, 4),
                        "survival_rate": round(stats["survival_rate"], 4),
                        "avg_cop_score": round(stats["avg_self_score"], 3),
                        "decision_ms_p95": round(stats["decision_ms_p95"], 3),
                    }
                )
                print(f"  {opponent:<12} {key}={value:<6} capture={rate:.3f}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(prog="param_sweep")
    parser.add_argument("--seeds", type=int, default=200)
    parser.add_argument("--out", default="docs/research/oat_sensitivity.csv")
    parser.add_argument("--opponents", default="self,shortest,mobility,reference")
    args = parser.parse_args()

    seeds = list(range(1, args.seeds + 1))
    opponents = [o.strip() for o in args.opponents.split(",") if o.strip()]
    points = sum(len(v) for v in SWEEP.values()) * len(opponents)
    print(f"OAT sweep: {points} points x {len(seeds)} seeds")
    rows = sweep(seeds, opponents)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
