"""Standard game state machine with an allow-list of transitions.

Illegal transitions raise IllegalTransitionError; any state may drop to TECHNICAL_LOSS."""

from ..exceptions import IllegalTransitionError

START = "STARTUP"
CONFIG = "CONFIG_LOADING"
NEGOTIATION = "NEGOTIATION"
STEP0 = "STEP0_DECLARATION"
READY = "READY"
COMMIT = "COMMIT"
ACK = "ACKNOWLEDGE"
REVEAL = "PUBLIC_REVEAL"
MOVE = "LOCAL_MOVE"
CLAIM = "CLAIM_HANDLING"
SUBGAME_DONE = "SUBGAME_COMPLETE"
AUDIT = "FINAL_AUDIT"
SERIES_DONE = "SERIES_COMPLETE"
TECH_LOSS = "TECHNICAL_LOSS"

ALLOWED: dict[str, set[str]] = {
    START: {CONFIG},
    CONFIG: {NEGOTIATION},
    NEGOTIATION: {STEP0},
    STEP0: {READY},
    READY: {COMMIT, SUBGAME_DONE},
    COMMIT: {ACK},
    ACK: {REVEAL},
    REVEAL: {MOVE},
    MOVE: {CLAIM, COMMIT, SUBGAME_DONE},
    CLAIM: {COMMIT, SUBGAME_DONE},
    SUBGAME_DONE: {READY, AUDIT},
    AUDIT: {SERIES_DONE},
    SERIES_DONE: set(),
    TECH_LOSS: set(),
}


class StateMachine:
    def __init__(self) -> None:
        self.state = START
        self.history: list[str] = [START]

    def to(self, target: str) -> str:
        if target == TECH_LOSS or target in ALLOWED.get(self.state, set()):
            self.state = target
            self.history.append(target)
            return target
        raise IllegalTransitionError(f"{self.state} -> {target} is not allowed")

    def technical_loss(self) -> str:
        return self.to(TECH_LOSS)
