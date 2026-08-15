"""A ``caught`` claim stops gameplay and enters the mutual final audit (records + nonce
exchange), then finishes. Exercises only the interop runtime's control flow via a stub
engine plus the real police engine's caught semantics — no strategy/gameplay code is
touched or changed (STEP 6 is verify-only).
"""

import time

from thief_agent.domain.crypto import seal
from thief_agent.interop import DEFAULT_GROUP_ID
from thief_agent.interop.delivery import Inbox
from thief_agent.interop.engine import IncomingOutcome, SubEngine
from thief_agent.interop.runtime import SubGameRuntime
from thief_agent.interop.terms import default_terms
from thief_agent.interop.wire import AuditPayload, TurnMessage


class _FakeTransport:
    """Records what the runtime pushes; feeds one opponent turn then the peer's audit."""

    def __init__(self, incoming_turn: dict, peer_audit: dict):
        self._incoming = [incoming_turn]
        self._peer_audit = peer_audit
        self.turns_sent: list = []
        self.audit_sent: dict | None = None
        self.audit_polled = False

    def send_turn(self, message):
        self.turns_sent.append(message)

    def poll_turn(self, timeout):
        return self._incoming.pop(0) if self._incoming else None

    def send_audit(self, payload):
        self.audit_sent = payload

    def poll_audit(self, timeout):
        self.audit_polled = True
        return self._peer_audit


class _StubEngine:
    """Stands in for SubEngine so we exercise ONLY the runtime's caught -> audit control
    flow. ``take_turn`` yields the opening move; ``concede`` yields the caught HOLD."""

    def __init__(self, role, outcome, records, concession):
        self.role = role
        self._outcome = outcome
        self.records = records
        self.step = len(records)
        self.tokens_used = 0  # deterministic stub: no model, so no tokens to report
        self._opening = TurnMessage(step=1, sender=role, commit="open", hint="")
        self._concession = concession

    def take_turn(self):
        return self._opening

    def concede(self):
        return self._concession

    def receive(self, msg):
        return self._outcome


def _sealed_step(step: int) -> tuple[dict, str]:
    payload = {"step": step, "sender": "police"}
    s = seal(payload)
    return {"payload": payload, "nonce": s["nonce"], "commit": s["commit"]}, s["commit"]


def _make_runtime(role, outcome, incoming_turn, peer_records, transport_records):
    rt = object.__new__(SubGameRuntime)  # skip heavy engine/brain construction
    rt.role = role
    rt.n = 1
    rt.terms = default_terms(max_steps=10)
    rt.inbox = Inbox(window=4)
    rt._listen = lambda event: None
    rt.result = None
    rt.started_at = "t0"
    rt._t0 = time.monotonic()
    concession = TurnMessage(
        step=2,
        sender=role,
        commit="conc",
        hint="",
        claim_response={"claim": [3, 3], "caught": True},
    )
    rt.engine = _StubEngine(role, outcome, transport_records, concession)
    peer_audit = AuditPayload(sender="opp", records=peer_records, result_claim="capture").to_wire()
    rt.transport = _FakeTransport(incoming_turn, peer_audit)
    return rt


def test_caught_true_stops_play_and_enters_final_audit_as_thief():
    rec1, c1 = _sealed_step(1)  # binds the incoming step-1 commit to a verifiable reveal
    incoming = TurnMessage(step=1, sender="police", commit=c1, hint="", capture_claim=[3, 3])
    rt = _make_runtime(
        role="thief",
        outcome=IncomingOutcome(i_am_caught=True),
        incoming_turn=incoming.to_wire(),
        peer_records=[rec1],
        transport_records=[rec1],
    )
    summary = rt.run(turn_timeout=2.0, poll=0.01)

    # gameplay stopped on the capture, and the concession carrying caught=True was sent
    assert summary["result"] == "capture"
    assert summary["winner"] == "police"
    assert rt.transport.turns_sent[-1]["claim_response"] == {"claim": [3, 3], "caught": True}
    # the mutual final audit was entered and completed (records + nonce exchange verified)
    assert rt.transport.audit_sent is not None and rt.transport.audit_polled is True
    assert summary["audit"]["skipped"] is False
    assert summary["audit"]["log_verified"] is True


def test_caught_true_ends_and_audits_as_police():
    rec1, c1 = _sealed_step(1)
    incoming = TurnMessage(
        step=1, sender="thief", commit=c1, hint="", claim_response={"claim": [3, 3], "caught": True}
    )
    rt = _make_runtime(
        role="police",
        outcome=IncomingOutcome(i_won=True),
        incoming_turn=incoming.to_wire(),
        peer_records=[rec1],
        transport_records=[rec1],
    )
    summary = rt.run(turn_timeout=2.0, poll=0.01)

    assert summary["result"] == "capture" and summary["winner"] == "police"
    assert rt.transport.audit_sent is not None and rt.transport.audit_polled is True
    assert summary["audit"]["log_verified"] is True


def test_real_police_engine_marks_win_on_caught_claim(commit):
    """The engine (unchanged) turns an opponent's caught concession into our capture win."""
    eng = SubEngine("police", default_terms(max_steps=10), DEFAULT_GROUP_ID, commit, 1)
    msg = TurnMessage(
        step=1,
        sender="thief",
        commit="x",
        hint="",
        claim_response={"claim": [3, 3], "caught": True},
    )
    assert eng.receive(msg).i_won is True
