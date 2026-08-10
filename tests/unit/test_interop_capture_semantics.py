"""Capture requires a DECLARED Capture Claim + truthful caught=true (PDF §3.5, Table 2):
bare coordinate coincidence is NEVER capture. The claim/response are SEALED into the
signed record so the capture protocol is auditable from evidence — never inferred from
revealed positions. Covers regression scenarios 1, 2, 3 and 8.
"""

from thief_agent.domain.board import Board
from thief_agent.interop import DEFAULT_GROUP_ID
from thief_agent.interop.engine import SubEngine
from thief_agent.interop.terms import default_terms
from thief_agent.interop.wire import TurnMessage
from thief_agent.peer.net_engine import PeerHalf
from thief_agent.security.signer import DevTestSigner
from thief_agent.strategy.base import Action

CFG = {
    "grid_size": 7,
    "cop_start": [3, 3],
    "thief_start": [0, 0],
    "pheromone_decay": 0.1,
    "max_barriers": 14,
}


class _Stay:
    def decide(self, obs):
        return Action("STAY")

    def hint(self, obs):
        return ""


def test_coincidence_without_capture_claim_is_not_capture(commit):
    """Scenario 1: a Cop turn with NO Capture Claim never catches the thief — even on the
    same cell (which the thief cannot see); the game continues normally."""
    eng = SubEngine("thief", default_terms(max_steps=12), DEFAULT_GROUP_ID, commit, 1)
    eng.take_turn()
    out = eng.receive(TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=None))
    assert out.i_am_caught is False
    nxt = eng.take_turn()  # gameplay continues
    assert nxt.step > 1


def test_valid_capture_claim_captures_seals_response_and_holds(commit):
    """Scenario 2 (+8): Capture Claim on the thief's TRUE cell -> caught=true; the concession
    seals the truthful claim_response with a STAY (no physical move after capture)."""
    eng = SubEngine("thief", default_terms(max_steps=12), DEFAULT_GROUP_ID, commit, 1)
    eng.take_turn()
    caught_pos = list(eng.half.pos)
    out = eng.receive(
        TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=caught_pos)
    )
    assert out.i_am_caught is True
    msg = eng.concede()
    rec = eng.half.records[-1]["payload"]
    assert rec["move"] == "STAY"  # legal no-move token, never HOLD:-
    assert rec["claim_response"] == {"claim": caught_pos, "caught": True}  # SEALED evidence
    assert msg.claim_response == {"claim": caught_pos, "caught": True}  # and on the live wire
    assert list(eng.half.pos) == caught_pos  # no physical movement after capture


def test_wrong_capture_claim_continues_and_seals_false_response(commit):
    """Scenario 3 (+8): a claim at the WRONG cell -> caught=false; play continues and the
    honest negative response is preserved in the next signed record."""
    eng = SubEngine("thief", default_terms(max_steps=12), DEFAULT_GROUP_ID, commit, 1)
    eng.take_turn()
    p = eng.half.pos
    miss = [p[0], (p[1] + 2) % 7]  # a different, in-bounds cell
    out = eng.receive(TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=miss))
    assert out.i_am_caught is False
    nxt = eng.take_turn()
    assert nxt.step > 1  # gameplay continues
    assert nxt.claim_response == {"claim": miss, "caught": False}
    assert eng.half.records[-1]["payload"]["claim_response"] == {"claim": miss, "caught": False}


def test_cop_capture_claim_is_sealed_in_signed_record(commit):
    """Scenario 8: when the Cop actually issues a Capture Claim (its cell == belief peak),
    the claimed coordinate is SEALED into the Cop's own record — auditable from evidence."""
    ph = PeerHalf("police", CFG, _Stay(), "g", commit, DevTestSigner(), 1)
    ph.receive({"scent": {"3,3": 0.9}, "hint": "", "barrier_placed": None, "claim": None})
    out = ph.act()  # Cop stays at (3,3); belief peak (3,3) == own cell -> Capture Claim
    assert isinstance(ph.board, Board)
    assert out["claim"] == [3, 3]
    assert ph.records[-1]["payload"]["capture_claim"] == [3, 3]  # SEALED
