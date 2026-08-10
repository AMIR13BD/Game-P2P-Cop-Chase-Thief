"""One sub-game over the pushed-turn wire: thief-first, exactly-once processing, an
own turn-deadline, then the mutual end-of-game audit. The transport/servers are built
once by the series and reused; a fresh runtime (and brain/board/commit-chain) is built
per sub-game.
"""

import time

from ..domain.crypto import audit_records
from .delivery import EquivocationError, Inbox, ProtocolViolationError
from .engine import IncomingOutcome, SubEngine, _now_iso
from .wire import AuditPayload, TurnMessage


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
        self.terms = terms
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
        """Integrity (re-hash with our serializer) AND binding (revealed == received in play)."""
        res = audit_records(records)
        failed = list(res["failed_steps"])
        by_step = {int(r["payload"].get("step", -1)): r for r in records}
        for step, commit in self.inbox.played.items():
            rec = by_step.get(int(step))
            if rec is None or rec.get("commit") != commit:
                failed.append(int(step))
        passed = not failed
        return {
            "passed": passed,
            "log_verified": passed,
            "tampered": not passed,
            "verified_steps": max(0, len(records) - len(set(failed))),
            "failed_steps": sorted(set(failed)),
            "skipped": False,
        }

    def _exchange_audit(self, outcome: str, turn_timeout: float) -> dict:
        mine = AuditPayload(sender=self.role, records=self.engine.records, result_claim=outcome)
        self.transport.send_audit(mine.to_wire())
        theirs = self.transport.poll_audit(turn_timeout)
        if theirs is None:
            return {
                "passed": False,
                "log_verified": False,
                "tampered": False,
                "verified_steps": 0,
                "failed_steps": [],
                "skipped": True,
            }
        return self._verify_theirs(AuditPayload.from_wire(theirs).records)

    def _drain_turns(self) -> None:
        """Discard any straggler/duplicate turns of THIS sub-game so a fresh next-sub-game
        inbox (next_step=1) never meets a stale high step. The next sub-game's turns are
        not sent until after its own handshake, so this cannot drop a live message."""
        while self.transport.poll_turn(0.0) is not None:
            pass

    def _finish(self, turn_timeout: float) -> dict:
        outcome, winner = self.result
        audit = (
            {
                "passed": False,
                "log_verified": False,
                "tampered": False,
                "verified_steps": 0,
                "failed_steps": [],
                "skipped": True,
            }
            if outcome == "timeout"
            else self._exchange_audit(outcome, turn_timeout)
        )
        self._drain_turns()
        # Survival length = threshold (max_steps), identical for both peers (not our turn count).
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
