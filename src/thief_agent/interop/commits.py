"""Where a peer's per-sub-game runtime commit SHA legitimately comes from (reporting only).

Book ch.5.5 (Step-0 box) and App. E rule 53: each side declares the 40-hex GitHub commit its
code ran on for THAT sub-game, and ch.9 requires that id in the emailed result. We only ever
read it from material the peer itself signed/sent — its negotiated identity (or the greeting
that carried it), or the Step-0 ``system_spec`` record it reveals in that sub-game's audit —
and we NEVER synthesise, guess or carry a value across sub-games. A value that is not exactly
40 hex characters is treated as absent ("") rather than reported.
"""

import re

_HEX40 = re.compile(r"[0-9a-fA-F]{40}")
# The spellings a peer may use for the same declared value. ``commit`` alone is deliberately
# NOT accepted: on the wire that name belongs to the 64-hex commit-reveal digest.
_COMMIT_KEYS = ("github_commit", "git_commit_hash", "commit_hash")


def hex40(value) -> str:
    """The value iff it is exactly 40 hex characters, else "" (never a partial match)."""
    text = str(value or "").strip()
    return text if _HEX40.fullmatch(text) else ""


def from_identity(*sources) -> str:
    """First 40-hex commit declared in any of the given dicts (identity, raw greeting, ...).

    Sources are scanned in the order given, and inside each source the known key spellings in
    order, so an explicit ``github_commit`` wins over an alias. A peer that nests the value in
    ``identity`` and a peer that puts it beside it are both read correctly."""
    for source in sources:
        if not isinstance(source, dict):
            continue
        for key in _COMMIT_KEYS:
            found = hex40(source.get(key))
            if found:
                return found
    return ""


def from_records(records) -> str:
    """The commit revealed in the peer's Step-0 ``system_spec`` record for this sub-game.

    This is the book's own binding (ch.5.5): the commit rides in the signed Step-0 payload the
    peer reveals during the end-of-sub-game audit, so it is per sub-game by construction. Used
    only as a fallback when the peer's identity carried no commit."""
    if not isinstance(records, list):
        return ""
    for record in records:
        payload = record.get("payload") if isinstance(record, dict) else None
        if not isinstance(payload, dict):
            continue
        if payload.get("step") == 0 or payload.get("type") == "system_spec":
            found = from_identity(payload)
            if found:
                return found
    return ""
