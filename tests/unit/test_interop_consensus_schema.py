"""The AGREED canonical consensus preimage/serialization (verbatim with uoh-ay26):
top-level EXACTLY {game_id, game_uid, sub_games}; each sub-game EXACTLY
{sub_game_number, result, roles, score, winner_group}; ordered g01->g06; consensus_sha
omitted from the audit wire when None and validated as 64 lowercase hex when present.
Covers regression scenarios A, B, E, F, G, H, I.
"""

import re

from thief_agent.domain.crypto import canonical_json
from thief_agent.interop.consensus import CANON_SUB_KEYS, consensus_sha, preimage
from thief_agent.interop.wire import AuditPayload

TOP = {"game_id", "game_uid", "sub_games"}
SUB = {"sub_game_number", "result", "roles", "score", "winner_group"}


def _rows(n=6):
    return [
        {
            "sub_game_number": i,
            "result": "survival" if i % 2 else "capture",
            "roles": {"amireman": "thief", "uoh-ay26": "police"},
            "score": {"amireman": 10, "uoh-ay26": 5},
            "winner_group": "amireman" if i % 2 else None,
        }
        for i in range(1, n + 1)
    ]


def test_canonical_object_has_exactly_the_agreed_top_level_keys():
    """Scenario A."""
    obj = preimage("G002", "uid-1", _rows())
    assert set(obj) == TOP
    assert CANON_SUB_KEYS == ("sub_game_number", "result", "roles", "score", "winner_group")


def test_each_subgame_has_exactly_the_agreed_keys():
    """Scenario B: no steps/tie/tokens/github_commit/audit/timestamps leak into a sub-game."""
    obj = preimage("G002", "uid-1", _rows())
    for sg in obj["sub_games"]:
        assert set(sg) == SUB


def test_steps_and_local_only_fields_do_not_affect_sha():
    """Scenarios C/D at the object level: extra keys on the input rows are dropped."""
    clean = _rows()
    noisy = [
        {**r, "steps": 35, "tie": False, "tokens": {"amireman": 9}, "started_at": "t", "audit": {}}
        for r in clean
    ]
    assert consensus_sha("G002", "u", noisy) == consensus_sha("G002", "u", clean)


def test_subgames_are_ordered_g01_to_g06_regardless_of_input_order():
    """Scenario E: shuffled input rows still hash identically (deterministic ordering)."""
    rows = _rows()
    shuffled = [rows[3], rows[0], rows[5], rows[1], rows[4], rows[2]]
    obj = preimage("G002", "uid-1", shuffled)
    assert [sg["sub_game_number"] for sg in obj["sub_games"]] == [1, 2, 3, 4, 5, 6]
    assert consensus_sha("G002", "uid-1", shuffled) == consensus_sha("G002", "uid-1", rows)


def test_consensus_sha_omitted_from_audit_wire_when_none():
    """Scenario F."""
    wire = AuditPayload("thief", [], "survival").to_wire()
    assert "consensus_sha" not in wire
    present = AuditPayload("thief", [], "__consensus__", consensus_sha="a" * 64).to_wire()
    assert present["consensus_sha"] == "a" * 64


def test_valid_64_lowercase_hex_digest_accepted():
    """Scenario G."""
    good = "0123456789abcdef" * 4  # 64 lowercase hex
    payload = AuditPayload.from_wire(
        {"sender": "thief", "records": [], "result_claim": "x", "consensus_sha": good}
    )
    assert payload.consensus_sha == good


def test_malformed_digest_rejected_safely():
    """Scenario H: uppercase / short / non-hex are dropped to None (never drive confirmation)."""
    for bad in ("A" * 64, "abc", "g" * 64, "0" * 63, "0" * 65, 12345):
        payload = AuditPayload.from_wire(
            {"sender": "thief", "records": [], "result_claim": "x", "consensus_sha": bad}
        )
        assert payload.consensus_sha is None


def test_canonical_bytes_are_exact_and_deterministic():
    """Scenario I: the exact canonical byte string is pinned so BOTH repos match byte-for-byte."""
    obj = preimage(
        "G002",
        "uid-1",
        [
            {
                "sub_game_number": 1,
                "result": "survival",
                "roles": {"amireman": "thief", "uoh-ay26": "police"},
                "score": {"amireman": 10, "uoh-ay26": 5},
                "winner_group": "amireman",
            }
        ],
    )
    expected = (
        '{"game_id":"G002","game_uid":"uid-1","sub_games":'
        '[{"result":"survival","roles":{"amireman":"thief","uoh-ay26":"police"},'
        '"score":{"amireman":10,"uoh-ay26":5},"sub_game_number":1,"winner_group":"amireman"}]}'
    )
    assert canonical_json(obj) == expected
    assert re.fullmatch(r"[0-9a-f]{64}", consensus_sha("G002", "uid-1", obj["sub_games"]))
