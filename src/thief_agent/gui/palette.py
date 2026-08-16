"""Colour vocabulary for the Tk presentation layer (P20 replay viewer, P21 live GUI).

Pure data and pure functions -- deliberately no Tk import, so every colour decision is
unit-testable on a headless runner. The heat ramp maps the 0-9 belief buckets produced by
`heatmap.belief_buckets` onto increasingly saturated red, which is the "intensifying
shades of red" the rulebook asks for in the belief heatmap (Chapter 7.3.1)."""

BG = "#12161c"
PANEL = "#1b2129"
FG = "#e8edf3"
MUTED = "#8b97a6"
GRID_LINE = "#2b3440"
BARRIER = "#4a5462"
SELF_POLICE = "#3da5ff"
SELF_THIEF = "#ffd23d"
TURN_GREEN = "#1f9d4d"
LOCKED_GREY = "#5a636e"
VERIFIED_GREEN = "#1f9d4d"
TAMPERED_RED = "#c62828"

# bucket 0 (no belief mass) -> bucket 9 (posterior peak): intensifying red (Chapter 7.3.1)
HEAT_RAMP = (
    "#161b22",
    "#2b1a1c",
    "#431d1d",
    "#5c1e1c",
    "#761d19",
    "#901c14",
    "#aa1d0f",
    "#c32a0a",
    "#da3c06",
    "#f25302",
)


def heat_color(bucket) -> str:
    """Colour for a 0-9 belief bucket; out-of-range values clamp to the ends."""
    try:
        value = int(bucket)
    except (TypeError, ValueError):
        value = 0
    return HEAT_RAMP[max(0, min(9, value))]


def label_color(bucket) -> str:
    """Readable text colour for a bucket label drawn on top of `heat_color(bucket)`."""
    try:
        value = int(bucket)
    except (TypeError, ValueError):
        value = 0
    return "#ffe9df" if value >= 4 else MUTED


def self_color(role: str) -> str:
    """Marker colour for the local player (blue Cop, amber Thief)."""
    return SELF_POLICE if role == "police" else SELF_THIEF


def banner_style(locked: bool) -> tuple[str, str]:
    """(text, background) for the turn indicator: grey LOCKED or green YOUR TURN."""
    return ("LOCKED", LOCKED_GREY) if locked else ("YOUR TURN", TURN_GREEN)


def integrity_style(verified: bool) -> tuple[str, str]:
    """(background, foreground) for the replay integrity badge."""
    return (VERIFIED_GREEN if verified else TAMPERED_RED, "#ffffff")
