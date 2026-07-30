from thief_agent.constants import Role
from thief_agent.peer.audit import run_audit
from thief_agent.sdk.series import run_series
from thief_agent.security.signer import DevTestSigner


def test_six_sub_games_and_role_alternation(cfg):
    res = run_series(cfg, Role.THIEF, "amireman-thief", DevTestSigner(), seed=1234)
    assert len(res["sub_games"]) == 6
    assert res["role_sequence"] == ["thief", "police", "thief", "police", "thief", "police"]


def test_every_subgame_outcome_and_audit(cfg):
    res = run_series(cfg, Role.THIEF, "amireman-thief", DevTestSigner(), seed=1234)
    for s in res["sub_games"]:
        assert s["outcome"] in ("capture", "survival")
        assert s["illegal"] == 0 and s["diagonal"] == 0
        assert run_audit(s["records"])["passed"]


def test_fresh_state_between_subgames(cfg):
    # step-0 record present in each sub-game log => state rebuilt each time
    res = run_series(cfg, Role.THIEF, "amireman-thief", DevTestSigner(), seed=1234)
    for s in res["sub_games"]:
        assert s["records"][0]["payload"]["step"] == 0
