"""Official result report, validator half: what `assert_compliant` accepts, which
omissions it rejects, which gaps only warn because the peer alone could fill them,
tolerance of extra local fields, and machine-readability. Field-presence tests live
in test_interop_official_result_compliance.py."""

import json

import pytest
from official_result_fixture import (
    OURS,
    THEIRS,
    official_result,
)

from thief_agent.interop import ids
from thief_agent.interop.compliance import assert_compliant, problems_with, warnings_for


def test_validator_accepts_the_official_result():
    doc = official_result()
    assert problems_with(doc) == [] and warnings_for(doc) == []
    assert_compliant(doc)  # does not raise


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["sub_games"].pop(),  # fewer than six sub-games
        lambda d: d["links"].pop("github"),  # rule 49: four repo links
        lambda d: d["links"]["github"].__setitem__(OURS, {"cop": "u"}),  # our own thief repo
        lambda d: d["sub_games"][2]["github_commit"].__setitem__(OURS, ""),  # our own, rule 53
        lambda d: d["sub_games"][0].pop("tokens"),  # rule 54
        lambda d: d.pop("mutual_agreement"),  # rules 35/36
        lambda d: d["mutual_agreement"].__setitem__("sha256", "nope"),  # not a SHA-256
        lambda d: d.pop("group_details"),  # §9.3.3
        lambda d: d["final_result"].pop("tokens_total_series"),  # series token total
        lambda d: d.pop("game_started_at"),  # §9.3.3 game timestamp
        lambda d: d["sub_games"][1].pop("log_files"),  # per-sub-game log reference
    ],
)
def test_validator_rejects_an_incomplete_report(mutate):
    doc = official_result()
    mutate(doc)
    assert problems_with(doc), "an HW-mandatory field went missing and was not caught"
    with pytest.raises(ValueError):
        assert_compliant(doc)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["sub_games"][2]["github_commit"].__setitem__(THEIRS, ""),
        lambda d: d["links"]["github"].__setitem__(THEIRS, {}),
        lambda d: [b for b in d["group_details"].values() if b["group_id"] == THEIRS][0].pop(
            "mcp_servers"
        ),
    ],
)
def test_a_gap_the_peer_alone_could_fill_is_warned_not_blocked(mutate):
    """Rule 35 punishes NOT reporting too: a peer that declared nothing must never stop our own
    report from going out. The hole is surfaced loudly instead — and never filled with a guess."""
    doc = official_result()
    mutate(doc)
    assert problems_with(doc) == []  # still sendable
    assert warnings_for(doc), "a peer-sourced gap must still be reported to the operator"
    assert_compliant(doc)  # does not raise


def test_validator_tolerates_extra_local_fields():
    doc = official_result()
    doc["local_notes"] = {"anything": True}
    doc["sub_games"][0]["duration_seconds"] = 12.5
    assert problems_with(doc) == []


def test_result_is_machine_readable_json(tmp_path):
    """Rules 33/34: the report is a JSON document, sent as a file — never free text."""
    path = tmp_path / ids.result_name("G013")
    path.write_text(json.dumps(official_result()), encoding="utf-8")
    assert json.loads(path.read_text(encoding="utf-8"))["report_type"] == "final_game_result"
