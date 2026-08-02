"""Deterministic, contract-valid scenario generator for scenario-diverse evaluation.

Varies grid size, both start cells, spatial distance, barrier budget and move/survival
limit within the Appendix F contract (grid>=7, max_barriers>=14, max_moves>=35,
survival_threshold>=35). Same-cell starts are rejected. Fully reproducible from a seed;
returns distinct scenarios (deduped on the full config tuple) each tagged with board size,
distance bucket and start-cell class for subgroup reporting."""

from ..shared.config_validate import validate
from ..shared.defaults import DEFAULT_GAME_CONFIG
from ..strategy.rng import make_rng

GRIDS = (7, 9, 11, 13)  # contract minimum is 7
BARRIERS = (14, 20, 28)  # contract minimum is 14
MOVES = (35, 45, 60)  # contract minimum is 35 (survival_threshold == move limit)
_BASE = validate(DEFAULT_GAME_CONFIG)


def start_class(cell, n: int) -> str:
    r, c = cell
    on_r, on_c = r in (0, n - 1), c in (0, n - 1)
    if on_r and on_c:
        return "corner"
    if on_r or on_c:
        return "edge"
    mid = n // 2
    return "center" if abs(r - mid) <= 1 and abs(c - mid) <= 1 else "interior"


def distance_bucket(dist: int, n: int) -> str:
    frac = dist / (2 * (n - 1))
    return "near" if frac < 0.34 else ("mid" if frac < 0.67 else "far")


def _scenario(n, cop, thf, mb, mv):
    cfg = {
        **_BASE,
        "grid_size": n,
        "cop_start": [cop[0], cop[1]],
        "thief_start": [thf[0], thf[1]],
        "max_barriers": mb,
        "max_moves": mv,
        "survival_threshold": mv,
    }
    dist = abs(cop[0] - thf[0]) + abs(cop[1] - thf[1])
    return {
        "cfg": cfg,
        "grid": n,
        "dist": dist,
        "dist_bucket": distance_bucket(dist, n),
        "cop_class": start_class(cop, n),
        "thief_class": start_class(thf, n),
    }


def generate(count: int, seed: int = 0):
    """`count` distinct contract-valid scenarios, deterministic under `seed`."""
    rng = make_rng(seed)
    seen: set = set()
    out: list = []
    while len(out) < count:
        n = GRIDS[rng.randrange(len(GRIDS))]
        cop = (rng.randrange(n), rng.randrange(n))
        thf = (rng.randrange(n), rng.randrange(n))
        if cop == thf:  # reject identical start cells
            continue
        mb, mv = BARRIERS[rng.randrange(len(BARRIERS))], MOVES[rng.randrange(len(MOVES))]
        key = (n, cop, thf, mb, mv)
        if key in seen:
            continue
        seen.add(key)
        out.append(_scenario(n, cop, thf, mb, mv))
    return out
