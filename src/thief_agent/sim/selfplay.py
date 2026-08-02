"""Reproducible offline self-play A/B benchmark for strategy evaluation.

Compares the CURRENT (candidate) MetaController selection against the FROZEN baseline
selection (commit police 00de656 / thief ac8d585) in a single process, so no strategy
files are copied between repositories. `BaselineMeta` re-declares the frozen
_police_choice / _thief_choice / select verbatim; `tests/unit/test_selfplay.py` asserts it
reproduces the frozen baseline outcomes on fixed seeds, which guarantees the A/B is faithful.

Matchups: A base/base, B candidate-police/base-thief, C base-police/candidate-thief,
D candidate/candidate. Deterministic and fully reproducible from the seed list."""

from ..strategy.connectivity import articulation_points
from ..strategy.graph import reachable_area
from ..strategy.meta import MetaController, _confidence
from ..strategy.moves import manhattan
from ..strategy.registry import portfolio
from .evaluation import evaluate_matchup

# frozen baseline windows (verbatim from commit 00de656 / ac8d585)
_POLICE_RISK_WINDOW = 5
_THIEF_ENDGAME_WINDOW = 6
_CLOSE = 2


class BaselineMeta(MetaController):
    """Frozen baseline selection (commit 00de656 / ac8d585), used only for A/B reference."""

    def _b_police(self, obs, board, target, conf):
        if self.horizon - obs.step <= _POLICE_RISK_WINDOW:
            return "hybrid", "near move limit: prioritise capture"
        if target is not None and reachable_area(board, target) > (board.size**2) // 2:
            if obs.barriers_used < obs.max_barriers and conf > 0.15:
                return "barrier", "open space + confident belief: cut escape route"
            return "herd", "open space: compress the thief region"
        return "intercept", "constrained space: intercept directly"

    def _b_thief(self, obs, board, target):
        if self.horizon - obs.step <= _THIEF_ENDGAME_WINDOW:
            return "endgame", "near move limit: maximise survival depth"
        if obs.self_pos in articulation_points(board):
            return "evade", "on an articulation cell: avoid self-trap"
        if target is not None and manhattan(obs.self_pos, target) <= _CLOSE:
            return "escape", "pursuer close: maximise distance"
        if self.profile.get("barrier_tendency", 0) > 0.2:
            return "evade", "barrier-heavy opponent: avoid seals"
        return "entropy", "safe: preserve ambiguity"

    def select(self, obs):
        from ..domain.board import Board

        board = Board(obs.board_size, set(obs.barriers))
        target, conf = _confidence(board, obs.scent)
        if self.role == "police":
            name, reason = self._b_police(obs, board, target, conf)
        else:
            name, reason = self._b_thief(obs, board, target)
        explored = False
        if self.epsilon > 0 and self.rng.random() < self.epsilon:
            pool = [k for k in portfolio(self.role) if k != name]
            name, reason, explored = (pool[self.rng.randrange(len(pool))], "explore", True)
        return name, reason, explored


def _factory(cls, role):
    return lambda rng: cls(role, rng, horizon=35, epsilon=0.0)


def run_matchup(cfg, police_cls, thief_cls, seeds, measure="police", budget_s=0.05):
    """Aggregate metrics for the `measure` side of police_cls-vs-thief_cls over seeds."""
    pol, thf = _factory(police_cls, "police"), _factory(thief_cls, "thief")
    if measure == "police":
        return evaluate_matchup(cfg, pol, thf, "police", seeds, budget_s)
    return evaluate_matchup(cfg, thf, pol, "thief", seeds, budget_s)


def four_matchups(cfg, seeds):
    """A/B/C/D summary dict. Candidate = current MetaController; Baseline = BaselineMeta."""
    cand, base = MetaController, BaselineMeta
    return {
        "A_base_vs_base": run_matchup(cfg, base, base, seeds, "police"),
        "B_candPolice_vs_baseThief": run_matchup(cfg, cand, base, seeds, "police"),
        "C_basePolice_vs_candThief": run_matchup(cfg, base, cand, seeds, "thief"),
        "D_cand_vs_cand_police": run_matchup(cfg, cand, cand, seeds, "police"),
    }
