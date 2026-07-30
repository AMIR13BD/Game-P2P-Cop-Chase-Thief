"""Stable strategy interfaces. Observations carry ONLY legally-visible live data."""

from dataclasses import dataclass, field

Cell = tuple[int, int]


@dataclass(frozen=True)
class Action:
    kind: str  # "MOVE" | "STAY" | "BARRIER"
    direction: str | None = None  # MOVE: N/S/E/W ; BARRIER: SELF/N/S/E/W


@dataclass(frozen=True)
class Observation:
    role: str
    self_pos: Cell
    board_size: int
    barriers: frozenset[Cell]
    scent: dict = field(default_factory=dict)  # opponent's received scent (no coords of self)
    last_hint: str = ""
    step: int = 0
    max_barriers: int = 14
    barriers_used: int = 0


class BrainBase:
    """Base class for all brains. Subclasses override `decide`."""

    def __init__(self, rng) -> None:
        self.rng = rng

    def decide(self, obs: Observation) -> Action:  # pragma: no cover - abstract
        raise NotImplementedError

    def hint(self, obs: Observation) -> str:
        return "moving through the streets"  # offline template default, 0 tokens
