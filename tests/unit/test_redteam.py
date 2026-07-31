"""P25 red-team / failure injection: every defined attack or failure must fail closed
and never yield an illegal move or a false-successful audit. This consolidates the
attack surface; deeper per-mechanism cases live in their own suites."""

import pytest

from thief_agent.domain.board import Board
from thief_agent.infra import gmail_report as gr
from thief_agent.peer.audit import run_audit
from thief_agent.peer.net_engine import PeerHalf
from thief_agent.report.confirm import make_confirmation, verify_mutual
from thief_agent.security.auth import AuthRegistry
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config import merge  # noqa: F401 - ensures module import safety
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy.base import Action
from thief_agent.strategy.production import make_gameplay_brain

CFG = validate(DEFAULT_GAME_CONFIG)


def test_expired_or_revoked_auth_rejected():
    reg = AuthRegistry({"good"}, {"revoked"})
    assert reg.check("good") is True
    assert reg.check("revoked") is False  # revoked beats allow-list
    assert reg.check("unknown") is False and reg.check(None) is False


def test_forged_final_agreement_fails_closed():
    police = DevTestSigner("p", key=b"kp")
    thief = DevTestSigner("t", key=b"kt")
    h = "a" * 64
    real = make_confirmation("p", h, police)
    forged = make_confirmation("t", h, police)  # police forges thief's confirmation
    assert verify_mutual(real, forged, police, thief)["passed"] is False


def test_forged_audit_records_fail_closed():
    from thief_agent.peer.turn_engine import run_sub_game

    res = run_sub_game(
        make_gameplay_brain("police", 1, baseline=True),
        make_gameplay_brain("thief", 2, baseline=True),
        {**CFG, "sub_game_number": 1},
        "g",
        DevTestSigner(),
        "0" * 40,
    )
    recs = [dict(r) for r in res["records"]]
    recs[-1] = {**recs[-1], "commit": "deadbeef"}  # tamper
    assert run_audit(recs, DevTestSigner())["passed"] is False


def test_inconsistent_or_malformed_barrier_rejected():
    thief = PeerHalf(
        "thief",
        CFG,
        make_gameplay_brain("thief", 1, baseline=True),
        "g",
        "0" * 40,
        DevTestSigner(),
        1,
    )
    assert thief._apply_barrier([999, 999]) is False  # out of bounds
    assert thief._apply_barrier("garbage") is False  # malformed
    assert thief._apply_barrier([1]) is False  # wrong shape


def test_thief_barrier_attempt_is_firewalled():
    class _Rogue:
        def decide(self, obs):
            return Action("BARRIER", "S")

        def hint(self, obs):
            return "x"

    thief = PeerHalf("thief", CFG, _Rogue(), "g", "0" * 40, DevTestSigner(), 1)
    assert thief.act()["barrier_placed"] is None  # thieves can never place barriers


def test_invalid_configuration_fails_closed():
    from thief_agent.exceptions import ConfigError

    bad = {**DEFAULT_GAME_CONFIG, "board_and_agents": {"grid_size": -1}}
    with pytest.raises((ConfigError, KeyError, ValueError, TypeError)):
        validate(bad)


def test_oversized_and_empty_attachment_rejected():
    with pytest.raises(ValueError):
        gr.validate_attachment(b"")
    with pytest.raises(ValueError):
        gr.validate_attachment(b"x" * (gr.MAX_REPORT_BYTES + 1))
    gr.validate_attachment(b'{"ok":1}')  # normal report passes


def test_malformed_report_never_sends():
    assert gr.should_send({"sub_games": []})[0] is False
    assert gr.should_send(None)[0] is False


def test_deadline_exhaustion_still_legal():
    from thief_agent.strategy.base import Observation
    from thief_agent.strategy.firewall import is_legal
    from thief_agent.strategy.rng import make_rng
    from thief_agent.strategy.thief_endgame import EndgameBrain

    brain = EndgameBrain(make_rng(1), max_depth=999, deadline_s=0.0)  # exhausted budget
    obs = Observation(
        role="thief",
        self_pos=(3, 3),
        board_size=7,
        barriers=frozenset(),
        scent={(0, 0): 0.9},
        step=30,
        max_barriers=14,
        barriers_used=0,
    )
    act = brain.decide(obs)
    assert is_legal(act, obs, Board(7), "thief")  # anytime search still returns a legal move
