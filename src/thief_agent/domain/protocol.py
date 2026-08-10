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


def build_payload(
    step: int,
    role: str,
    state: str,
    move: str,
    intent: str,
    hint: str,
    barrier: list | None = None,
    capture_claim: list | None = None,
    claim_response: dict | None = None,
) -> dict:
    """The sealed record: richer than (state|move|intent|nonce) per book ch5.

    ``move`` is always a legal move_set token (N/S/E/W/STAY). A barrier turn foregoes
    movement (book §3.4: "in a turn where the cop foregoes movement, it may place a
    barrier"), so its ``move`` is STAY and the placement is declared SEPARATELY here as
    ``barrier_placed`` — never encoded as a 'BARRIER:*' move. Absent unless a barrier is set.

    ``capture_claim`` (cop's claimed [r,c]) and ``claim_response`` (thief's truthful
    {"claim", "caught"}) are SEALED here when the LIVE turn actually carried them, so the
    capture protocol is auditable from signed evidence — never derived from coordinates.
    Both are absent unless the real event occurred (identical wire shape otherwise)."""
    payload = {
        "step": step,
        "role": role,
        "state": state,
        "move": move,
        "intent": intent,
        "hint": hint,
    }
    if barrier is not None:
        payload["barrier_placed"] = list(barrier)
    if capture_claim is not None:
        payload["capture_claim"] = list(capture_claim)
    if claim_response is not None:
        payload["claim_response"] = dict(claim_response)
    return payload
