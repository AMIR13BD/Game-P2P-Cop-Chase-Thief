"""Local post-game audit: recompute every commitment and detect tampering."""

from ..domain.crypto import audit_records


def run_audit(records: list[dict]) -> dict:
    """Return {'passed', 'verified_steps', 'failed_steps'} over sealed records."""
    plain = [{"payload": r["payload"], "nonce": r["nonce"], "commit": r["commit"]} for r in records]
    return audit_records(plain)
