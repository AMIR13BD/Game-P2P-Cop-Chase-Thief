"""Every artifact path is proven to land inside the output directory before it is written.

Independent of the identity guard on purpose: that one is a predicate about a string, this
one is a fact about a resolved path. A bypass of either still has to get past the other,
and the write is the step that cannot be undone.
"""

import pytest

from thief_agent.exceptions import ConfigError
from thief_agent.interop.artifacts_io import write_doc
from thief_agent.interop.guard import safe_child

ESCAPES = [
    "declaration_../../../../pwned.json",
    "../pwned.json",
    "..\\pwned.json",
    "result_../../../x.json",
    "/tmp/pwned.json",
    "sub/../../../pwned.json",
]

CONTAINED = [
    "declaration_amireman-vs-uoh-ay26.json",
    "config_G020_g01.json",
    "log_amireman-vs-uoh-ay26_g06.json",
    "result_G020.json",
]


@pytest.mark.parametrize("name", ESCAPES)
def test_a_name_that_escapes_the_output_directory_is_refused(tmp_path, name):
    with pytest.raises(ConfigError):
        safe_child(tmp_path, name)


@pytest.mark.parametrize("name", CONTAINED)
def test_ordinary_artifact_names_are_allowed(tmp_path, name):
    assert safe_child(tmp_path, name).parent == tmp_path.resolve()


@pytest.mark.parametrize("name", ESCAPES)
def test_nothing_is_written_outside_the_output_directory(tmp_path, name):
    out = tmp_path / "run"
    out.mkdir()
    before = sorted(p.name for p in tmp_path.iterdir())
    with pytest.raises(ConfigError):
        write_doc(out, name, {"any": "document"})
    assert sorted(p.name for p in tmp_path.iterdir()) == before
    assert list(out.iterdir()) == []


def test_a_contained_document_is_written_as_canonical_bytes(tmp_path):
    path = write_doc(tmp_path, "result_G020.json", {"b": 1, "a": 2})
    assert path.read_bytes() == b'{"a":2,"b":1}\n'
