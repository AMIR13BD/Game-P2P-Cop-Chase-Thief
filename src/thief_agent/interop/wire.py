"""The reference-v3 wire message shapes (exact official field names).

Nulls are emitted explicitly to match the reference's own wire; a receiver tolerates
either. Tool argument names mirror the reference exactly: ``negotiate`` /
``receive_turn`` / ``receive_control`` take ``message``; ``submit_audit`` takes
``payload``.
"""

from dataclasses import asdict, dataclass, field


@dataclass
class TurnMessage:
    """One half-turn. The commit is sent; the nonce is withheld until the audit."""

    step: int
    sender: str  # "police" | "thief"
    commit: str
    hint: str
    smell_grid: dict = field(default_factory=dict)  # {"r,c": intensity} scent trail
    timestamp: str = ""
    barrier_placed: list | None = None  # public: impassable for both (cop only)
    capture_claim: list | None = None  # police: "I claim you are at [r,c]"
    claim_response: dict | None = None  # thief: {"claim": [r,c], "caught": bool}
    win_claim: dict | None = None  # thief: {"type": "survival"}

    def to_wire(self) -> dict:
        return asdict(self)

    @classmethod
    def from_wire(cls, data: dict) -> "TurnMessage":
        known = set(cls.__dataclass_fields__)
        missing = {"step", "sender", "commit"} - set(data)
        if missing:
            raise ValueError(f"turn message missing fields: {sorted(missing)}")
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class AuditPayload:
    """End-of-game reveal: every record with its nonce, for the OPPONENT to re-hash."""

    sender: str
    records: list
    result_claim: str  # "capture" | "survival" | "timeout"

    def to_wire(self) -> dict:
        return asdict(self)

    @classmethod
    def from_wire(cls, data: dict) -> "AuditPayload":
        known = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class Negotiation:
    """The pre-game greeting: the flat signed terms ride here, extras BESIDE them."""

    terms: dict
    nonce: str
    signature: str
    group_id: str
    role: str | None = None  # SPEC §7.2
    sub_game_number: int | None = None  # SPEC §7.2
    identity: dict = field(default_factory=dict)
    game_uid: str | None = None  # SPEC §7.3 (declared once opponent known)

    def to_wire(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_wire(cls, data: dict) -> "Negotiation":
        known = set(cls.__dataclass_fields__)
        return cls(**{k: v for k, v in data.items() if k in known})
