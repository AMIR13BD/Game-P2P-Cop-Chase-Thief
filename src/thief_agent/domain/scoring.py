"""Fixed scoring table (Appendix F). Values are immutable constants."""

CAPTURE_COP = 20
CAPTURE_THIEF = 5
SURVIVAL_COP = 5
SURVIVAL_THIEF = 10
TIE_SCORE = 2
TECHNICAL_LOSS = 0


def score_outcome(outcome: str) -> tuple[int, int]:
    """Return (police_score, thief_score) for a sub-game outcome."""
    if outcome == "capture":
        return (CAPTURE_COP, CAPTURE_THIEF)
    if outcome == "survival":
        return (SURVIVAL_COP, SURVIVAL_THIEF)
    if outcome == "technical":
        return (TECHNICAL_LOSS, TECHNICAL_LOSS)
    raise ValueError(f"unknown outcome '{outcome}'")
