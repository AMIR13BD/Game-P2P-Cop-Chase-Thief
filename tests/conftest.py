import pytest

from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.shared.gitinfo import current_commit


@pytest.fixture
def cfg():
    return validate(DEFAULT_GAME_CONFIG)


@pytest.fixture
def signer():
    return DevTestSigner()


@pytest.fixture
def commit():
    return current_commit(default="0" * 40)
