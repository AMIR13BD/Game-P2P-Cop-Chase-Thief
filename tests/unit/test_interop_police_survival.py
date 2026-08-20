"""Police end-of-game lifecycle: at the signed 35-step threshold with no capture, our
Police self-concludes THIEF survival instead of stalling for a peer end message; an early
peer silence (before the threshold) remains a genuine timeout (never fabricated survival).

Also pins the Kit's meaning of the reported ``steps``: the reference takes it straight from
``rt.state.step_number`` (peer/summary.py), i.e. OUR OWN sealed-action count. It is a
per-side number, not a shared one — the two peers legitimately report different values for
the same sub-game — so a police peer that is told the thief survived reports the 34 moves it
made, never the 35-step threshold the thief reached."""

from thief_agent.interop.engine import SubEngine
from thief_agent.interop.runtime import SubGameRuntime
from thief_agent.interop.terms import default_terms


class _Stub:
    """Feeds pre-built thief turns then goes silent; records nothing else it needs."""

    def __init__(self, msgs):
        self.msgs, self.i = list(msgs), 0

    def poll_turn(self, timeout):
        if self.i < len(self.msgs):
            m = self.msgs[self.i]
            self.i += 1
            return m
        return None

    def send_turn(self, m):
        pass

    def send_audit(self, p):
        pass

    def poll_audit(self, t):
        return None


def _thief_turns(terms, n, keep_win_claim=False):
    """n valid thief turns. By default the survival end-signal is STRIPPED (simulate a peer
    that reaches the threshold but never sends a recognizable end message); with
    ``keep_win_claim`` the peer announces its survival the way the reference does."""
    eng = SubEngine("thief", terms, "peer", "0" * 40, 1, seed=42)
    out = []
    for _ in range(n):
        w = eng.take_turn().to_wire()
        if not keep_win_claim:
            w.pop("win_claim", None)
        out.append(w)
    return out


def test_police_self_concludes_survival_at_threshold():
    terms = default_terms()
    rt = SubGameRuntime(
        "police",
        terms,
        _Stub(_thief_turns(terms, terms["max_steps"])),
        "amireman",
        "0" * 40,
        2,
        seed=7,
    )
    summ = rt.run(turn_timeout=1.0, poll=0.0)  # short: a broken fix would fall through to timeout
    assert summ["result"] == "survival"
    assert summ["winner"] == "thief"
    assert summ["steps"] == terms["max_steps"] == 35


def test_police_reports_its_own_move_count_when_the_thief_claims_survival():
    """The peer thief announces survival on ITS step 35; we answered 34 of its turns and
    never moved a 35th time, so the Kit's own-step_number rule reports 34."""
    terms = default_terms()
    turns = _thief_turns(terms, terms["max_steps"], keep_win_claim=True)
    rt = SubGameRuntime("police", terms, _Stub(turns), "amireman", "0" * 40, 2, seed=7)
    summ = rt.run(turn_timeout=1.0, poll=0.0)
    assert summ["result"] == "survival" and summ["winner"] == "thief"
    assert summ["steps"] == terms["max_steps"] - 1 == 34
    assert summ["steps"] == rt.engine.step  # our own counter, never the shared threshold


def test_police_early_peer_silence_is_timeout_not_survival():
    terms = default_terms()
    rt = SubGameRuntime(
        "police",
        terms,
        _Stub(_thief_turns(terms, 30)),  # silent at 30 < 35
        "amireman",
        "0" * 40,
        4,
        seed=7,
    )
    summ = rt.run(turn_timeout=0.4, poll=0.0)
    assert summ["result"] == "timeout"  # never fabricate survival before the signed threshold
