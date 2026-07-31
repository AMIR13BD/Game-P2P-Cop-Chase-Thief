"""Batch simulation: accumulate turns and count illegal/diagonal/timeouts/exceptions."""

import time

from ..shared.gitinfo import current_commit
from .engine import simulate

DECISION_BUDGET_S = 1.0


def run_batch(cfg: dict, min_turns: int = 10000, base_seed: int = 1) -> dict:
    total = sub = illegal = diagonal = timeouts = exceptions = 0
    outcomes: dict[str, int] = {}
    commit = current_commit(default="0000000")
    seed = base_seed
    while total < min_turns:
        seed += 1
        sub += 1
        t0 = time.perf_counter()
        try:
            res = simulate(cfg, seed, github_commit=commit)
        except Exception:  # noqa: BLE001 - batch must never crash; count instead
            exceptions += 1
            continue
        if time.perf_counter() - t0 > DECISION_BUDGET_S:
            timeouts += 1
        total += len(res["records"]) - 1
        illegal += res["illegal"]
        diagonal += res["diagonal"]
        outcomes[res["outcome"]] = outcomes.get(res["outcome"], 0) + 1
    return {
        "turns": total,
        "sub_games": sub,
        "illegal": illegal,
        "diagonal": diagonal,
        "timeouts": timeouts,
        "exceptions": exceptions,
        "outcomes": outcomes,
    }
