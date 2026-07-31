"""Technical-loss result and a guarded runner for defined failure modes.

Defined failures (config/protocol/crypto/illegal-transition) map to a deterministic
0/0 technical outcome with preserved diagnostics. Unexpected programmer errors are
NOT swallowed."""

from ..exceptions import ConfigError, CryptoError, IllegalTransitionError


def technical_result(reason: str, evidence: dict | None = None) -> dict:
    return {
        "outcome": "technical",
        "police_score": 0,
        "thief_score": 0,
        "steps": 0,
        "records": [],
        "trajectory": [],
        "illegal": 0,
        "diagonal": 0,
        "reason": reason,
        "evidence": evidence or {},
    }


def safe_play(fn):
    """Run fn(); map defined failures to a technical result, re-raise anything else."""
    try:
        return fn()
    except (ConfigError, CryptoError, IllegalTransitionError) as exc:
        return technical_result(f"{type(exc).__name__}: {exc}")
