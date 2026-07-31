import json

from thief_agent.constants import Role
from thief_agent.report import ids
from thief_agent.report.emit import emit_series
from thief_agent.report.verify import agree, verify_series
from thief_agent.sdk.series import run_series
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

GID = "amireman-police-vs-opp"
REPOS = {"amireman-police": {"cop": "u1", "thief": "u2"}, "opp": {"cop": "u3", "thief": "u4"}}


def _emit(tmp, cfg, signer, commit, seed=1234):
    series = run_series(
        cfg, Role.POLICE, "amireman-police", signer, seed=seed, github_commit=commit
    )
    out = emit_series(
        str(tmp),
        GID,
        {**DEFAULT_GAME_CONFIG, "agreed_between": ["amireman-police", "opp"]},
        "amireman-police",
        "opp",
        series,
        commit,
        REPOS,
        signer,
    )
    return series, out


def _rewrite(path, mutate):
    with open(path, encoding="utf-8") as fh:
        obj = json.load(fh)
    mutate(obj)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)


def test_valid_complete_chain_and_six_sub_games(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    r = verify_series(str(tmp_path), GID, signer)
    assert r["passed"], r["failures"]
    with open(tmp_path / ids.result_name(GID), encoding="utf-8") as fh:
        res = json.load(fh)
    assert res["num_sub_games"] == 6 and len(res["sub_games"]) == 6


def test_modified_declaration_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    _rewrite(tmp_path / ids.declaration_name(GID), lambda o: o.update(game_uid="deadbeef"))
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_modified_configuration_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    _rewrite(tmp_path / ids.config_name(GID, 1), lambda o: o["scoring"].update(capture_cop=99))
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_modified_turn_record_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)

    def mut(o):
        o["records"][1]["payload"]["move"] = "MOVE:TAMPER"

    _rewrite(tmp_path / ids.log_name(GID, 1), mut)
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_modified_final_result_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    _rewrite(
        tmp_path / ids.result_name(GID), lambda o: o["final_result"].update(winner_group="cheater")
    )
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_broken_hash_link_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    _rewrite(
        tmp_path / ids.result_name(GID), lambda o: o["sub_games"][0].update(log_sha256="0" * 64)
    )
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_missing_artifact_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    (tmp_path / ids.log_name(GID, 3)).unlink()
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_malformed_json_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    (tmp_path / ids.config_name(GID, 2)).write_text("{ not json", encoding="utf-8")
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_schema_violation_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    _rewrite(tmp_path / ids.result_name(GID), lambda o: o.pop("mutual_agreement"))
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_reordered_records_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    _rewrite(
        tmp_path / ids.log_name(GID, 1), lambda o: o.update(records=list(reversed(o["records"])))
    )
    assert not verify_series(str(tmp_path), GID, signer)["passed"]


def test_wrong_game_id_fails(tmp_path, cfg, signer, commit):
    _emit(tmp_path, cfg, signer, commit)
    assert not verify_series(str(tmp_path), "wrong-game-id", signer)["passed"]


def test_peer_disagreement_detected(tmp_path, cfg, signer, commit):
    _, out = _emit(tmp_path, cfg, signer, commit)
    res = out["result"]
    peer = json.loads(json.dumps(res))
    assert agree(res, peer)
    peer["mutual_agreement"]["sha256"] = "0" * 64
    assert not agree(res, peer)


def test_deterministic_emission_same_series(tmp_path, cfg, signer, commit):
    series = run_series(
        cfg, Role.POLICE, "amireman-police", signer, seed=1234, github_commit=commit
    )
    a, b = tmp_path / "a", tmp_path / "b"
    for d in (a, b):
        emit_series(
            str(d),
            GID,
            {**DEFAULT_GAME_CONFIG, "agreed_between": ["amireman-police", "opp"]},
            "amireman-police",
            "opp",
            series,
            commit,
            REPOS,
            signer,
        )
    for name in (ids.declaration_name(GID), ids.result_name(GID), ids.log_name(GID, 1)):
        assert (a / name).read_text() == (b / name).read_text()
