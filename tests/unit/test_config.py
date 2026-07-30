import copy

import pytest

from thief_agent.exceptions import ConfigError
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


def test_valid_config_passes():
    flat = validate(DEFAULT_GAME_CONFIG)
    assert flat["grid_size"] == 7 and flat["num_agents"] == 2
    assert flat["sub_games"] == 6


def test_map_area_defaults_new_york():
    cfg = copy.deepcopy(DEFAULT_GAME_CONFIG)
    cfg["world"]["map_area"] = ""
    assert validate(cfg)["map_area"] == "New York"
    del cfg["world"]["map_area"]
    assert validate(cfg)["map_area"] == "New York"


def test_fixed_value_change_rejected():
    cfg = copy.deepcopy(DEFAULT_GAME_CONFIG)
    cfg["scoring"]["capture_cop"] = 21
    with pytest.raises(ConfigError):
        validate(cfg)


def test_minimum_below_floor_rejected():
    cfg = copy.deepcopy(DEFAULT_GAME_CONFIG)
    cfg["board_and_agents"]["grid_size"] = 5
    with pytest.raises(ConfigError):
        validate(cfg)
    cfg2 = copy.deepcopy(DEFAULT_GAME_CONFIG)
    cfg2["movement_and_barriers"]["max_barriers"] = 10
    with pytest.raises(ConfigError):
        validate(cfg2)


def test_minimum_raise_allowed():
    cfg = copy.deepcopy(DEFAULT_GAME_CONFIG)
    cfg["board_and_agents"]["grid_size"] = 9
    assert validate(cfg)["grid_size"] == 9


def test_diagonal_moveset_rejected():
    cfg = copy.deepcopy(DEFAULT_GAME_CONFIG)
    cfg["movement_and_barriers"]["move_set"] = ["N", "S", "E", "W", "NE", "STAY"]
    with pytest.raises(ConfigError):
        validate(cfg)


def test_malformed_moveset_failclosed():
    cfg = copy.deepcopy(DEFAULT_GAME_CONFIG)
    cfg["movement_and_barriers"]["move_set"] = []
    with pytest.raises(ConfigError):
        validate(cfg)
