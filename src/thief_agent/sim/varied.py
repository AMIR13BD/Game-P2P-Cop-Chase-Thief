"""Scenario-diverse paired evaluation with real barrier instrumentation.

Runs one deterministic sub-game per distinct scenario (see sim/scenarios), so N scenarios
give N genuinely different games (not one repeated game under N seeds). `evaluate` reports
the outcome rate, unique-trajectory count, per-game success vector (for paired CIs),
board/distance subgroups, latency, technical/illegal/timeout counts, and — when
instrumenting Police — barrier metrics measured from the exact observation the engine feeds."""

import time

from ..domain.board import Board
from ..domain.rules import barrier_cell
from ..peer.turn_engine import run_sub_game
from ..security.signer import DevTestSigner
from ..strategy.belief import BeliefMap
from ..strategy.graph import distance_map, reachable_area
from ..strategy.rng import make_rng
from .metrics import percentile


class _Timed:
    def __init__(self, inner):
        self.inner, self.times = inner, []

    def decide(self, obs):
        t0 = time.perf_counter()
        act = self.inner.decide(obs)
        self.times.append(time.perf_counter() - t0)
        return act

    def hint(self, obs):
        return self.inner.hint(obs)


class _BarrierProbe(_Timed):
    def __init__(self, inner):
        super().__init__(inner)
        self.placed = self.useful = self.wasted = self.selfblock = self.area = 0

    def decide(self, obs):
        act = super().decide(obs)
        if act.kind != "BARRIER":
            return act
        self.placed += 1
        board = Board(obs.board_size, set(obs.barriers))
        cell = barrier_cell(obs.self_pos, act.direction)
        belief = BeliefMap(board)
        belief.update(obs.scent)
        tgt = belief.argmax()
        trial = Board(obs.board_size, board.barriers | {cell})
        if tgt is None:
            return act
        if not trial.passable(tgt):  # barrier seals the belief cell itself (a capture seal)
            self.useful += 1
            return act
        red = reachable_area(board, tgt) - reachable_area(trial, tgt)
        if red > 0:
            self.useful += 1
            self.area += red
        else:
            self.wasted += 1
        if distance_map(trial, tgt).get(obs.self_pos) is None:
            self.selfblock += 1  # placed barrier that cuts us off from the target
        return act


def _last_police_kind(records) -> str:
    for rec in reversed(records):
        p = rec.get("payload", {})
        if p.get("role") == "police":
            return p.get("move", "STAY:").split(":")[0]
    return ""


def run_one(scn, police_factory, thief_factory, idx, measure, instrument=False, signer=None):
    signer = signer or DevTestSigner()
    cfg = scn["cfg"]
    horizon = cfg["survival_threshold"]  # brains see the scenario's real move limit
    pol = police_factory(make_rng(idx), horizon)
    pol = _BarrierProbe(pol) if instrument else _Timed(pol)
    thf = _Timed(thief_factory(make_rng(idx + 1000), horizon))
    res = run_sub_game(pol, thf, {**cfg, "sub_game_number": 1}, "v", signer, "0" * 40)
    times = pol.times if measure == "police" else thf.times
    want = "capture" if measure == "police" else "survival"
    row = {
        "ok": 1 if res["outcome"] == want else 0,
        "outcome": res["outcome"],
        "illegal": res["illegal"] + res["diagonal"],
        "times": times,
        "traj": hash((tuple(res["trajectory"]), res["outcome"], res["steps"])),
    }
    if instrument:
        row["probe"] = pol
        row["budget_left"] = cfg["max_barriers"] - pol.placed
        row["cap_by_barrier"] = int(
            res["outcome"] == "capture" and _last_police_kind(res["records"]) == "BARRIER"
        )
    return row


def _rate_by(scens, games, key):
    groups: dict = {}
    for s, g in zip(scens, games, strict=True):
        groups.setdefault(key(s), []).append(g["ok"])
    return {k: {"n": len(v), "rate": round(sum(v) / len(v), 3)} for k, v in sorted(groups.items())}


def _barrier_totals(games, n):
    g = [x for x in games if "probe" in x]
    placed = sum(x["probe"].placed for x in g)
    useful = sum(x["probe"].useful for x in g)
    return {
        "barriers_per_game": round(placed / n, 3),
        "useful": useful,
        "zero_or_negative": sum(x["probe"].wasted for x in g),
        "useful_rate": round(useful / placed, 3) if placed else 0.0,
        "self_obstruction": sum(x["probe"].selfblock for x in g),
        "reachable_area_reduction_total": sum(x["probe"].area for x in g),
        "capture_via_barrier_action": sum(x["cap_by_barrier"] for x in g),
        "avg_budget_remaining": round(sum(x["budget_left"] for x in g) / n, 2),
    }


def evaluate(scenarios, police_factory, thief_factory, measure, instrument=False):
    games = [
        run_one(s, police_factory, thief_factory, i, measure, instrument)
        for i, s in enumerate(scenarios)
    ]
    n = len(games)
    times = [t for g in games for t in g["times"]]
    ok = [g["ok"] for g in games]
    agg = {
        "scenarios": n,
        "unique_trajectories": len({g["traj"] for g in games}),
        "rate": round(sum(ok) / n, 4) if n else 0.0,
        "successes": sum(ok),
        "ok_vector": ok,
        "technical": sum(1 for g in games if g["outcome"] == "technical"),
        "illegal": sum(g["illegal"] for g in games),
        "timeouts": sum(1 for t in times if t > 1.0),
        "p50_ms": round(1000 * percentile(times, 0.5), 3),
        "p95_ms": round(1000 * percentile(times, 0.95), 3),
        "max_ms": round(1000 * max(times), 3) if times else 0.0,
        "by_grid": _rate_by(scenarios, games, lambda s: s["grid"]),
        "by_distance": _rate_by(scenarios, games, lambda s: s["dist_bucket"]),
    }
    if instrument:
        agg["barrier"] = _barrier_totals(games, n)
    return agg
