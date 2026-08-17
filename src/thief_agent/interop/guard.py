"""The trust boundary for the opponent's IDENTITY, and containment for the paths it names.

The peer's ``group_id`` arrives unauthenticated. The terms signature (SPEC §4) covers the
agreed terms and the signer's nonce — it does NOT cover the group name, so a verifying
signature says nothing about it. That name then reaches ``derive_game_ids`` and becomes
the artifact filename base, which is how an unchecked value walks into
``out_dir / f"declaration_{game_id}.json"`` and out of the output directory entirely.

Two rules follow, and the second is the one that is easy to get wrong:

* **Refuse, never rewrite.** A hostile identity is rejected on the record. Silently
  sanitising it would file a counted match under a name its owner never used, and the
  join between the two teams' reports is by exactly that name.
* **Check containment separately anyway.** Identity validation and path containment are
  independent defences on purpose: the validator is a predicate about a string, the
  containment check is a fact about a resolved path. Either alone can be reasoned around;
  together, a bypass of one still lands inside the output directory.
"""

from pathlib import Path

from ..exceptions import ConfigError

MAX_GROUP_CHARS = 64
# Path separators and the NUL that truncates a filename in the C layer beneath us.
_FORBIDDEN = ("/", "\\", "\x00")
# Windows drive prefixes ("C:") and the home shorthand are path-like, not group names.
_DRIVE_SUFFIX = ":"


def check_group_id(peer_group: object, our_group: str) -> str:
    """Return the peer's group id unchanged, or raise ``ConfigError`` naming the problem.

    Deliberately permissive about CONTENT — spaces, dots, digits, Hebrew and other
    non-ASCII team names are all legitimate, and refusing them would reject an honest
    opponent. It is only the handful of constructs that mean something to a filesystem
    that are refused.
    """
    if not isinstance(peer_group, str) or not peer_group.strip():
        raise ConfigError("greeting names no usable group_id (empty or not a string)")
    if len(peer_group) > MAX_GROUP_CHARS:
        raise ConfigError(f"peer group_id longer than {MAX_GROUP_CHARS} characters")
    if peer_group == our_group:
        raise ConfigError(
            f"peer declares OUR own group_id {our_group!r}: a pairing has two distinct "
            "groups, and one id for both collapses the per-group roles and scores"
        )
    for bad in _FORBIDDEN:
        if bad in peer_group:
            raise ConfigError(f"peer group_id contains {bad!r}, which names a path, not a group")
    if ".." in peer_group or peer_group.strip(".") == "":
        raise ConfigError("peer group_id contains a path-traversal segment ('..')")
    if peer_group.startswith("~") or peer_group[1:2] == _DRIVE_SUFFIX:
        raise ConfigError("peer group_id is path-like (home shorthand or drive prefix)")
    if any(ord(ch) < 32 for ch in peer_group):
        raise ConfigError("peer group_id contains control characters")
    return peer_group


def safe_child(base: Path, name: str) -> Path:
    """The path ``base / name``, proven to stay inside ``base``.

    Resolves both sides before comparing, so ``..`` segments, absolute names and symlinked
    output directories are all judged on where they actually land rather than on how they
    are spelled.
    """
    root = Path(base).resolve()
    if "\\" in name:  # inert on POSIX, a separator on Windows: refuse on both, identically
        raise ConfigError(f"refusing {name!r}: a backslash is a path separator on Windows")
    candidate = (root / name).resolve()
    if candidate != root and root not in candidate.parents:
        raise ConfigError(f"refusing to touch {name!r}: it resolves outside {root}")
    return candidate
