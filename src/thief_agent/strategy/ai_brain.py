"""AIPrimaryBrain: OpenAI-primary tactical selection over the deterministic engine.

Pipeline (matches the frozen architecture): the deterministic brain generates the
legal candidate list, hard-safety features and a fallback pick; the advisor lets
OpenAI select among those candidates (per the configured call policy); the choice is
validated and firewall-enforced. Any API failure/timeout/budget issue => deterministic
pick. OpenAI never creates actions, never sees hidden truth, never affects the
capture-claim (the frozen engine emits that after the action resolves)."""

from collections import Counter

from ..advisor.advisor import TacticalAdvisor
from ..advisor.client import OpenAIClient
from ..advisor.features import candidate_actions, tactical_context
from ..domain.board import Board
from .base import Action, BrainBase, Observation
from .belief import BeliefMap
from .firewall import enforce
from .meta import MetaController

_DIRS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}


def _same(a: Action, b: Action) -> bool:
    return a.kind == b.kind and a.direction == b.direction


class AIPrimaryBrain(BrainBase):
    def __init__(self, role, rng, horizon=35, policy="B", client=None, seed=0) -> None:
        super().__init__(rng)
        self.role = role
        self.horizon = horizon
        # Deterministic engine = the full MetaController (portfolio police + survivor
        # thief): it generates the fallback pick and stays legal/firewalled on its own.
        self.det = MetaController(role, rng, horizon=horizon, epsilon=0.0, strategy_seed=seed)
        self.advisor = TacticalAdvisor(client or OpenAIClient(), policy=policy)
        self.profile: dict = {"dirs": Counter(), "reversals": 0, "moves": 0}
        self._last_peak = None

    def _update_profile(self, board: Board, obs: Observation) -> dict:
        belief = BeliefMap(board)
        belief.update(obs.scent)
        peak = belief.argmax()
        if peak is not None and self._last_peak is not None and peak != self._last_peak:
            dr, dc = peak[0] - self._last_peak[0], peak[1] - self._last_peak[1]
            for name, (mr, mc) in _DIRS.items():
                if (dr, dc) == (mr, mc):
                    self.profile["dirs"][name] += 1
            self.profile["moves"] += 1
        self._last_peak = peak
        top = self.profile["dirs"].most_common(1)
        return {
            "opp_moves": self.profile["moves"],
            "opp_favored_dir": top[0][0] if top else None,
        }

    def decide(self, obs: Observation) -> Action:
        board = Board(obs.board_size, set(obs.barriers))
        profile = self._update_profile(board, obs)
        det_action = self.det.decide(obs)
        belief = BeliefMap(board)
        belief.update(obs.scent)
        candidates = candidate_actions(obs, board, belief.argmax())
        if not any(_same(det_action, c) for c in candidates):
            candidates.append(det_action)  # keep the fallback selectable
        recommended = next(f"A{i}" for i, c in enumerate(candidates) if _same(det_action, c))
        context = tactical_context(obs, board, candidates, recommended, profile, self.horizon)
        chosen_id, _source = self.advisor.select(obs, context, recommended)
        idx = int(chosen_id[1:]) if chosen_id and chosen_id[1:].isdigit() else int(recommended[1:])
        action = candidates[idx] if 0 <= idx < len(candidates) else det_action
        legal, _sub = enforce(action, obs, board, self.role)  # final safety net
        return legal

    def hint(self, obs: Observation) -> str:
        return self.det.hint(obs)
