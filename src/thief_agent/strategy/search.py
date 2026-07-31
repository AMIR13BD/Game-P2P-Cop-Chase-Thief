"""Anytime / iterative-deepening search primitives with a wall-clock deadline.

Strategies use these to stay bounded: they always return the best legal candidate
found so far and never exceed their time budget. Deterministic given a fixed set of
candidates and evaluator (the clock only decides *when* to stop, not *what* wins)."""

import time
from collections.abc import Callable, Iterable
from typing import Any


def anytime_best(
    candidates: Iterable[Any],
    evaluate: Callable[[Any], float],
    deadline_s: float,
    now: Callable[[], float] = time.perf_counter,
) -> Any:
    """Return the highest-scoring candidate, stopping once the deadline elapses.

    Always returns a candidate if any were seen; ties keep the earliest (stable)."""
    start = now()
    best: Any = None
    best_score: float | None = None
    for cand in candidates:
        score = evaluate(cand)
        if best_score is None or score > best_score:
            best, best_score = cand, score
        if now() - start >= deadline_s:
            break
    return best


def deepening_best(
    candidates: list[Any],
    evaluate_at_depth: Callable[[Any, int], float],
    max_depth: int,
    deadline_s: float,
    now: Callable[[], float] = time.perf_counter,
) -> Any:
    """Iterative deepening: evaluate all candidates at increasing depth while time
    remains, returning the best candidate from the deepest fully-scored level."""
    start = now()
    best: Any = candidates[0] if candidates else None
    for depth in range(1, max_depth + 1):
        level_best: Any = None
        level_score: float | None = None
        for cand in candidates:
            score = evaluate_at_depth(cand, depth)
            if level_score is None or score > level_score:
                level_best, level_score = cand, score
            if now() - start >= deadline_s:
                return level_best if level_best is not None else best
        best = level_best
        if now() - start >= deadline_s:
            break
    return best
