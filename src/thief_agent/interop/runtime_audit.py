"""The end-of-game mutual audit for one sub-game: verifying the peer's revealed
records, exchanging audit envelopes, and the fail-closed 'no peer audit' verdict.

Split out of ``runtime.py`` purely to keep each module inside the repository's 150-line
ceiling. These are the SAME methods, moved verbatim onto a mixin that ``SubGameRuntime``
inherits, so attribute lookup, call order and every audit verdict are unchanged.
"""

import time

from ..domain.crypto import audit_records, commit_of
from . import commits
from .wire import AuditPayload

AUDIT_WAIT = 30.0  # cap the end-of-game audit wait: a responsive peer audits in <1s, so this
# never regresses a well-behaved peer, but a fully-silent peer can no longer re-introduce a
# ~turn_timeout stall after a self-concluded survival.


class AuditExchangeMixin:
    """Audit half of ``SubGameRuntime`` (see runtime.py for the turn loop)."""

    def _verify_theirs(self, records: list) -> dict:
        """Integrity (re-hash with our serializer) AND binding (revealed == received in play).

        Pass/fail semantics are UNCHANGED. On failure we additionally persist enough evidence
        (first failing step, expected vs received commit, mismatch reason, peer reveal records)
        to pin the exact cause offline — the records are the exchanged public transcript, so no
        secret material is added."""
        res = audit_records(records)
        failed = list(res["failed_steps"])
        by_step = {int(r["payload"].get("step", -1)): r for r in records}
        integrity_failed = set(res["failed_steps"])
        mismatches: list[dict] = []
        for r in records:  # reveal-hash: commit != H(payload,nonce)
            step = int(r.get("payload", {}).get("step", -1))
            if step in integrity_failed:
                try:
                    recomputed = commit_of(r["payload"], r.get("nonce", ""))
                except Exception:  # noqa: BLE001 - diagnostics must never raise
                    recomputed = None
                mismatches.append(
                    {
                        "step": step,
                        "reason": "reveal_hash",
                        "expected_commit": recomputed,
                        "received_commit": r.get("commit"),
                    }
                )
        for step, commit in self.inbox.played.items():  # binding: revealed == received in play
            rec = by_step.get(int(step))
            if rec is None:
                failed.append(int(step))
                mismatches.append(
                    {
                        "step": int(step),
                        "reason": "missing_reveal",
                        "expected_commit": commit,
                        "received_commit": None,
                    }
                )
            elif rec.get("commit") != commit:
                failed.append(int(step))
                mismatches.append(
                    {
                        "step": int(step),
                        "reason": "binding_received_in_play",
                        "expected_commit": commit,
                        "received_commit": rec.get("commit"),
                    }
                )
        passed = not failed
        audit = {
            "passed": passed,
            "log_verified": passed,
            "tampered": not passed,
            "verified_steps": max(0, len(records) - len(set(failed))),
            "failed_steps": sorted(set(failed)),
            "skipped": False,
        }
        if not passed:
            mismatches.sort(key=lambda m: m["step"])
            audit["tamper"] = {
                "first_failed_step": mismatches[0]["step"] if mismatches else None,
                "first_reason": mismatches[0]["reason"] if mismatches else None,
                "mismatches": mismatches,
                "peer_records": records,
            }
        return audit

    def _exchange_audit(self, outcome: str, turn_timeout: float) -> dict:
        # Our OUTGOING per-sub-game audit envelope is left byte-identical to the frozen baseline
        # (no sub_game_number emitted); this fix is receive-side only. See _poll_peer_audit.
        mine = AuditPayload(sender=self.role, records=self.engine.records, result_claim=outcome)
        self.transport.send_audit(mine.to_wire())
        peer = self._poll_peer_audit(min(turn_timeout, AUDIT_WAIT))
        if peer is None:
            return self._missing_audit(outcome)
        self.peer_step0_commit = commits.from_records(peer.records)  # reporting only
        # Keep the peer's result_claim: agreement needs BOTH to claim the SAME outcome.
        audit = self._verify_theirs(peer.records)
        audit["local_result_claim"] = outcome
        audit["peer_result_claim"] = peer.result_claim
        audit["result_agreed"] = peer.result_claim == outcome
        return audit

    def _poll_peer_audit(self, wait: float) -> "AuditPayload | None":
        """The peer's end-of-game audit FOR THIS sub-game. When the peer tags its envelope with
        an explicit ``sub_game_number`` we BUCKET by it: a straggler audit for a different
        sub-game (e.g. left in the shared inbox across a role swap) is skipped, never mis-filed
        onto this one. A peer that omits the tag (older/reference) is taken by arrival, exactly
        as before — backward compatible. Mirrors the straggler-skip in ``exchange_agreement``."""
        deadline = time.monotonic() + wait
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            theirs = self.transport.poll_audit(remaining)
            if theirs is None:
                return None
            peer = AuditPayload.from_wire(theirs)
            if peer.sub_game_number not in (None, self.n):
                continue  # a straggler audit for a different sub-game: skip, keep waiting
            return peer

    @staticmethod
    def _missing_audit(outcome: str) -> dict:  # no peer audit: unverifiable, not agreed
        return {
            "passed": False,
            "log_verified": False,
            "tampered": False,
            "verified_steps": 0,
            "failed_steps": [],
            "skipped": True,
            "local_result_claim": outcome,
            "peer_result_claim": None,
            "result_agreed": False,
        }

    def _drain_turns(self) -> None:
        """Discard stragglers/duplicates of THIS sub-game so the next sub-game's fresh inbox
        never meets a stale high step (its turns are sent only after its own handshake)."""
        while self.transport.poll_turn(0.0) is not None:
            pass
