"""Public-safety filtering and audited credibility for free-language hints (P17).

A hint may be truthful, vague or deceptive, but it must NEVER carry coordinates, a
true position, or any nonce/secret/token/commit material. Credibility is computed
ONLY over audit-verified records, so unverified claims can never shape strategy."""

import re

from ..peer.audit import run_audit

DEFAULT_WORD_CAP = 15

# Any digit is forbidden: a public hint never needs a numeral, and every position /
# coordinate / row-col / index leak necessarily contains one. This is the strongest
# fail-closed reading of "no true position disclosure".
_DIGIT = re.compile(r"\d")
_HEXY = re.compile(r"\b[a-fA-F]{8,}\b")  # all-letter hex blobs (nonce/commit-like)
_BANNED = re.compile(r"\b(nonce|token|secret|commit|signature|seed|private|key)\b", re.I)
_DIRWORDS = {"north": (-1, 0), "south": (1, 0), "east": (0, 1), "west": (0, -1)}


def word_count(hint: str) -> int:
    return len(hint.split())


def is_within_cap(hint: str, cap: int = DEFAULT_WORD_CAP) -> bool:
    return word_count(hint) <= cap


def leaks_information(hint: str) -> bool:
    """True if the hint exposes any digit (coordinate/position/index) or secret material."""
    return bool(_DIGIT.search(hint) or _HEXY.search(hint) or _BANNED.search(hint))


def is_valid(hint, cap: int = DEFAULT_WORD_CAP) -> bool:
    return (
        isinstance(hint, str)
        and hint.strip() != ""
        and is_within_cap(hint, cap)
        and not leaks_information(hint)
    )


def sanitize(hint, cap: int = DEFAULT_WORD_CAP, default: str = "moving through the streets") -> str:
    """Return the hint unchanged if valid, else a safe generic default (fail-closed)."""
    return hint if is_valid(hint, cap) else default


def hint_direction(hint) -> tuple[int, int] | None:
    """Coarse movement bias a receiver can infer from a hint (or None)."""
    if not isinstance(hint, str):
        return None
    low = hint.lower()
    for word, delta in _DIRWORDS.items():
        if word in low:
            return delta
    return None


def credibility_from_records(records: list, signer=None) -> tuple[int, float]:
    """Audited-only hint honesty: (hints_checked, fraction declared truthful).

    Returns a neutral 0.5 when nothing is verifiable, so unproven hints are ignored."""
    if not run_audit(records, signer)["passed"]:
        return (0, 0.5)
    checked = consistent = 0
    for rec in records:
        p = rec.get("payload", {})
        if p.get("step", 0) == 0 or not p.get("hint"):
            continue
        checked += 1
        consistent += 1 if p.get("intent") == "truth" else 0
    return (checked, consistent / checked if checked else 0.5)
