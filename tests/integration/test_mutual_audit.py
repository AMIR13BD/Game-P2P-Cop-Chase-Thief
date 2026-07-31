"""Finding 1: strict cross-repo match audit (verify_match) fails closed on tampered
or incomplete evidence. Baseline uses distinct per-peer Git commits + signed idents."""

import json
import os

from thief_agent.constants import Role
from thief_agent.report import artifacts, ids
from thief_agent.report.emit import emit_series
from thief_agent.report.verify import verify_match
from thief_agent.sdk.series import run_series
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

GID = "amireman-police-vs-amireman-thief"
CP, CT = "a" * 40, "b" * 40
REPOS = {
    "amireman-police": {"cop": "pu1", "thief": "pu2"},
    "amireman-thief": {"cop": "tu1", "thief": "tu2"},
}


def _build(tmp, signer, peer_commit=CT):
    cfg = validate(DEFAULT_GAME_CONFIG)
    s = run_series(cfg, Role.POLICE, "amireman-police", signer, seed=1, github_commit=CP)
    peer_ident = artifacts.group_ident("amireman-thief", REPOS, signer, peer_commit)
    emit_series(
        str(tmp),
        GID,
        {**DEFAULT_GAME_CONFIG, "agreed_between": ["amireman-police", "amireman-thief"]},
        "amireman-police",
        "amireman-thief",
        s,
        CP,
        REPOS,
        signer,
        peer_commit=peer_commit,
        peer_ident=peer_ident,
    )


def _rw(path, fn):
    with open(path, encoding="utf-8") as fh:
        o = json.load(fh)
    fn(o)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(o, fh)


def test_baseline_match_audit_passes(tmp_path, signer):
    _build(tmp_path, signer)
    r = verify_match(str(tmp_path), GID, signer)
    assert r["passed"], r["failures"]


def test_modified_opponent_members_fails(tmp_path, signer):
    _build(tmp_path, signer)
    _rw(
        tmp_path / ids.declaration_name(GID),
        lambda o: o["groups"]["group_2"].__setitem__("members", ["HACK"]),
    )
    assert not verify_match(str(tmp_path), GID, signer)["passed"]


def test_modified_opponent_hardware_fails(tmp_path, signer):
    _build(tmp_path, signer)
    _rw(
        tmp_path / ids.declaration_name(GID),
        lambda o: o["groups"]["group_2"].__setitem__("hardware_spec", {"cpu": "FAKE"}),
    )
    assert not verify_match(str(tmp_path), GID, signer)["passed"]


def test_modified_score_winner_fails(tmp_path, signer):
    _build(tmp_path, signer)
    _rw(
        tmp_path / ids.result_name(GID),
        lambda o: o["final_result"].__setitem__("winner_group", "cheater"),
    )
    assert not verify_match(str(tmp_path), GID, signer)["passed"]


def test_modified_opponent_commit_fails(tmp_path, signer):
    _build(tmp_path, signer)
    _rw(
        tmp_path / ids.result_name(GID),
        lambda o: o["sub_games"][0]["github_commit"].__setitem__("amireman-thief", "c" * 40),
    )
    assert not verify_match(str(tmp_path), GID, signer)["passed"]


def test_removed_sub_game_fails(tmp_path, signer):
    _build(tmp_path, signer)
    _rw(tmp_path / ids.result_name(GID), lambda o: o.update(sub_games=o["sub_games"][:5]))
    os.remove(tmp_path / ids.config_name(GID, 6))
    os.remove(tmp_path / ids.log_name(GID, 6))
    assert not verify_match(str(tmp_path), GID, signer)["passed"]


def test_removed_config_section_fails(tmp_path, signer):
    _build(tmp_path, signer)
    _rw(tmp_path / ids.config_name(GID, 1), lambda o: o.pop("scoring"))
    assert not verify_match(str(tmp_path), GID, signer)["passed"]


def test_same_git_commit_for_both_peers_fails(tmp_path, signer):
    _build(tmp_path, signer, peer_commit=CP)  # both peers share one commit
    assert not verify_match(str(tmp_path), GID, signer)["passed"]


def test_unsigned_mutual_agreement_fails(tmp_path, signer):
    _build(tmp_path, signer)
    _rw(tmp_path / ids.result_name(GID), lambda o: o["mutual_agreement"].pop("signatures"))
    assert not verify_match(str(tmp_path), GID, signer)["passed"]


def test_declaration_missing_github_commit_fails(tmp_path, signer):
    _build(tmp_path, signer)
    _rw(tmp_path / ids.declaration_name(GID), lambda o: o["groups"]["group_2"].pop("github_commit"))
    assert not verify_match(str(tmp_path), GID, signer)["passed"]
