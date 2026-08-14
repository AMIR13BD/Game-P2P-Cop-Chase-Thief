"""One sub-game over the pushed-turn wire: thief-first, exactly-once processing, an own
turn-deadline, then the mutual end-of-game audit (transport/servers reused across sub-games)."""

import time

from ..domain.crypto import audit_records, commit_of
from .delivery import EquivocationError, Inbox, ProtocolViolationError
from .engine import IncomingOutcome, SubEngine, _now_iso
from .wire import AuditPayload, TurnMessage

AUDIT_WAIT = 30.0  # cap the end-of-game audit wait: a responsive peer audits in <1s, so this
# never regresses a well-behaved peer, but a fully-silent peer can no longer re-introduce a
# ~turn_timeout stall after a self-concluded survival.


class SubGameRuntime:
    """Runs one sub-game (police or thief) against a remote opponent."""

    def __init__(
        self,
        role: str,
        terms: dict,
        transport,
        group: str,
        github_commit: str,
        sub_game_number: int,
        seed: int = 1234,
        listener=None,
    ):
        self.engine = SubEngine(role, terms, group, github_commit, sub_game_number, seed)
        self.transport = transport
        self.inbox = Inbox(window=4)
        self.role = role
        self.n = sub_game_number
        self._listen = listener or (lambda event: None)
        self.result: tuple[str, str] | None = None  # (outcome, winner_role)
        self.started_at = _now_iso()
        self._t0 = time.monotonic()

    def run(self, turn_timeout: float = 180.0, poll: float = 0.3) -> dict:
        if self.role == "thief":
            self._take_turn()
        deadline = time.monotonic() + turn_timeout
        while self.result is None:
            incoming = self.transport.poll_turn(poll)
            if incoming is None:
                if time.monotonic() > deadline:
                    self.result = ("timeout", self.role)  # opponent went silent
                continue
            deadline = time.monotonic() + turn_timeout
            try:
                ready = self.inbox.offer(incoming)  # exactly-once, in step order
            except (EquivocationError, ProtocolViolationError):
                self.result = ("technical_loss", "-")  # classify, never crash the series
                break
            for raw in ready:
                self._process(TurnMessage.from_wire(raw))
                # Police self-concludes the SIGNED survival at the 35-step threshold rather than
                # waiting (up to turn_timeout) for the peer thief's end message. Fires ONLY at the
                # full threshold with no capture, so an early peer silence (e.g. step 30) still
                # yields a genuine timeout below — never a fabricated survival.
                if (
                    self.result is None
                    and self.role == "police"
                    and self.engine.step >= self.engine.threshold
                ):
                    self.result = ("survival", "thief")
                if self.result is not None:
                    break
        return self._finish(turn_timeout)

    def _take_turn(self) -> None:
        message = self.engine.take_turn()
        self.transport.send_turn(message.to_wire())
        self._listen({"type": "moved", "sub_game": self.n, "step": message.step})
        if message.win_claim:  # thief reached survival threshold
            self.result = ("survival", "thief")

    def _process(self, msg: TurnMessage) -> None:
        outcome: IncomingOutcome = self.engine.receive(msg)
        if outcome.i_won:
            self.result = ("capture", "police")
        elif outcome.opponent_won:
            self.result = ("survival", "thief")
        elif outcome.i_am_caught:  # thief: HOLD + honest claim_response (no move), then end
            self.transport.send_turn(self.engine.concede().to_wire())
            self.result = ("capture", "police")
        else:
            self._take_turn()

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
                    {"step": step, "reason": "reveal_hash",
                     "expected_commit": recomputed, "received_commit": r.get("commit")}
                )
        for step, commit in self.inbox.played.items():  # binding: revealed == received in play
            rec = by_step.get(int(step))
            if rec is None:
                failed.append(int(step))
                mismatches.append(
                    {"step": int(step), "reason": "missing_reveal",
                     "expected_commit": commit, "received_commit": None}
                )
            elif rec.get("commit") != commit:
                failed.append(int(step))
                mismatches.append(
                    {"step": int(step), "reason": "binding_received_in_play",
                     "expected_commit": commit, "received_commit": rec.get("commit")}
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
        mine = AuditPayload(sender=self.role, records=self.engine.records, result_claim=outcome)
        self.transport.send_audit(mine.to_wire())
        theirs = self.transport.poll_audit(min(turn_timeout, AUDIT_WAIT))
        if theirs is None:
            return self._missing_audit(outcome)
        peer = AuditPayload.from_wire(theirs)
        # Keep the peer's result_claim: agreement needs BOTH to claim the SAME outcome.
        audit = self._verify_theirs(peer.records)
        audit["local_result_claim"] = outcome
        audit["peer_result_claim"] = peer.result_claim
        audit["result_agreed"] = peer.result_claim == outcome
        return audit

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

    def _finish(self, turn_timeout: float) -> dict:
        outcome, winner = self.result
        if outcome == "timeout":
            audit = self._missing_audit(outcome)
        else:
            audit = self._exchange_audit(outcome, turn_timeout)
        self._drain_turns()
        # Survival length = threshold (max_steps) for BOTH peers, not our own turn count.
        steps = self.engine.threshold if outcome == "survival" else self.engine.step
        return {
            "sub_game_number": self.n,
            "role": self.role,
            "result": outcome,
            "winner": winner,
            "steps": steps,
            "records": self.engine.records,
            "audit": audit,
            "started_at": self.started_at,
            "duration_seconds": time.monotonic() - self._t0,
            "tokens_total": 0,
        }
