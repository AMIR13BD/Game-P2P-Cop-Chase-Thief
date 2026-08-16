"""The Tk presentation layer's pure view-models (P20/P21 submission requirement).

Everything asserted here runs headlessly: the Tk widgets are a thin painter over these
dicts, so role perspective, heat mapping, banner state, stepper bounds and the
VERIFIED OK / TAMPERED verdict are all testable without a display."""

import pytest

from thief_agent.domain.board import Board
from thief_agent.gui import palette
from thief_agent.gui.evidence import cells_upto, observation_at, scents_upto
from thief_agent.gui.live_model import is_uniform, legend_rows, live_state
from thief_agent.gui.replay_data import reconstruct
from thief_agent.gui.replay_model import ReplayModel, series_verdict
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.tamper_gen import tamper_commit
from thief_agent.strategy.base import Observation
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


def _obs(role="police", scent=None):
    return Observation(
        role=role,
        self_pos=(0, 0),
        board_size=7,
        barriers=frozenset(),
        scent=scent if scent is not None else {(3, 3): 0.9},
        step=4,
        max_barriers=14,
        barriers_used=0,
    )


@pytest.mark.parametrize(("role", "opponent"), [("police", "thief"), ("thief", "police")])
def test_live_state_perspective_follows_the_observation(role, opponent):
    state = live_state(_obs(role))
    assert state["role"] == role and state["opponent"] == opponent


def test_live_state_heatmap_is_peaked_and_maps_to_colour():
    state = live_state(_obs(scent={(3, 3): 0.9}))
    assert state["peak"] == (3, 3) and state["peak_bucket"] == 9
    assert state["informative"] is True
    assert palette.heat_color(9) != palette.heat_color(0)


def test_empty_scent_is_flagged_uniform_not_silently_shown():
    state = live_state(_obs(scent={}))
    assert is_uniform(state["buckets"]) and state["informative"] is False


@pytest.mark.parametrize(
    ("state_name", "locked", "text"),
    [("MOVE", False, "YOUR TURN"), ("READY", False, "YOUR TURN"), ("COMMIT", True, "LOCKED")],
)
def test_turn_indicator_state_and_colour(state_name, locked, text):
    state = live_state(_obs(), state=state_name)
    assert state["locked"] is locked
    label, colour = palette.banner_style(state["locked"])
    assert label == text
    assert colour == (palette.LOCKED_GREY if locked else palette.TURN_GREEN)


def test_legend_reports_the_tracked_opponent():
    rows = dict(legend_rows(live_state(_obs("thief"))))
    assert rows["Role"] == "THIEF" and rows["Tracking"] == "POLICE"


def test_replay_model_stepper_respects_bounds():
    model = ReplayModel(_records(), CFG["grid_size"])
    assert model.current()["has_prev"] is False
    model.step_back()
    assert model.index == 0
    model.go(model.total + 50)
    assert model.index == model.total - 1 and model.current()["has_next"] is False
    model.step_back()
    assert model.index == model.total - 2


def test_replay_model_next_advances_the_board():
    model = ReplayModel(_records(), CFG["grid_size"])
    first = model.current()
    model.step_forward()
    assert model.current()["index"] == first["index"] + 1


def test_verified_replay_reports_verified_ok_green():
    model = ReplayModel(_records(), CFG["grid_size"])
    assert model.verified is True
    assert model.integrity_text() == "VERIFIED OK"
    assert palette.integrity_style(True)[0] == palette.VERIFIED_GREEN
    assert series_verdict([model])[0] is True


def test_tampered_replay_reports_tampered_red():
    model = ReplayModel(tamper_commit(_records(), step=1), CFG["grid_size"])
    assert model.verified is False
    assert model.integrity_text().startswith("TAMPERED")
    assert palette.integrity_style(False)[0] == palette.TAMPERED_RED
    assert series_verdict([model])[0] is False


def test_observation_from_evidence_is_role_correct_and_peaked():
    frames = reconstruct(_records())
    police, thief, _ = cells_upto(frames, len(frames) - 1)
    cop_view = observation_at(frames, len(frames) - 1, CFG, "police")
    thief_view = observation_at(frames, len(frames) - 1, CFG, "thief")
    assert cop_view.self_pos == police and thief_view.self_pos == thief
    assert cop_view.scent and thief_view.scent  # each sees the OTHER's emission field
    assert live_state(cop_view)["informative"] and live_state(thief_view)["informative"]


def test_evidence_scents_are_the_opponents_field_not_our_own():
    frames = reconstruct(_records())
    last = len(frames) - 1
    board = Board(CFG["grid_size"], set())
    police_scent, thief_scent = scents_upto(frames, last, board, CFG["pheromone_decay"])
    cop_view = observation_at(frames, last, CFG, "police")
    assert cop_view.scent == thief_scent and cop_view.scent != police_scent
