"""Pure view-model for the live GUI: everything the window draws, computed without Tk.

Role-correctness is structural rather than configured -- the perspective is taken from the
Observation itself, so a Thief window necessarily shows the Thief's belief about the Police
and a Cop window the Cop's belief about the Thief. The hidden-position guarantee of
`window.local_view` still holds here: only `self_pos` is ever a known cell, and every other
cell carries a probability bucket, never the opponent's true location."""

from .heatmap import belief_buckets
from .status_banner import banner, input_locked

OPPONENT = {"police": "thief", "thief": "police"}


def live_state(obs, state: str = "MOVE", connected: bool = True, deadline_s=30) -> dict:
    """The complete renderable state for one live frame, from a single Observation."""
    buckets = belief_buckets(obs.board_size, obs.scent, obs.barriers)
    peak = max(buckets, key=buckets.get) if buckets else None
    return {
        "role": obs.role,
        "opponent": OPPONENT.get(obs.role, "opponent"),
        "self_pos": tuple(obs.self_pos),
        "board_size": obs.board_size,
        "barriers": [tuple(b) for b in obs.barriers],
        "buckets": buckets,
        "peak": peak,
        "peak_bucket": buckets.get(peak, 0) if peak is not None else 0,
        "step": obs.step,
        "state": state,
        "locked": input_locked(state),
        "status": banner(state, obs.step, deadline_s, connected),
        "informative": not is_uniform(buckets),
    }


def is_uniform(buckets) -> bool:
    """True when every cell shares one bucket -- a flat, uninformative prior."""
    return len(set(buckets.values())) <= 1


def legend_rows(state: dict) -> list[tuple[str, str]]:
    """(label, value) pairs for the window's side panel."""
    peak = state.get("peak")
    return [
        ("Role", str(state.get("role", "")).upper()),
        ("Tracking", str(state.get("opponent", "")).upper()),
        ("Step", str(state.get("step", 0))),
        ("Protocol state", str(state.get("state", ""))),
        ("Most-likely cell", f"{tuple(peak)}" if peak is not None else "-"),
        ("Belief peak", f"{state.get('peak_bucket', 0)}/9"),
        ("Barriers known", str(len(state.get("barriers", ())))),
    ]
