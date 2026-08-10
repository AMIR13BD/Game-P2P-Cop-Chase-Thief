"""Move legality on the interop wire/audit. Per the HW PDF (v3.0.0), the move_set is
FIXED to N,S,E,W,STAY (Appendix F); STAY is the legal stay-in-place. The caught concession
must NOT emit an illegal token ('HOLD:-') and must NOT physically move — it seals a STAY and
delivers the truthful claim_response on the live wire. Reproduces the reported (5,6) capture.
"""

import json

import pytest

from thief_agent.domain.moveset import validate_move_set
from thief_agent.exceptions import ConfigError
from thief_agent.interop import DEFAULT_GROUP_ID
from thief_agent.interop.engine import SubEngine
from thief_agent.interop.terms import default_terms
from thief_agent.interop.wire import TurnMessage

PDF_MOVE_SET = ("N", "S", "E", "W", "STAY")


def test_config_move_set_is_exactly_pdf():
    assert validate_move_set(["N", "S", "E", "W", "STAY"]) == PDF_MOVE_SET


@pytest.mark.parametrize(
    "bad",
    [
        ["N", "S", "E", "W"],
        ["N", "S", "E", "W", "STAY", "HOLD"],
        ["N", "S", "E", "W", "NE", "STAY"],
        ["HOLD"],
    ],
)
def test_hold_and_diagonals_rejected_as_moves(bad):
    with pytest.raises(ConfigError):
        validate_move_set(bad)


def test_caught_concession_seals_stay_not_hold_and_no_physical_move(commit):
    """Reported capture: thief at its cell, cop claims it -> caught. Concession = STAY, no move."""
    eng = SubEngine("thief", default_terms(max_steps=12), DEFAULT_GROUP_ID, commit, 1)
    eng.take_turn()
    caught_pos = list(eng.half.pos)
    out = eng.receive(
        TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=caught_pos)
    )
    assert out.i_am_caught is True
    msg = eng.concede()
    rec = eng.half.records[-1]["payload"]
    # sealed terminal record: legal STAY token, position unchanged, NO illegal HOLD:-
    assert rec["move"] == "STAY"
    assert rec["move"] in PDF_MOVE_SET
    assert rec["state"].endswith(f"self={caught_pos}")
    assert list(eng.half.pos) == caught_pos  # no physical movement after capture
    # live wire carries the positive claim_response; no move mislabel on the wire
    assert msg.claim_response == {"claim": caught_pos, "caught": True}
    blob = json.dumps(msg.to_wire()) + json.dumps(eng.half.records[-1])
    assert "HOLD:-" not in blob  # never on wire or in audit record


def test_normal_stay_serializes_as_stay_token(commit):
    """A normal stay-in-place must serialize as the legal token 'STAY', not 'STAY:None'."""
    from thief_agent.domain.board import Board
    from thief_agent.peer.net_engine import PeerHalf

    class _Stay:
        def decide(self, obs):
            from thief_agent.strategy.base import Action

            return Action("STAY")

        def hint(self, obs):
            return "holding"

    ph = PeerHalf(
        "thief",
        {
            "grid_size": 7,
            "cop_start": [0, 0],
            "thief_start": [3, 3],
            "pheromone_decay": 0.1,
            "max_barriers": 14,
        },
        _Stay(),
        "g",
        commit,
        __import__("thief_agent.security.signer", fromlist=["DevTestSigner"]).DevTestSigner(),
        1,
    )
    out = ph.act()
    assert isinstance(ph.board, Board)
    assert ph.records[-1]["payload"]["move"] == "STAY"  # not "STAY:None"
    assert "STAY:None" not in json.dumps(out) + json.dumps(ph.records[-1])


def test_wrong_capture_claim_continues(commit):
    eng = SubEngine("thief", default_terms(max_steps=12), DEFAULT_GROUP_ID, commit, 1)
    eng.take_turn()
    p = eng.half.pos
    miss = [p[0], p[1] + 1]
    out = eng.receive(TurnMessage(step=1, sender="police", commit="x", hint="", capture_claim=miss))
    assert out.i_am_caught is False
    nxt = eng.take_turn().to_wire()  # gameplay continues; response transmitted
    assert nxt["claim_response"] == {"claim": miss, "caught": False}
    assert nxt["step"] > 1
