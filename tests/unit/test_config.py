import copy

import pytest

from thief_agent.exceptions import ConfigError
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


def _cfg():
    return copy.deepcopy(DEFAULT_GAME_CONFIG)


def test_valid_config_passes():
    flat = validate(DEFAULT_GAME_CONFIG)
    assert flat["grid_size"] == 7 and flat["num_agents"] == 2
    assert flat["sub_games"] == 6 and flat["num_games"] == 1  # series 6, num_games illustrative


def test_empty_map_area_defaults_new_york():
    c = _cfg()
    c["world"]["map_area"] = ""
    assert validate(c)["map_area"] == "New York"


def test_fixed_value_change_rejected():
    c = _cfg()
    c["scoring"]["capture_cop"] = 21
    with pytest.raises(ConfigError):
        validate(c)


def test_minimum_below_floor_rejected():
    c = _cfg()
    c["board_and_agents"]["grid_size"] = 5
    with pytest.raises(ConfigError):
        validate(c)
    c2 = _cfg()
    c2["rate_limiter_gatekeeper"]["requests_per_minute"] = 10
    with pytest.raises(ConfigError):
        validate(c2)


def test_minimum_raise_allowed():
    c = _cfg()
    c["board_and_agents"]["grid_size"] = 9
    c["movement_and_barriers"]["max_barriers"] = 20
    assert validate(c)["grid_size"] == 9


def test_diagonal_moveset_rejected():
    c = _cfg()
    c["movement_and_barriers"]["move_set"] = ["N", "S", "E", "W", "NE", "STAY"]
    with pytest.raises(ConfigError):
        validate(c)


def test_malformed_moveset_failclosed():
    c = _cfg()
    c["movement_and_barriers"]["move_set"] = []
    with pytest.raises(ConfigError):
        validate(c)
