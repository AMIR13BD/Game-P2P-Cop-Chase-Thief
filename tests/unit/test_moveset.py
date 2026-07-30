import pytest

from thief_agent.domain.moveset import validate_move_set
from thief_agent.exceptions import ConfigError


def test_exact_legal_set_ok():
    assert validate_move_set(["N", "S", "E", "W", "STAY"]) == ("N", "S", "E", "W", "STAY")


@pytest.mark.parametrize(
    "bad", [None, [], "NSEW", ["N", "S", "E", "W"], ["N", "S", "E", "W", "STAY", "X"]]
)
def test_malformed_or_incomplete_failclosed(bad):
    with pytest.raises(ConfigError):
        validate_move_set(bad)


@pytest.mark.parametrize("d", ["NE", "NW", "SE", "SW"])
def test_diagonals_rejected(d):
    with pytest.raises(ConfigError):
        validate_move_set(["N", "S", "E", "W", "STAY", d])
