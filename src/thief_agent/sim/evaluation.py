"""Evaluation harness (P12): run a candidate brain (as one role) against an opponent
over a fixed seed list, measuring outcome, score, legality, fallback need and
decision-time distribution. Time-bounded and fully reproducible from the seeds."""

import time

from ..domain.board import Board
from ..peer.turn_engine import run_sub_game
from ..security.signer import DevTestSigner
from ..strategy.base import Observation
from ..strategy.firewall import is_legal
from ..strategy.rng import make_rng
from .metrics import MatchStats


class TimingBrain:
    """Wrap a brain to record per-decision wall-clock time and candidate-side
    fallback need (an illegal proposal the firewall would have to replace)."""

    def __init__(self, inner) -> None:
        self.inner = inner
        self.times: list[float] = []
        self.fallbacks = 0

    def decide(self, obs: Observation):
        t0 = time.perf_counter()
        act = self.inner.decide(obs)
        self.times.append(time.perf_counter() - t0)
        board = Board(obs.board_size, set(obs.barriers))
        if not is_legal(act, obs, board, obs.role):
            self.fallbacks += 1
        return act

    def hint(self, obs: Observation) -> str:
        return self.inner.hint(obs)


def evaluate_matchup(
    cfg, candidate_factory, opponent_factory, role, seeds, budget_s=0.05, signer=None
):
    """Aggregate metrics for `candidate` (playing `role`) vs `opponent` over seeds."""
    signer = signer or DevTestSigner()
    stats = MatchStats()
    for seed in seeds:
        cand = TimingBrain(candidate_factory(make_rng(seed)))
        opp = opponent_factory(make_rng(seed + 1000))
        police, thief = (cand, opp) if role == "police" else (opp, cand)
        res = run_sub_game(police, thief, {**cfg, "sub_game_number": 1}, "eval", signer, "0" * 40)
        self_s = res["police_score"] if role == "police" else res["thief_score"]
        opp_s = res["thief_score"] if role == "police" else res["police_score"]
        stats.add(res, self_s, opp_s, cand.times, budget_s)
        stats.fallbacks += cand.fallbacks
    return stats.summary(role)
