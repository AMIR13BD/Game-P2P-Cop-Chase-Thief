import pytest

from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


@pytest.fixture
def cfg():
    return validate(DEFAULT_GAME_CONFIG)


@pytest.fixture
def signer():
    return DevTestSigner()
