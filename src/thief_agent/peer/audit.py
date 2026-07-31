"""Local post-game audit: recompute commitments and verify Step-0 signature + git
field. Malformed/incomplete records fail closed (returned as failed steps), never
raising KeyError."""

import re

from ..domain.crypto import verify
from ..exceptions import CryptoError

GIT_RE = re.compile(r"^[0-9a-f]{7,40}$")


def _step_of(rec: object) -> int:
    if isinstance(rec, dict) and isinstance(rec.get("payload"), dict):
        val = rec["payload"].get("step", -1)
        return val if isinstance(val, int) else -1
    return -1


def _check(rec: dict, signer) -> None:
    payload, nonce, commit = rec["payload"], rec["nonce"], rec["commit"]
    verify(payload, nonce, commit)
    if payload.get("step") == 0:
        if not GIT_RE.match(str(payload.get("github_commit", ""))):
            raise CryptoError("Step-0 github_commit missing or malformed")
        if signer is not None and not signer.verify(payload, rec.get("signature", "")):
            raise CryptoError("Step-0 signature invalid")


def run_audit(records: list, signer=None) -> dict:
    failed: list[int] = []
    verified = 0
    for rec in records:
        try:
            _check(rec, signer)
            verified += 1
        except (KeyError, TypeError, CryptoError):
            failed.append(_step_of(rec))
    return {"passed": not failed, "verified_steps": verified, "failed_steps": failed}
