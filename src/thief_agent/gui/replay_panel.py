"""Pure presentation helpers for the replay viewer: trail shading and the info panel.

Separated from `tk_replay` so the window stays inside the line limit and so this logic
stays testable without a display."""

TRAIL = {
    "police": ("#12283c", "#1b3b58", "#27547c"),
    "thief": ("#332c12", "#4d421a", "#6f5f24"),
}


def trail_fills(frame) -> dict:
    """Recency-shaded wash over the cells each side is recorded as having occupied."""
    fills: dict = {}
    for role, cells in (frame.get("trail") or {}).items():
        shades = TRAIL.get(role)
        if not shades:
            continue
        for position, cell in enumerate(cells):
            age = len(cells) - position
            fills[tuple(cell)] = shades[0] if age > 8 else shades[1] if age > 3 else shades[2]
    return fills


def wrap(text: str, width: int) -> list[str]:
    """Naive word wrap; the info panel is a fixed-width Tk label, not a text widget."""
    lines: list[str] = []
    line = ""
    for word in str(text).split():
        candidate = f"{line} {word}".strip()
        if len(candidate) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    return [*lines, line] if line else lines


def info_text(frame, sub_games: int) -> str:
    """The right-hand panel: where we are in the log and what the verifier concluded."""
    failed = frame["failed_steps"]
    return "\n".join(
        [
            f"Sub-game        {frame['sub_game']}  (of {sub_games} loaded)",
            f"Frame           {frame['index'] + 1} / {frame['total']}",
            f"Recorded step   {frame['step']}",
            f"Mover           {str(frame['mover']).upper()}",
            f"Action          {frame['action']}",
            "",
            "INTEGRITY",
            "Each record's SHA-256(nonce,",
            "payload) is recomputed and",
            "compared with its commitment.",
            f"Failed steps    {failed if failed else 'none'}",
            "",
            "HINT",
            *wrap(frame["hint"] or "-", 30),
        ]
    )
