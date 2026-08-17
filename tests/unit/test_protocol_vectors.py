"""Cross-team conformance: OUR modules against the published protocol vector values.

This is the interoperability baseline (34 checks). It must stay green: every one of
these is a place where a byte of difference means two independent implementations
cannot play, audit or settle a match together.
"""

import hashlib
import json

import pytest
from protocol_vectors import (
    CANONICAL,
    COMMITS,
    EXPECT_GAME_ID,
    EXPECT_GAME_UID,
    OTHER_FORMS,
    REFERENCE_FORM,
    TERMS_NONCE,
    TERMS_SIGNATURE,
    UID_PAIRS,
    VECTOR_TERMS,
)

from thief_agent.domain.crypto import canonical_json, commit_of
from thief_agent.interop.ids import (
    config_name,
    declaration_name,
    derive_game_ids,
    log_name,
    result_name,
)
from thief_agent.interop.negotiate import Negotiator
from thief_agent.interop.terms import DEFAULTS, TERMS_KEYS, terms_from_config

# SPEC 6: the settlement signature's SPACED second form, against our compact form.
REPORT_SPACED: list[tuple[dict, str, str]] = [
    (
        {
            "קבוצה_א": "team-aleph",
            "קבוצה_ב": "team-bet",
            "תוצאה": {"מנצחת": "team-aleph", "ניקוד": [20, 5]},
            "game_uid": "f757f50d-d4f4-17e7-06cf-755905739b16",
            "tokens_total_series": 0,
            "github_commit": "abc1234",
        },
        "af661c4101cfe73470794102ab7417b67ef0ea5b8c3bc55b38133ac5f8e95049",
        "a87d61b5c1b7ea838a8e5fc7acc9f9004e28e50acb8c243431ab6ff78be33397",
    ),
    (
        {
            "סדרה": [{"משחקון": 1, "ניקוד": [5, 10]}, {"משחקון": 2, "ניקוד": [20, 5]}],
            "ram_gb": 31.8,
            "decay_per_step": 0.1,
            "mutual_agreement": True,
        },
        "77c4cce023b641406db0dd3efd7ca44563aa8e4b8eaa9e02c128fa9b9ef7bbd7",
        "4f9234b867116a1367245a65a0b18ff0f1390bea65f982e42576104321b6845b",
    ),
]


@pytest.mark.parametrize(("obj", "canon", "sha"), CANONICAL)
def test_canonical_json_is_byte_exact(obj, canon, sha):
    """sort_keys, ensure_ascii=False, compact separators — and code-point key order."""
    assert canonical_json(obj) == canon
    assert hashlib.sha256(canon.encode("utf-8")).hexdigest() == sha


@pytest.mark.parametrize(("payload", "nonce", "commit"), COMMITS)
def test_commit_reveal_reference_construction(payload, nonce, commit):
    """SHA256(canonical_json(payload)|nonce) with a SINGLE pipe separator."""
    assert commit_of(payload, nonce) == commit


def test_commit_is_the_reference_form_and_not_the_other_two():
    payload, nonce, _ = COMMITS[1]
    ours = commit_of(payload, nonce)
    assert ours == REFERENCE_FORM
    assert ours not in OTHER_FORMS


def test_terms_signature_via_the_real_negotiator():
    """The signature the handshake actually sends, not a re-derivation in the test."""
    negotiator = Negotiator(dict(VECTOR_TERMS), {"group_id": "team-aleph"}, "team-aleph")
    negotiator._nonce = TERMS_NONCE
    assert negotiator.signed(role="police", sub_game_number=1).signature == TERMS_SIGNATURE


@pytest.mark.parametrize(("group_a", "group_b"), UID_PAIRS)
def test_both_match_ids_are_order_independent(group_a, group_b):
    """Both peers sort the pair, so neither has to be told which name to use."""
    game_id, game_uid = derive_game_ids(VECTOR_TERMS, group_a, group_b)
    assert game_id == EXPECT_GAME_ID
    assert game_uid == EXPECT_GAME_UID


def test_artifact_filenames_follow_the_official_grammar():
    gid = EXPECT_GAME_ID
    assert declaration_name(gid) == f"declaration_{gid}.json"
    assert result_name(gid) == f"result_{gid}.json"
    assert config_name(gid, 7) == f"config_{gid}_g07.json"
    assert log_name(gid, 7) == f"log_{gid}_g07.json"


def test_the_fourteen_signed_terms_match_the_agreed_set():
    assert set(TERMS_KEYS) == set(VECTOR_TERMS)
    ours = terms_from_config({})
    expected = {k: v for k, v in VECTOR_TERMS.items() if k != "num_games"}
    assert {k: v for k, v in ours.items() if k != "num_games"} == expected


def test_project_terms_file_matches_our_defaults():
    """The repo-level terms.json is the same agreement our code signs."""
    assert dict(DEFAULTS) == {
        "board_size": 7,
        "smell_grid_size": 5,
        "decay_per_step": 0.1,
        "emit_intensity": 0.9,
        "min_center_intensity": 0.5,
        "max_steps": 35,
        "barriers_max": 14,
        "setting": "Haifa",
        "hint_max_words": 15,
        "axis_origin_corner": "top-left",
        "axis_start_index": 0,
        "thief_start": [3, 3],
        "cop_start": [0, 0],
        "num_games": 6,
    }


@pytest.mark.parametrize(("report", "spaced_sha", "compact_sha"), REPORT_SPACED)
def test_settlement_uses_a_second_spaced_serialization(report, spaced_sha, compact_sha):
    """The settlement signature is SPACED; our compact form is deliberately different."""
    spaced = json.dumps(report, sort_keys=True, ensure_ascii=False)
    assert hashlib.sha256(spaced.encode("utf-8")).hexdigest() == spaced_sha
    assert hashlib.sha256(canonical_json(report).encode("utf-8")).hexdigest() == compact_sha
