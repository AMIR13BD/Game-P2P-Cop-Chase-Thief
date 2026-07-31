"""P20 replay viewer: reconstruct frames from audited records, per-step crypto
verification (VERIFIED OK vs TAMPERED via deliberate fixtures), config-hash check,
malformed-log safe handling, and stepper bounds."""

from thief_agent.gui.replay_controls import status_line, step_controls
from thief_agent.gui.replay_data import (
    Frame,
    board_at,
    load_log,
    reconstruct,
    render_truth_board,
)
from thief_agent.gui.replay_verify import replay_status, verify_config_hash, verify_steps
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_hash import config_sha256
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.tamper_gen import tamper_commit, tamper_payload
from thief_agent.strategy.production import make_gameplay_brain

CFG = validate(DEFAULT_GAME_CONFIG)


def _sub_game(seed=1):
    return run_sub_game(
        make_gameplay_brain("police", seed, baseline=True),
        make_gameplay_brain("thief", seed + 5, baseline=True),
        {**CFG, "sub_game_number": 1},
        "opp",
        DevTestSigner(),
        "0" * 40,
    )


def test_reconstruct_produces_turn_frames():
    recs = _sub_game()["records"]
    frames = reconstruct(recs)
    assert frames and all(isinstance(f, Frame) for f in frames)
    assert all(f.step > 0 for f in frames)
    assert {f.role for f in frames} <= {"police", "thief"}


def test_perstep_verify_ok_then_tampered():
    recs = _sub_game()["records"]
    assert replay_status(recs)["verified"] is True
    assert status_line(replay_status(recs)) == "VERIFIED OK"
    bad = tamper_commit(recs, step=1)
    st = replay_status(bad)
    assert st["verified"] is False and 1 in st["failed_steps"]
    assert "TAMPERED" in status_line(st)
    # payload tampering is detected too, and the original is never mutated
    assert replay_status(tamper_payload(recs, step=1))["verified"] is False
    assert replay_status(recs)["verified"] is True


def test_verify_steps_shape():
    recs = _sub_game()["records"]
    steps = verify_steps(recs)
    assert steps and all(set(s) == {"step", "ok"} for s in steps)


def test_config_hash_verification():
    assert verify_config_hash(CFG, config_sha256(CFG)) is True
    assert verify_config_hash(CFG, "deadbeef") is False


def test_malformed_log_is_safe():
    assert reconstruct(None) == []
    assert reconstruct([{"no": "payload"}, 42, {"payload": "x"}]) == []
    assert load_log("/nonexistent/path.json") == []
    assert replay_status([{"bad": "rec"}])["verified"] is False


def test_board_at_and_truth_render():
    recs = _sub_game()["records"]
    frames = reconstruct(recs)
    pos = board_at(frames, len(frames) - 1)
    assert pos["police"] is not None and pos["thief"] is not None
    board = render_truth_board(CFG["grid_size"], pos["police"], pos["thief"], pos["barriers"])
    assert board.count("P") == 1 and board.count("T") == 1


def test_stepper_bounds():
    assert step_controls(-5, 6) == {"index": 0, "has_prev": False, "has_next": True, "total": 6}
    assert step_controls(99, 6) == {"index": 5, "has_prev": True, "has_next": False, "total": 6}
    assert step_controls(0, 0)["index"] == 0
