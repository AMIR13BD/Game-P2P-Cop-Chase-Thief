import copy

import pytest

from thief_agent.exceptions import IllegalTransitionError
from thief_agent.peer import state_machine as states
from thief_agent.peer.audit import run_audit
from thief_agent.peer.technical import safe_play, technical_result
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


def test_technical_result_is_zero_zero():
    r = technical_result("x")
    assert r["outcome"] == "technical" and r["police_score"] == 0 and r["thief_score"] == 0


def test_invalid_transition_maps_to_technical():
    def boom():
        return states.StateMachine().to(states.MOVE)  # illegal from STARTUP

    with pytest.raises(IllegalTransitionError):
        boom()
    assert safe_play(boom)["outcome"] == "technical"


def test_malformed_commitment_maps_to_technical():
    from thief_agent.domain.crypto import verify

    assert safe_play(lambda: verify({"a": 1}, "00" * 16, "0" * 64))["outcome"] == "technical"


def test_invalid_config_maps_to_technical():
    bad = copy.deepcopy(DEFAULT_GAME_CONFIG)
    del bad["scoring"]
    assert safe_play(lambda: validate(bad))["outcome"] == "technical"


def test_malformed_audit_record_no_crash():
    assert run_audit([{"nope": 1}], None)["passed"] is False


def test_programmer_error_not_swallowed():
    with pytest.raises(ZeroDivisionError):
        safe_play(lambda: 1 / 0)
