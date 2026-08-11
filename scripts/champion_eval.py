"""Offline OLD-vs-NEW strategy evaluation (no network, no Gmail, no counted mode).

OLD = frozen baseline selection (sim.selfplay.BaselineMeta); NEW = current
MetaController. Measured over scenario-diverse contract-valid boards against the
uoh-ay26 public-policy proxy and generic opponents, plus self-play. Reports thief
survival rate / mean survival turns and police capture rate / mean capture turn.
Deterministic. Usage: `uv run python scripts/champion_eval.py [n_scenarios]`."""

import statistics
import sys

from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.sim.opponents.simple import GreedyBrain, MobilityBrain, ShortestPathBrain
from thief_agent.sim.opponents.uoh import UohCopBrain, UohThiefBrain
from thief_agent.sim.scenarios import generate
from thief_agent.sim.selfplay import BaselineMeta
from thief_agent.strategy.meta import MetaController
from thief_agent.strategy.rng import make_rng

SIGNER = DevTestSigner()


def _meta(cls, role, horizon):
    return lambda rng: cls(role, rng, horizon=horizon, epsilon=0.0)


def _play(cfg, cand_factory, opp_factory, role, seed):
    h = cfg["survival_threshold"]
    cand = cand_factory(h)(make_rng(seed))
    opp = opp_factory(h)(make_rng(seed + 1000))
    police, thief = (cand, opp) if role == "police" else (opp, cand)
    return run_sub_game(police, thief, {**cfg, "sub_game_number": 1}, "eval", SIGNER, "0" * 40)


def _bench(cand_factory, opp_factory, role, scenarios):
    wins, steps, self_score, illegal = 0, [], 0, 0
    want = "capture" if role == "police" else "survival"
    for i, sc in enumerate(scenarios):
        res = _play(sc["cfg"], cand_factory, opp_factory, role, seed=i)
        wins += res["outcome"] == want
        steps.append(res["steps"])
        self_score += res["police_score"] if role == "police" else res["thief_score"]
        illegal += res["illegal"]
    n = len(scenarios)
    return {
        "rate": round(wins / n, 3),
        "mean_turns": round(statistics.mean(steps), 1),
        "avg_score": round(self_score / n, 2),
        "illegal": illegal,
    }


def _uoh_cop(_h):
    return lambda rng: UohCopBrain(rng)


def _uoh_thief(_h):
    return lambda rng: UohThiefBrain(rng)


def _simple(cls):
    return lambda _h: (lambda rng: cls(rng))


def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    scen = generate(n, seed=20260810)
    # factories close over horizon (set per scenario inside _play via survival_threshold)
    nt = lambda h: _meta(MetaController, "thief", h)  # noqa: E731
    ot = lambda h: _meta(BaselineMeta, "thief", h)  # noqa: E731
    np_ = lambda h: _meta(MetaController, "police", h)  # noqa: E731
    op = lambda h: _meta(BaselineMeta, "police", h)  # noqa: E731

    def row(label, res):
        print(f"  {label:32s} rate={res['rate']:.3f}  mean_turns={res['mean_turns']:5.1f}  "
              f"avg_score={res['avg_score']:5.2f}  illegal={res['illegal']}")

    print(f"\n=== THIEF survival ({n} scenarios; higher rate/score better) ===")
    row("OLD thief vs uoh-cop", _bench(ot, _uoh_cop, "thief", scen))
    row("NEW thief vs uoh-cop", _bench(nt, _uoh_cop, "thief", scen))
    row("NEW thief vs shortest-cop", _bench(nt, _simple(ShortestPathBrain), "thief", scen))
    row("NEW thief vs greedy-cop", _bench(nt, _simple(GreedyBrain), "thief", scen))
    row("NEW thief vs mobility-cop", _bench(nt, _simple(MobilityBrain), "thief", scen))

    print(f"\n=== POLICE capture ({n} scenarios; higher rate/score better) ===")
    row("OLD police vs uoh-thief", _bench(op, _uoh_thief, "police", scen))
    row("NEW police vs uoh-thief", _bench(np_, _uoh_thief, "police", scen))
    row("NEW police vs shortest-thief", _bench(np_, _simple(ShortestPathBrain), "police", scen))
    row("NEW police vs greedy-thief", _bench(np_, _simple(GreedyBrain), "police", scen))
    row("NEW police vs mobility-thief", _bench(np_, _simple(MobilityBrain), "police", scen))

    print("\n=== SELF-PLAY (NEW vs NEW) ===")
    row("NEW police vs NEW thief", _bench(np_, nt, "police", scen))


if __name__ == "__main__":
    main()
