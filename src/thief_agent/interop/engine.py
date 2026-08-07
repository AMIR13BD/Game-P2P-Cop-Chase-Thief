"""Sub-game engine: wraps our EXISTING gameplay engine (``peer.net_engine.PeerHalf``,
which already drives our production brain and seals byte-compatible commit-reveal
records) and translates it to/from the reference-v3 wire, adding the push-model capture
round-trip and the thief's survival claim. No strategy code is modified — the brain is
reached through exactly the same call PeerHalf already makes.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from ..peer.net_engine import PeerHalf
from ..security.signer import peer_signer
from ..strategy.production import make_gameplay_brain
from .terms import to_flat_cfg
from .wire import TurnMessage


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class IncomingOutcome:
    """What an inbound message told us."""

    i_won: bool = False  # opponent confirmed my capture claim (police)
    i_am_caught: bool = False  # opponent's claim/barrier hit my true cell (thief)
    opponent_won: bool = False  # opponent raised a survival win-claim


class SubEngine:
    """One side of one sub-game against a remote opponent (fresh per sub-game)."""

    def __init__(
        self,
        role: str,
        terms: dict,
        group: str,
        github_commit: str,
        sub_game_number: int,
        seed: int = 1234,
    ):
        flat = to_flat_cfg(terms, seed + 100 + sub_game_number)
        brain = make_gameplay_brain(role, flat["seed"], horizon=terms["max_steps"])
        self.half = PeerHalf(
            role, flat, brain, group, github_commit, peer_signer(group), sub_game_number
        )
        self.role = role
        self.threshold = terms["max_steps"]
        self.pending_response: dict | None = None  # thief's honest claim answer, rides next msg

    @property
    def records(self) -> list:
        return self.half.records

    @property
    def step(self) -> int:
        return self.half.step

    def survived(self) -> bool:
        return self.role == "thief" and self.half.step >= self.threshold

    def take_turn(self) -> TurnMessage:
        """Compute+seal one of our turns (via our brain) and build its wire message."""
        out = self.half.act()
        win = {"type": "survival"} if self.survived() else None
        message = TurnMessage(
            step=out["step"],
            sender=out["sender"],
            commit=out["commit"],
            hint=out["hint"],
            smell_grid=out["scent"],
            timestamp=_now_iso(),
            barrier_placed=out["barrier_placed"],
            capture_claim=out["claim"],
            claim_response=self.pending_response,
            win_claim=win,
        )
        self.pending_response = None
        return message

    def receive(self, msg: TurnMessage) -> IncomingOutcome:
        """Fold an inbound turn into our belief/scent/barriers; resolve capture/survival."""
        legacy = {
            "hint": msg.hint,
            "scent": msg.smell_grid,
            "claim": msg.capture_claim,
            "barrier_placed": msg.barrier_placed,
        }
        caught = self.half.receive(legacy)
        outcome = IncomingOutcome()
        if self.role == "police" and msg.claim_response and msg.claim_response.get("caught"):
            outcome.i_won = True
        if self.role == "thief" and msg.capture_claim is not None:
            answer = {"claim": list(msg.capture_claim), "caught": bool(caught)}
            self.pending_response = answer
            outcome.i_am_caught = bool(caught)
        if msg.win_claim and msg.win_claim.get("type") == "survival":
            outcome.opponent_won = True
        return outcome
