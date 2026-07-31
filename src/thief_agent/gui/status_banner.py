"""State / deadline / connection banner and input lock (P21).

Input is accepted only while the protocol is in a move-accepting state; at every other
state (config, negotiation, commit, reveal, done) the GUI locks input to prevent an
out-of-turn or illegal action from being submitted."""

INPUT_STATES = frozenset({"READY", "MOVE"})


def banner(state: str, step: int, deadline_s, connected: bool) -> str:
    conn = "ONLINE" if connected else "OFFLINE"
    return f"[{conn}] state={state} step={step} deadline={deadline_s}s"


def input_locked(state: str) -> bool:
    """True when the GUI must reject input (any non move-accepting state)."""
    return state not in INPUT_STATES
