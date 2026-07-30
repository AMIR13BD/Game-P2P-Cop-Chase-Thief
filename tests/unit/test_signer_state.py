import pytest

from thief_agent.exceptions import IllegalTransitionError
from thief_agent.peer import state_machine as states
from thief_agent.security.signer import DevTestSigner, OfficialSigner


def test_devtest_signer_marks_output():
    sig = DevTestSigner().sign({"a": 1})
    assert sig.startswith("devtest:")


def test_official_signer_blocked_external():
    with pytest.raises(RuntimeError, match="BLOCKED-EXTERNAL"):
        OfficialSigner().sign({"a": 1})


def test_legal_transition_path():
    sm = states.StateMachine()
    for st in (
        states.CONFIG,
        states.NEGOTIATION,
        states.STEP0,
        states.READY,
        states.COMMIT,
        states.ACK,
        states.REVEAL,
        states.MOVE,
    ):
        sm.to(st)
    assert sm.state == states.MOVE


def test_illegal_transition_raises():
    sm = states.StateMachine()
    with pytest.raises(IllegalTransitionError):
        sm.to(states.MOVE)


def test_technical_loss_from_anywhere():
    sm = states.StateMachine()
    sm.to(states.CONFIG)
    assert sm.technical_loss() == states.TECH_LOSS
