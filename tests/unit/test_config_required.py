import copy

import pytest

from thief_agent.exceptions import ConfigError
from thief_agent.shared.config_spec import REQUIRED
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


@pytest.mark.parametrize("category", list(REQUIRED))
def test_missing_category_fails_closed(category):
    c = copy.deepcopy(DEFAULT_GAME_CONFIG)
    del c[category]
    with pytest.raises(ConfigError):
        validate(c)


@pytest.mark.parametrize("category", list(REQUIRED))
def test_missing_one_field_fails_closed(category):
    c = copy.deepcopy(DEFAULT_GAME_CONFIG)
    field = REQUIRED[category][0]
    del c[category][field]
    with pytest.raises(ConfigError):
        validate(c)


def test_unknown_field_rejected():
    c = copy.deepcopy(DEFAULT_GAME_CONFIG)
    c["scoring"]["bogus"] = 1
    with pytest.raises(ConfigError):
        validate(c)


def test_start_position_off_board_rejected():
    c = copy.deepcopy(DEFAULT_GAME_CONFIG)
    c["board_and_agents"]["thief_start"] = [7, 7]
    with pytest.raises(ConfigError):
        validate(c)
