"""Fail-closed validation of the configured move set. Diagonals are always illegal."""

from ..constants import DIAGONALS, LEGAL_TOKENS
from ..exceptions import ConfigError


def validate_move_set(move_set: object) -> tuple[str, ...]:
    """Return the canonical legal token tuple, or raise ConfigError (fail closed).

    Accepts only exactly {N, S, E, W, STAY}. Missing/empty/non-list/diagonal/
    unknown tokens all raise rather than silently falling back to any default.
    """
    if not move_set or not isinstance(move_set, (list, tuple)):
        raise ConfigError("move_set missing or malformed; refusing to guess (fail closed)")
    tokens = [str(t).strip().upper() for t in move_set]
    for tok in tokens:
        if tok in DIAGONALS:
            raise ConfigError(f"diagonal move '{tok}' is illegal")
        if tok not in LEGAL_TOKENS:
            raise ConfigError(f"unsupported move token '{tok}'")
    if set(tokens) != set(LEGAL_TOKENS):
        raise ConfigError("move_set must be exactly N, S, E, W, STAY")
    return LEGAL_TOKENS
