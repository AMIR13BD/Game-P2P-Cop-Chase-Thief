import pytest

from thief_agent.exceptions import ArtifactError
from thief_agent.report import schemas


def test_unknown_kind_rejected():
    with pytest.raises(ArtifactError):
        schemas.validate("bogus", {})


def test_non_object_rejected():
    with pytest.raises(ArtifactError):
        schemas.validate("result", ["not", "a", "dict"])


@pytest.mark.parametrize("kind", list(schemas.REQUIRED))
def test_missing_required_field_rejected(kind):
    obj = {k: {} for k in schemas.REQUIRED[kind]}
    del obj[schemas.REQUIRED[kind][0]]
    with pytest.raises(ArtifactError):
        schemas.validate(kind, obj)


def test_log_malformed_summary_rejected():
    obj = {k: {} for k in schemas.REQUIRED["log"]}
    obj["records"] = "notlist"
    with pytest.raises(ArtifactError):
        schemas.validate("log", obj)
