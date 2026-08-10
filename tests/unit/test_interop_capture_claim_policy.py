"""The Cop ALWAYS declares a Capture Claim for its own post-move cell — every turn, with NO
belief/scent gating (PDF §3.5 Table 2: the declaration is the capture; a miss is a free
caught=false). Thief semantics are unchanged. Covers regression scenarios A-I, incl. the exact
G1 [5,6] landing that the old belief-gated policy silently missed.
"""

from thief_agent.interop import DEFAULT_GROUP_ID
from thief_agent.interop.engine import SubEngine
from thief_agent.interop.scoring import score_for
from thief_agent.interop.terms import default_terms
from thief_agent.interop.wire import TurnMessage
from thief_agent.peer.net_engine import PeerHalf
from thief_agent.security.signer import DevTestSigner
from thief_agent.strategy.base import Action


def _cfg(cop=(3, 3), thief=(0, 0)):
    return {
        "grid_size": 7,
        "cop_start": list(cop),
        "thief_start": list(thief),
        "pheromone_decay": 0.1,
        "max_barriers": 14,
    }


class _Move:
    def __init__(self, direction):
        self._d = direction

    def decide(self, obs):
        return Action("MOVE", self._d)

    def hint(self, obs):
        return ""


class _Stay:
    def decide(self, obs):
        return Action("STAY")

    def hint(self, obs):
        return ""


def _cop(cop_start, brain, commit, scent=None):
    ph = PeerHalf("police", _cfg(cop=cop_start), brain, "g", commit, DevTestSigner(), 1)
    if scent is not None:
        ph.receive({"scent": scent, "hint": "", "barrier_placed": None, "claim": None})
    return ph


def test_move_to_empty_cell_claims_post_move_cell_and_thief_is_not_caught(commit):
    """Scenario A + E: Cop claims its landing cell; a Thief elsewhere returns caught=false."""
    out = _cop((5, 5), _Move("E"), commit).act()  # [5,5] -> [5,6]
    assert out["claim"] == [5, 6]  # A: post-move cell
    thief = SubEngine("thief", default_terms(max_steps=12), DEFAULT_GROUP_ID, commit, 1)
    thief.take_turn()  # thief's own step 1
    res = thief.receive(
        TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=[5, 6])
    )
    assert res.i_am_caught is False  # thief is not at [5,6]
    assert thief.take_turn().step > 1  # E: gameplay continues


def test_stay_turn_claims_current_cell(commit):
    """Scenario C: even on STAY the Cop declares a claim for its current cell."""
    ph = _cop((4, 2), _Stay(), commit)
    out = ph.act()
    assert list(ph.pos) == [4, 2]
    assert out["claim"] == [4, 2]
    assert ph.records[-1]["payload"]["capture_claim"] == [4, 2]  # F: sealed


def test_claim_is_ungated_by_scent_belief(commit):
    """Scenario I: the claim is the Cop's own cell REGARDLESS of where scent/belief peaks."""
    ph = _cop((1, 1), _Stay(), commit, scent={"6,6": 0.9})  # belief peak far from the cop
    out = ph.act()
    assert out["claim"] == [1, 1]  # still its own cell, not the belief peak [6,6]


def test_g1_5_6_regression_landing_becomes_capture(commit):
    """Scenario B + D + F: Cop lands on the Thief's [5,6], always claims [5,6]; the Thief there
    is caught, concedes with a sealed STAY (no escape), and capture scores 20/5."""
    cop_out = _cop((5, 5), _Move("E"), commit).act()  # [5,5] -> [5,6]
    assert cop_out["claim"] == [5, 6]

    thief = SubEngine("thief", default_terms(max_steps=35), DEFAULT_GROUP_ID, commit, 1)
    thief.half.pos = (5, 6)  # place the Thief on the co-located cell
    res = thief.receive(
        TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=cop_out["claim"])
    )
    assert res.i_am_caught is True  # B: caught by the landing claim
    msg = thief.concede()
    assert list(thief.half.pos) == [5, 6]  # D: no escape move after capture
    assert msg.claim_response == {"claim": [5, 6], "caught": True}
    assert thief.half.records[-1]["payload"]["claim_response"] == {
        "claim": [5, 6],
        "caught": True,
    }  # F
    assert (score_for("capture", "police"), score_for("capture", "thief")) == (20, 5)  # 20/5


def test_missing_claim_is_not_a_capture_even_on_coincidence(commit):
    """Scenario G: no capture_claim -> never a capture, even if positions would coincide. Only a
    declared claim matched to the Thief's true cell captures (never coordinate equality alone)."""
    thief = SubEngine("thief", default_terms(max_steps=12), DEFAULT_GROUP_ID, commit, 1)
    thief.take_turn()  # thief's own step 1
    thief.half.pos = (5, 6)
    res = thief.receive(
        TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=None)
    )
    assert res.i_am_caught is False  # coincidence without a claim is not capture
    assert thief.take_turn().step > 1
