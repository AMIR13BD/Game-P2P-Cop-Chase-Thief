"""Total parsers for OPPONENT-CONTROLLED values, and the limits that bound them.

Everything here is adversarial input: it arrives over a public tunnel from a peer we do
not trust and cannot authenticate beyond the terms signature. So every function in this
module is TOTAL — it returns a value or ``None``/a default, and never raises. A parser
that raises on a hostile field hands the opponent a way to end our series with one
malformed message, which is a far cheaper win than playing.

Deliberately dependency-free (no domain, peer or interop imports) so both the wire layer
and the gameplay half can share it without an import cycle.

The limits are sized for the official 7x7 match with a wide margin: no legal message from
a conforming peer comes close to any of them.
"""

import math
import queue

# A turn is a commit, a <=15-word hint and at most one scent cell per board square: a
# couple of kilobytes. A quarter-megabyte is ~100x the largest legal message.
MAX_MESSAGE_BYTES = 262_144
# One sealed record per step plus step 0; 4x the step cap tolerates a peer that numbers
# half-turns rather than rounds and still refuses an unbounded reveal.
AUDIT_RECORDS_PER_STEP = 4
# Per-inbox backlog. A whole series is ~36 turns, 6 audits and 6 agreements.
MAX_QUEUED = 1024
MAX_HINT_CHARS = 4_096
# The transmitted field is bounded by the board; the default covers the standard 7x7.
DEFAULT_MAX_CELLS = 49
MAX_INTENSITY = 1.0

_HEX = frozenset("0123456789abcdef")


def as_step(value: object) -> int | None:
    """A non-negative step index, or None. A digit string is accepted and coerced — it is
    unambiguous, and refusing it would reject a peer we can read perfectly well."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def is_commit(value: object) -> bool:
    """Exactly 64 LOWERCASE hex characters. Commits are compared as strings, so case is a
    real divergence, and every conforming peer emits ``hexdigest()`` output."""
    return isinstance(value, str) and len(value) == 64 and set(value) <= _HEX


def as_text(value: object, limit: int = MAX_HINT_CHARS) -> str:
    """Free text (hint, timestamp). Absent or wrong-typed becomes empty; an empty
    timestamp is explicitly TOLERATED — some conforming peers send one."""
    return value[:limit] if isinstance(value, str) else ""


def as_finite(value: object) -> float | None:
    """A real, finite number. NaN and Infinity survive JSON but are not legal values, and
    a single NaN poisons a belief map for the rest of the sub-game."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def as_cell(value: object, size: int | None = None) -> tuple[int, int] | None:
    """A [row, col] pair of plain ints, optionally required to be on the board."""
    if isinstance(value, str) or not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    out: list[int] = []
    for part in value:
        if isinstance(part, bool) or not isinstance(part, int):
            return None
        if size is not None and not 0 <= part < size:
            return None
        out.append(part)
    return (out[0], out[1])


def _parse_key(key: object, size: int | None) -> tuple[int, int] | None:
    if not isinstance(key, str):
        return None
    parts = key.split(",")
    if len(parts) != 2:
        return None
    try:
        cell = (int(parts[0]), int(parts[1]))
    except ValueError:
        return None
    if size is not None and not (0 <= cell[0] < size and 0 <= cell[1] < size):
        return None
    return cell


def scent_cells(
    raw: object, size: int | None = None, limit: int = DEFAULT_MAX_CELLS
) -> dict[tuple[int, int], float]:
    """Parse a transmitted ``{"r,c": intensity}`` field into cells.

    A malformed key, a non-numeric or non-finite value, an off-board coordinate or an
    out-of-range intensity DROPS that cell — the rest of the message is still perfectly
    usable, and one bad cell must never cost a series. Once ``limit`` cells have been
    accepted the remainder is ignored, so a flooded grid cannot grow our state.
    """
    out: dict[tuple[int, int], float] = {}
    if not isinstance(raw, dict):
        return out
    for key, value in raw.items():
        if len(out) >= limit:
            break
        cell = _parse_key(key, size)
        if cell is None:
            continue
        number = as_finite(value)
        if number is None or not 0.0 <= number <= MAX_INTENSITY:
            continue
        out[cell] = number
    return out


def enqueue(inbox: "queue.Queue", message: object) -> bool:
    """Hand a message to an inbox without ever blocking the HTTP worker.

    A full inbox DROPS the arrival and reports it, rather than growing without bound or
    parking the request thread — a peer that floods us should cost itself a message, not
    our memory or our ability to answer anyone else.
    """
    try:
        inbox.put_nowait(message)
        return True
    except queue.Full:
        return False


def oversized(payload: object, limit: int = MAX_MESSAGE_BYTES) -> bool:
    """True when a message is too large to be a legal 7x7 turn. Measured on the encoded
    form, because that is what actually consumed the memory getting here."""
    try:
        return len(repr(payload)) > limit
    except Exception:  # noqa: BLE001 - a __repr__ that raises is itself a refusal
        return True
