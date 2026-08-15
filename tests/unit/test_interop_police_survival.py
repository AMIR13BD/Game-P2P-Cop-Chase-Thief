"""Police end-of-game lifecycle: at the signed 35-step threshold with no capture, our
Police self-concludes THIEF survival instead of stalling for a peer end message; an early
peer silence (before the threshold) remains a genuine timeout (never fabricated survival)."""

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


def _thief_turns(terms, n):
    """n valid thief turns with the survival end-signal STRIPPED (simulate a peer that
    reaches the threshold but never sends a recognizable end message)."""
    eng = SubEngine("thief", terms, "peer", "0" * 40, 1, seed=42)
    out = []
    for _ in range(n):
        w = eng.take_turn().to_wire()
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
