"""Commit-reveal over SHA-256.

Canonical serialization and commit format are interoperable with the official
reference implementation (Game-P2P-Cop-Chase, (c) Dr. Yoram Segal / GTAI,
Educational-Use EULA). This module is an independent re-implementation of that
format, not a copy. See docs/REUSE-REGISTER.md.
"""

import hashlib
import json
import secrets
from typing import Any

from ..exceptions import CryptoError

NONCE_BYTES = 16


def canonical_json(payload: dict[str, Any]) -> str:
    """Key-order-independent, compact JSON so both peers hash identical bytes."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def commit_of(payload: dict[str, Any], nonce: str) -> str:
    return hashlib.sha256(f"{canonical_json(payload)}|{nonce}".encode()).hexdigest()


def fresh_nonce() -> str:
    return secrets.token_hex(NONCE_BYTES)


def seal(payload: dict[str, Any]) -> dict[str, str]:
    """Generate a fresh nonce and its commitment for a payload."""
    nonce = fresh_nonce()
    return {"nonce": nonce, "commit": commit_of(payload, nonce)}


def verify(payload: dict[str, Any], nonce: str, commit: str) -> None:
    actual = commit_of(payload, nonce)
    if not secrets.compare_digest(actual, commit):
        raise CryptoError(f"commit mismatch: expected {commit[:12]}..., got {actual[:12]}...")


def audit_records(records: list[dict]) -> dict:
    """Re-verify every {payload, nonce, commit}. Returns pass/verified/failed."""
    failed: list[int] = []
    for rec in records:
        try:
            verify(rec["payload"], rec["nonce"], rec["commit"])
        except CryptoError:
            failed.append(int(rec["payload"].get("step", -1)))
    return {
        "passed": not failed,
        "verified_steps": len(records) - len(failed),
        "failed_steps": failed,
    }
