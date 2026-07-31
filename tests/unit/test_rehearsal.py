"""P26 local counted-rehearsal validation: an emitted counted-two-peer evidence
directory validates with the peers' own distinct keys, and a forged peer confirmation
is detected (fails closed)."""

from thief_agent.constants import Role
from thief_agent.report.confirm import confirmation_summary, final_hash, make_confirmation
from thief_agent.report.emit import emit_series
from thief_agent.sdk.series import run_series
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.sim.rehearsal import validate_counted_evidence

POLICE = DevTestSigner("amireman-police", key=b"police-key")
THIEF = DevTestSigner("amireman-thief", key=b"thief-key")
REPOS = {
    "amireman-police": {"cop": "pu1", "thief": "pu2"},
    "amireman-thief": {"cop": "tu1", "thief": "tu2"},
}
GID = "amireman-police-vs-amireman-thief"
SIGNERS = {"amireman-police": POLICE, "amireman-thief": THIEF}


def _emit(tmp, thief_conf):
    cfg = validate(DEFAULT_GAME_CONFIG)
    series = run_series(cfg, Role.POLICE, "amireman-police", POLICE, seed=1, github_commit="a" * 40)
    h = final_hash(confirmation_summary(series, "amireman-police", "amireman-thief"))
    series["confirmations"] = {
        "amireman-police": make_confirmation("amireman-police", h, POLICE),
        "amireman-thief": thief_conf(h),
    }
    emit_series(
        str(tmp),
        GID,
        {**DEFAULT_GAME_CONFIG, "agreed_between": ["amireman-police", "amireman-thief"]},
        "amireman-police",
        "amireman-thief",
        series,
        "a" * 40,
        REPOS,
        POLICE,
        peer_commit="b" * 40,
    )


def test_counted_evidence_validates(tmp_path):
    _emit(tmp_path, lambda h: make_confirmation("amireman-thief", h, THIEF))
    res = validate_counted_evidence(str(tmp_path), GID, SIGNERS)
    assert res["passed"], res["failures"]
    assert res["sub_games"] == 6


def test_forged_peer_confirmation_detected(tmp_path):
    # Thief confirmation forged with the POLICE key -> must fail under the thief key.
    _emit(tmp_path, lambda h: make_confirmation("amireman-thief", h, POLICE))
    res = validate_counted_evidence(str(tmp_path), GID, SIGNERS)
    assert res["passed"] is False


def test_shared_key_is_flagged_forgeable(tmp_path):
    # If both peers shared one key, swapped-key verification would pass -> flagged.
    shared = {"amireman-police": POLICE, "amireman-thief": POLICE}
    _emit(tmp_path, lambda h: make_confirmation("amireman-thief", h, POLICE))
    res = validate_counted_evidence(str(tmp_path), GID, shared)
    assert res["passed"] is False and any("forgeable" in f for f in res["failures"])
