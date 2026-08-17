"""Historical settlement digests must never move, and the new profile must be exact.

Two filed counted series are pinned to literal constants taken from the artifacts we
already emailed. If either changes, a report we have already submitted stops verifying —
so these assertions are deliberately hard-coded rather than recomputed from the code
under test.
"""

import hashlib
import json

import pytest
from consensus_fixtures import (
    G002_GAME_ID,
    G002_GAME_UID,
    G002_LEGACY_SHA,
    G002_ROWS,
    G020_AGGREGATE,
    G020_GAME_ID,
    G020_GAME_UID,
    G020_LEGACY_SHA,
    G020_REFERENCE_SHA,
    G020_ROWS,
)

from thief_agent.domain.crypto import canonical_json
from thief_agent.interop.consensus import (
    CANON_SUB_KEYS,
    LEGACY,
    OFFICIAL_REFERENCE_V1,
    PROFILES,
    consensus_sha,
)

HISTORICAL = [
    (G020_GAME_ID, G020_GAME_UID, G020_ROWS, G020_LEGACY_SHA),
    (G002_GAME_ID, G002_GAME_UID, G002_ROWS, G002_LEGACY_SHA),
]


@pytest.mark.parametrize(("game_id", "game_uid", "rows", "expected"), HISTORICAL)
def test_filed_legacy_digest_is_reproduced_exactly(game_id, game_uid, rows, expected):
    assert consensus_sha(game_id, game_uid, rows) == expected


@pytest.mark.parametrize(("game_id", "game_uid", "rows", "expected"), HISTORICAL)
def test_legacy_is_the_default_profile(game_id, game_uid, rows, expected):
    """Omitting the profile must keep filing the digest our opponents already agreed."""
    assert consensus_sha(game_id, game_uid, rows, profile=LEGACY) == expected


def test_official_reference_profile_matches_the_lecturer_reference():
    got = consensus_sha(G020_GAME_ID, G020_GAME_UID, G020_ROWS, profile=OFFICIAL_REFERENCE_V1)
    assert got == G020_REFERENCE_SHA


def test_the_two_profiles_are_different_and_neither_is_a_half_change():
    """A change applied to the scope OR the separators alone matches nobody at all."""
    legacy = consensus_sha(G020_GAME_ID, G020_GAME_UID, G020_ROWS, profile=LEGACY)
    reference = consensus_sha(G020_GAME_ID, G020_GAME_UID, G020_ROWS, profile=OFFICIAL_REFERENCE_V1)
    assert legacy != reference

    scope_only = {
        "game_id": G020_GAME_ID,
        "aggregate": G020_AGGREGATE,
        "sub_games": [{k: r[k] for k in CANON_SUB_KEYS} for r in G020_ROWS],
    }
    compact = hashlib.sha256(canonical_json(scope_only).encode("utf-8")).hexdigest()
    assert compact not in (legacy, reference)

    spaced_legacy = json.dumps(
        {"game_id": G020_GAME_ID, "game_uid": G020_GAME_UID, "sub_games": G020_ROWS},
        sort_keys=True,
        ensure_ascii=False,
    )
    assert hashlib.sha256(spaced_legacy.encode("utf-8")).hexdigest() not in (legacy, reference)


def test_the_five_consensus_row_keys_are_frozen():
    """Shared with the lecturer's reference row; changing it breaks BOTH profiles."""
    assert set(CANON_SUB_KEYS) == {
        "sub_game_number",
        "result",
        "roles",
        "score",
        "winner_group",
    }


def test_only_the_two_known_profiles_exist_and_an_unknown_one_is_refused():
    assert PROFILES == (LEGACY, OFFICIAL_REFERENCE_V1)
    with pytest.raises(ValueError):
        consensus_sha(G020_GAME_ID, G020_GAME_UID, G020_ROWS, profile="something-else")
