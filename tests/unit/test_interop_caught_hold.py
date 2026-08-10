"""A caught thief must HOLD (not move) and deliver the honest claim_response, then the
sub-game ends — matching the reference send_final/MoveType.HOLD. Regression for the bug
where the caught concession executed another thief move (cop+thief same cell, game 'continued')."""

from thief_agent.interop import DEFAULT_GROUP_ID
from thief_agent.interop.engine import SubEngine
from thief_agent.interop.terms import default_terms
from thief_agent.interop.wire import TurnMessage


def test_caught_concession_holds_position_and_seals_claim_response(commit):
    eng = SubEngine("thief", default_terms(max_steps=10), DEFAULT_GROUP_ID, commit, 1)
    eng.take_turn()  # opening move -> thief is now at a sealed position
    caught_pos = list(eng.half.pos)
    step_before = eng.half.step

    # the cop claims our ACTUAL cell -> we are caught
    out = eng.receive(
        TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=caught_pos)
    )
    assert out.i_am_caught is True

    msg = eng.concede()
    # HOLD: the thief did NOT move off the caught cell
    assert list(eng.half.pos) == caught_pos
    # the concession is a real sealed HOLD record (no gameplay move)
    assert eng.half.records[-1]["payload"]["move"] == "STAY"  # legal move_set token, not HOLD:-
    assert eng.half.records[-1]["payload"]["state"].endswith(f"self={caught_pos}")
    assert eng.half.step == step_before + 1  # one final message, not a re-played move loop
    # honest claim_response is delivered on the concession
    assert msg.claim_response == {"claim": caught_pos, "caught": True}
    assert msg.capture_claim is None and msg.win_claim is None


def test_missed_claim_is_not_caught_and_thief_continues(commit):
    eng = SubEngine("thief", default_terms(max_steps=10), DEFAULT_GROUP_ID, commit, 1)
    eng.take_turn()
    elsewhere = [eng.half.pos[0], eng.half.pos[1] + 1]  # a cell that is NOT the thief
    out = eng.receive(
        TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=elsewhere)
    )
    assert out.i_am_caught is False  # a miss never marks caught
    assert eng.pending_response == {"claim": elsewhere, "caught": False}  # honest answer still made
