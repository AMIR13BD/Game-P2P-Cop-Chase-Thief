"""Per-step cryptographic verification and config-hash check for the replay viewer
(P20). Recomputes each record's commitment; any mismatch marks that step tampered."""

from ..domain.crypto import verify
from ..exceptions import CryptoError
from ..shared.config_hash import config_sha256


def verify_steps(records) -> list[dict]:
    """[{step, ok}] recomputing each record's SHA-256 commitment."""
    out: list[dict] = []
    for rec in records or []:
        step = rec.get("payload", {}).get("step") if isinstance(rec, dict) else None
        try:
            verify(rec["payload"], rec["nonce"], rec["commit"])
            ok = True
        except (KeyError, TypeError, CryptoError):
            ok = False
        out.append({"step": step, "ok": ok})
    return out


def replay_status(records) -> dict:
    """Overall replay integrity: verified flag + the list of failed steps."""
    steps = verify_steps(records)
    failed = [s["step"] for s in steps if not s["ok"]]
    return {"verified": not failed and bool(steps), "failed_steps": failed, "total": len(steps)}


def verify_config_hash(config: dict, expected: str) -> bool:
    """True iff the config's canonical SHA-256 matches the recorded config_sha256."""
    return config_sha256(config) == expected
