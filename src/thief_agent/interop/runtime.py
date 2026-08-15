"""One sub-game over the pushed-turn wire: thief-first, exactly-once processing, an own
turn-deadline, then the mutual end-of-game audit (transport/servers reused across sub-games)."""

import time

from .delivery import EquivocationError, Inbox, ProtocolViolationError
from .engine import IncomingOutcome, SubEngine, _now_iso
from .runtime_audit import AuditExchangeMixin
from .wire import TurnMessage


class SubGameRuntime(AuditExchangeMixin):
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
        # The peer's Step-0 commit as revealed in THIS sub-game's audit (book ch.5.5) —
        # reporting-only, and only a fallback when its identity declared no commit.
        self.peer_step0_commit = ""

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
            # Book App. E rule 54: report the tokens actually consumed in this sub-game (0 for
            # template/deterministic play), never a placeholder.
            "tokens_total": self.engine.tokens_used,
            "peer_github_commit_step0": self.peer_step0_commit,
        }
