"""Regression for the TEST22 friendly series against Orcai-MJ.

Our Cop captured on step 9 in sub-games 2/4/6 and the peer confirmed each one, yet we
recorded ``timeout``, sent no ``submit_audit``, and the peer's unread audits then
mis-associated onto 3/5 as false TAMPER. Cause: a peer whose sub-game has ended re-sends a
COPY of its last turn to carry the ``claim_response`` it owes (the reference
deliver_verdict convention); that copy repeats an already-played step+commit, so
exactly-once delivery absorbed the confirmed capture. These tests pin the fixed lifecycle.
"""

from thief_agent.interop.runtime import SubGameRuntime
from thief_agent.interop.terms import default_terms

TERMS = default_terms()


class _Transport:
    """Scripted peer: queues turn messages, records what we send."""

    def __init__(self, turns=()):
        self.turns, self.audits = list(turns), []
        self.sent_turns: list = []
        self.sent_audits: list = []

    def poll_turn(self, timeout):
        return self.turns.pop(0) if self.turns else None

    def poll_audit(self, timeout):
        return self.audits.pop(0) if self.audits else None

    def send_turn(self, msg):
        self.sent_turns.append(msg)

    def send_audit(self, payload):
        self.sent_audits.append(payload)


def _peer_turn(step, commit, sender="thief", **extra):
    msg = {
        "step": step,
        "sender": sender,
        "commit": commit,
        "hint": "",
        "smell_grid": {},
        "timestamp": "",
        "barrier_placed": None,
        "capture_claim": None,
        "claim_response": None,
        "win_claim": None,
    }
    msg.update(extra)
    return msg


def _pair(commit, sender="thief", **extra):
    """A turn, then the courtesy-flush COPY of it (same step, same commit)."""
    return [_peer_turn(1, commit, sender), _peer_turn(1, commit, sender, **extra)]


def _runtime(role, transport, n=1):
    return SubGameRuntime(role, TERMS, transport, "amireman", "0" * 40, n, seed=1234)


# ---------------------------------------------------------------- capture path
def test_capture_confirmed_on_absorbed_duplicate_is_not_a_timeout():
    """The TEST22 sub-game 2/4/6 shape: peer replays its last turn carrying caught=true."""
    commit = "a" * 64
    # the second entry is the courtesy flush: SAME step, SAME commit, owed answer attached
    tp = _Transport(_pair(commit, claim_response={"claim": [4, 5], "caught": True}))
    out = _runtime("police", tp).run(turn_timeout=0.5, poll=0.0)
    assert out["result"] == "capture"
    assert out["winner"] == "police"


def test_absorbed_duplicate_never_replays_the_move():
    """Exactly-once is NOT weakened: the duplicate must not drive another of our turns."""
    commit = "b" * 64
    tp = _Transport([_peer_turn(1, commit), _peer_turn(1, commit)])
    _runtime("police", tp).run(turn_timeout=0.4, poll=0.0)
    # step 1 applied once -> exactly one reply; the duplicate produced no second turn
    assert len(tp.sent_turns) == 1


def test_capture_sends_exactly_one_submit_audit():
    commit = "c" * 64
    tp = _Transport(_pair(commit, claim_response={"claim": [4, 5], "caught": True}))
    out = _runtime("police", tp).run(turn_timeout=0.5, poll=0.0)
    assert out["result"] == "capture"
    assert len(tp.sent_audits) == 1
    sent = tp.sent_audits[0]
    assert sent["sender"] == "police" and sent["result_claim"] == "capture"
    assert sent["records"], "our own records must be published for the peer to verify"


def test_a_false_claim_response_never_fabricates_a_capture():
    """caught=false must NOT end the sub-game as a capture."""
    tp = _Transport(_pair("d" * 64, claim_response={"claim": [4, 5], "caught": False}))
    assert _runtime("police", tp).run(turn_timeout=0.3, poll=0.0)["result"] == "timeout"


def test_thief_never_self_awards_a_capture_from_a_duplicate():
    """Only the Cop may conclude capture from claim_response.caught."""
    commit = "e" * 64
    tp = _Transport(_pair(commit, "police", claim_response={"claim": [0, 0], "caught": True}))
    out = _runtime("thief", tp).run(turn_timeout=0.3, poll=0.0)
    assert out["result"] != "capture"


def test_survival_win_claim_on_a_duplicate_is_honoured():
    commit = "f" * 64
    tp = _Transport(_pair(commit, win_claim={"type": "survival"}))
    out = _runtime("police", tp).run(turn_timeout=0.5, poll=0.0)
    assert out["result"] == "survival" and out["winner"] == "thief"


# ------------------------------------------------------------------ audit path
def test_timeout_still_publishes_our_audit():
    """A silent peer keeps the timeout verdict, but our records are still sent."""
    tp = _Transport([])
    out = _runtime("police", tp).run(turn_timeout=0.2, poll=0.0)
    assert out["result"] == "timeout"
    assert len(tp.sent_audits) == 1, "our half of the transcript must always be published"
    assert out["audit"]["skipped"] is True  # peer sent nothing back: unverifiable, not agreed
    assert out["audit"]["result_agreed"] is False


def test_audit_is_sent_once_per_sub_game_for_every_outcome():
    for role, turns in (("police", []), ("thief", [])):
        tp = _Transport(turns)
        _runtime(role, tp).run(turn_timeout=0.2, poll=0.0)
        assert len(tp.sent_audits) == 1
