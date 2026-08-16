"""Replay-viewer panel helpers: trail recency shading and the info-panel text.

Split from test_gui_tk_layer.py to keep both files inside the 150-line limit."""

from thief_agent.gui.replay_model import ReplayModel
from thief_agent.gui.replay_panel import TRAIL, info_text, trail_fills
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.tamper_gen import tamper_commit
from thief_agent.strategy.production import make_gameplay_brain

CFG = validate(DEFAULT_GAME_CONFIG)


def _records(seed=1):
    return run_sub_game(
        make_gameplay_brain("police", seed, baseline=True),
        make_gameplay_brain("thief", seed + 5, baseline=True),
        {**CFG, "sub_game_number": 1},
        "opp",
        DevTestSigner(),
        "0" * 40,
    )["records"]


def test_trail_shading_is_recency_ordered():
    frame = {"trail": {"thief": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]}}
    fills = trail_fills(frame)
    assert fills[(0, 4)] == TRAIL["thief"][2]  # newest cell is the brightest shade
    assert fills[(0, 0)] == TRAIL["thief"][1]
    assert set(fills) == {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)}


def test_info_panel_reports_the_verifier_not_a_literal():
    model = ReplayModel(_records(), CFG["grid_size"])
    text = info_text(model.current(), 6)
    assert "Failed steps    none" in text and "SHA-256" in text
    bad = ReplayModel(tamper_commit(_records(), step=1), CFG["grid_size"])
    assert "Failed steps    [1" in info_text(bad.current(), 6)  # both roles' step-1 records


def test_replay_model_exposes_trail_for_both_roles():
    model = ReplayModel(_records(), CFG["grid_size"])
    model.go(model.total - 1)
    trail = model.current()["trail"]
    assert trail["police"] and trail["thief"]
