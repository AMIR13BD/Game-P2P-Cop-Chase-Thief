"""The emailed ``result_<game_id>.json`` carries EVERY field the book makes mandatory.

Book (police_thief_p2p.pdf v3.0.0): §9.3.3 p.78 (identity, GitHub + MCP addresses, hardware,
game timestamp, SHA-256 mutual agreement); ch.9 p.78 (both groups' GitHub links, the commit id
of each sub-game, total tokens); §9.4 + App. E rule 49 (four repo links); ch.5.5 + rule 53
(per-sub-game commit); rule 54 (tokens per sub-game and per series); rules 35/36 (mutual
agreement); App. F table 17 (scoring + tie) and table 18 row 1 (six sub-games)."""

from official_result_fixture import (
    OURS,
    PEER_POLICE_SHA,
    PEER_THIEF_SHA,
    THEIRS,
    official_result,
)

from thief_agent.interop import ids
from thief_agent.interop.consensus import consensus_sha


def test_filename_is_result_game_id_json():
    assert ids.result_name("G013") == "result_G013.json"


def test_official_series_has_exactly_six_rows():
    doc = official_result()
    assert doc["num_sub_games"] == 6 and len(doc["sub_games"]) == 6
    assert [r["sub_game_number"] for r in doc["sub_games"]] == [1, 2, 3, 4, 5, 6]


def test_roles_result_and_winner_present_per_row():
    for row in official_result()["sub_games"]:
        assert set(row["roles"]) == {OURS, THEIRS}
        assert set(row["roles"].values()) == {"police", "thief"}
        assert row["result"] in {"capture", "survival", "timeout", "technical_loss"}
        assert "winner_group" in row and row["tie"] is False


def test_score_and_token_fields_are_group_keyed():
    doc = official_result(tokens=1500)
    for row in doc["sub_games"]:
        assert set(row["score"]) == {OURS, THEIRS} and set(row["tokens"]) == {OURS, THEIRS}
        assert row["tokens"][OURS] == 1500  # rule 54: real per-sub-game consumption
    assert doc["final_result"]["tokens_total_series"][OURS] == 6 * 1500  # ...and the series total


def test_audit_log_reference_and_timing_fields_present():
    doc = official_result()
    for row in doc["sub_games"]:
        assert {"log_verified", "tampered", "result_agreed"} <= set(row["audit"])
        assert row["log_files"][OURS] and row["log_files"][THEIRS]
        assert row["started_at"] and row["ended_at"] and row["steps"] == 35
    assert doc["game_started_at"] and doc["game_ended_at"] and doc["timezone"]


def test_both_negotiated_per_sub_game_shas_are_reported():
    """Rule 53: the commit each side actually played, per sub-game — never blank when the peer
    declared one, and never swapped between the groups when roles alternate."""
    rows = official_result()["sub_games"]
    assert [r["github_commit"][THEIRS] for r in rows] == [
        PEER_POLICE_SHA,
        PEER_THIEF_SHA,
        PEER_POLICE_SHA,
        PEER_THIEF_SHA,
        PEER_POLICE_SHA,
        PEER_THIEF_SHA,
    ]
    assert all(len(r["github_commit"][OURS]) == 40 for r in rows)
    assert all(r["github_commit"][OURS] != r["github_commit"][THEIRS] for r in rows)


def test_four_github_repo_links_present():
    github = official_result()["links"]["github"]
    assert set(github) == {OURS, THEIRS}
    assert {"cop", "thief"} <= set(github[OURS]) and {"cop", "thief"} <= set(github[THEIRS])
    assert len({url for repos in github.values() for url in repos.values()}) == 4


def test_group_identity_mcp_and_hardware_blocks_present():
    """§9.3.3: the mandatory report carries identity, MCP addresses and hardware for both."""
    details = official_result()["group_details"]
    assert {b["group_id"] for b in details.values()} == {OURS, THEIRS}
    for block in details.values():
        assert block["members"] and block["repos"] and block["mcp_servers"]
        assert "hardware_spec" in block and "llm_model" in block


def test_final_aggregate_is_complete_and_correct():
    doc = official_result()
    final = doc["final_result"]
    assert set(final) == {
        "series_tie",
        "sub_games_won",
        "ties",
        "tokens_total_series",
        "total_score",
        "winner_group",
    }
    # amireman is Thief on g1/3/5 (survival: 10) and Police on g2/4/6 (capture: 20) => 90 vs 30.
    assert final["total_score"] == {OURS: 90, THEIRS: 30}
    assert final["sub_games_won"] == {OURS: 6, THEIRS: 0}
    assert final["winner_group"] == OURS and final["series_tie"] is False and final["ties"] == 0


def test_series_tie_adds_two_to_each_side():
    """App. F table 17 row 5 / §9.2.1 tie rule: +2 to each side, once, only on a level series."""
    from thief_agent.interop.scoring import aggregate

    rows = [
        {"result": "survival", "score": {OURS: 10, THEIRS: 5}, "tokens": {OURS: 0, THEIRS: 0}},
        {"result": "survival", "score": {OURS: 5, THEIRS: 10}, "tokens": {OURS: 0, THEIRS: 0}},
    ]
    final = aggregate(rows, OURS, THEIRS)
    assert final["series_tie"] is True and final["total_score"] == {OURS: 17, THEIRS: 17}
    assert final["winner_group"] is None


def test_mutual_agreement_block_is_complete():
    ma = official_result()["mutual_agreement"]
    assert {"sha256", "peer_sha256", "sha_match", "results_agreed", "confirmed"} == set(ma)
    assert len(ma["sha256"]) == 64 and ma["sha_match"] is True and ma["confirmed"] is True


def test_reporting_metadata_never_moves_the_consensus_digest():
    """Tokens, commits, identity blocks and timestamps are reporting-only: the canonical
    consensus preimage (and therefore the digest both peers exchange) is unchanged."""
    plain = official_result(tokens=0)
    rich = official_result(tokens=9999)
    assert consensus_sha("G013", "uid-0001", plain["sub_games"]) == consensus_sha(
        "G013", "uid-0001", rich["sub_games"]
    )
