"""Adaptive meta-controller (P16): selects a whole strategy from the portfolio each
turn from role, game state, belief confidence, remaining turns, score, opponent
profile, barrier/trap risk and past strategy performance.

Guarantees: deterministic under a fixed seed; controlled (seeded) exploration; every
returned action passes the legality firewall (never bypassed); bounded compute (one
delegated brain call); and a per-turn log of the chosen strategy and its reason."""

from ..domain.board import Board
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .connectivity import articulation_points
from .firewall import enforce
from .graph import reachable_area
from .hints import biased_target
from .moves import manhattan, move_toward
from .registry import make_brain, portfolio

POLICE_RISK_WINDOW = 5
THIEF_ENDGAME_WINDOW = 6
CLOSE = 2


def _confidence(board: Board, scent: dict):
    belief = BeliefMap(board)
    belief.update(scent)
    return belief.argmax(), (max(belief.dist.values()) if belief.dist else 0.0)


class MetaController(BrainBase):
    def __init__(self, role, rng, horizon=35, epsilon=0.1, profile=None, credibility=0.5) -> None:
        super().__init__(rng)
        self.role = role
        self.horizon = horizon
        self.epsilon = epsilon
        self.profile = profile or {}
        self.credibility = credibility  # audited opponent hint-honesty (0.5 = neutral)
        self.score_margin = 0
        self._brains: dict[str, BrainBase] = {}
        self._last_name = "hybrid"
        self.log: list[dict] = []

    def _hint_biased(self, obs: Observation, board: Board) -> Action | None:
        """If an AUDIT-credible directional hint shifts the belief cell, pursue it.

        Gated by `biased_target` (credibility must exceed 0.5); unaudited/low-credibility
        or non-directional hints leave the target unchanged and this returns None."""
        if self.role != "police" or not obs.last_hint:
            return None
        raw = BeliefMap(board)
        raw.update(obs.scent)
        biased = biased_target(board, obs.scent, obs.last_hint, self.credibility)
        if biased is None or biased == raw.argmax():
            return None
        return move_toward(obs, board, biased)

    def update_score(self, self_total: int, opp_total: int) -> None:
        self.score_margin = self_total - opp_total

    def _brain(self, name: str) -> BrainBase:
        if name not in self._brains:
            self._brains[name] = make_brain(self.role, name, self.rng)
        return self._brains[name]

    def _police_choice(self, obs, board, target, conf):
        if self.horizon - obs.step <= POLICE_RISK_WINDOW:
            return "hybrid", "near move limit: prioritise capture"
        if target is not None and reachable_area(board, target) > (board.size**2) // 2:
            if obs.barriers_used < obs.max_barriers and conf > 0.15:
                return "barrier", "open space + confident belief: cut escape route"
            return "herd", "open space: compress the thief region"
        return "intercept", "constrained space: intercept directly"

    def _thief_choice(self, obs, board, target):
        if self.horizon - obs.step <= THIEF_ENDGAME_WINDOW:
            return "endgame", "near move limit: maximise survival depth"
        if obs.self_pos in articulation_points(board):
            return "evade", "on an articulation cell: avoid self-trap"
        if target is not None and manhattan(obs.self_pos, target) <= CLOSE:
            return "escape", "pursuer close: maximise distance"
        if self.profile.get("barrier_tendency", 0) > 0.2:
            return "evade", "barrier-heavy opponent: avoid seals"
        return "entropy", "safe: preserve ambiguity"

    def select(self, obs: Observation):
        board = Board(obs.board_size, set(obs.barriers))
        target, conf = _confidence(board, obs.scent)
        if self.role == "police":
            name, reason = self._police_choice(obs, board, target, conf)
        else:
            name, reason = self._thief_choice(obs, board, target)
        explored = False
        if self.epsilon > 0 and self.rng.random() < self.epsilon:
            pool = [k for k in portfolio(self.role) if k != name]
            name, reason, explored = (
                pool[self.rng.randrange(len(pool))],
                "controlled exploration",
                True,
            )
        return name, reason, explored

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        biased = self._hint_biased(obs, board)
        if biased is not None:
            legal, substituted = enforce(biased, obs, board, self.role)
            self._last_name = "intercept"
            self.log.append(
                {
                    "step": obs.step,
                    "strategy": "hint_biased",
                    "reason": "credible audited hint",
                    "explored": False,
                    "fallback": substituted,
                }
            )
            return legal
        name, reason, explored = self.select(obs)
        self._last_name = name
        legal, substituted = enforce(self._brain(name).decide(obs), obs, board, self.role)
        self.log.append(
            {
                "step": obs.step,
                "strategy": name,
                "reason": reason,
                "explored": explored,
                "fallback": substituted,
            }
        )
        return legal

    def hint(self, obs: Observation) -> str:
        return self._brain(self._last_name).hint(obs)
