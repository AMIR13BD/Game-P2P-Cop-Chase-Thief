"""Protocol data models. Local Day-1 uses StepRecord; TurnMessage documents the
wire shape (only public fields) that Day-2 networking will actually send."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepRecord:
    """A sealed per-turn record: full payload plus its nonce and commitment."""

    payload: dict[str, Any]
    nonce: str
    commit: str

    def to_dict(self) -> dict:
        return {"payload": self.payload, "nonce": self.nonce, "commit": self.commit}


@dataclass
class TurnMessage:
    """Public fields a peer would send per turn. True move/position/verdict and the
    nonce are NOT here; they are sealed inside `commit` until the final audit."""

    step: int
    sender: str
    hint: str
    commit: str
    scent: dict = field(default_factory=dict)
    barrier_placed: list | None = None
    capture_claim: list | None = None
    claim_response: dict | None = None
    win_claim: dict | None = None


def build_payload(step: int, role: str, state: str, move: str, intent: str, hint: str) -> dict:
    """The sealed record: richer than (state|move|intent|nonce) per book ch5."""
    return {
        "step": step,
        "role": role,
        "state": state,
        "move": move,
        "intent": intent,
        "hint": hint,
    }
