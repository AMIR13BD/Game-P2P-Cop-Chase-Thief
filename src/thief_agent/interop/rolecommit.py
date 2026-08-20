"""Per-ROLE runtime commit SHAs: which repository actually played THIS sub-game.

A pairing submits TWO repositories — a cop one and a thief one (App. E rule 49) — but a
series runs from ONE of them, so the launching repo's HEAD is the right SHA for only half
the sub-games. Book ch.5.5 / App. E rule 53 want the commit of the code that played, per
sub-game, so the roles must be declared separately and selected by the role we hold.

Reporting metadata only. It is read from material each side declares about ITSELF, it is
never inferred from the peer, and it cannot reach the consensus preimage (``CANON_SUB_KEYS``
excludes every commit field), so a series settles to byte-identical digests either way.

Wire shape, chosen to be readable by a peer that already parses the reference identity:

* the flat ``github_commit`` / ``git_commit_hash`` of the identity we send for a sub-game
  carries THAT sub-game's role SHA — the field every conforming peer already reads
  (``commits.from_identity``), so a peer needs no new code to record us correctly;
* an additive ``github_commits`` map ``{"cop": ..., "thief": ...}`` rides alongside for a
  peer (or a human reading the report) that wants both without replaying the handshake.

Absent per-role SHAs, every function here collapses to the pre-existing single-commit
behaviour and the identity object is returned unchanged, so the wire bytes are untouched.
"""

from .commits import hex40

COP = "cop"
THIEF = "thief"


def resolve(default: str, police: str = "", thief: str = "") -> dict:
    """The ``{cop, thief}`` commit map, each falling back to ``default`` when not supplied.

    ``default`` is the launching repository's HEAD, i.e. exactly what a run without the
    per-role flags used for both roles before this existed."""
    base = hex40(default)
    return {COP: hex40(police) or base, THIEF: hex40(thief) or base}


def key_for(role: str) -> str:
    """Map key for a wire role: the protocol says ``police``, the repo map says ``cop``."""
    return COP if role == "police" else THIEF


def for_role(identity: dict, role: str, default: str = "") -> str:
    """The SHA of the implementation that plays ``role``, or the identity's single commit."""
    declared = identity.get("github_commits")
    scoped = hex40(declared.get(key_for(role))) if isinstance(declared, dict) else ""
    return scoped or hex40(default) or hex40(identity.get("github_commit"))


def view(identity: dict, role: str, default: str = "") -> tuple[dict, str]:
    """``(the identity to declare as this role, that role's SHA)``.

    The SAME object is returned when the role's SHA is already the identity's flat commit,
    so a run that declared no per-role SHAs puts byte-identical bytes on the wire."""
    sha = for_role(identity, role, default)
    if not sha or sha == identity.get("github_commit"):
        return identity, sha
    scoped = dict(identity)
    scoped["github_commit"] = sha
    scoped["git_commit_hash"] = sha
    return scoped, sha
