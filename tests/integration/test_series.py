from thief_agent.constants import Role
from thief_agent.sdk.series import run_series


def test_six_sub_games_and_role_alternation(cfg, signer, commit):
    res = run_series(cfg, Role.THIEF, "amireman-thief", signer, seed=1234, github_commit=commit)
    assert len(res["sub_games"]) == 6
    assert res["role_sequence"] == ["thief", "police", "thief", "police", "thief", "police"]


def test_every_subgame_outcome_and_no_technical(cfg, signer, commit):
    res = run_series(cfg, Role.THIEF, "amireman-thief", signer, seed=1234, github_commit=commit)
    for s in res["sub_games"]:
        assert s["outcome"] in ("capture", "survival")  # valid commit => audit passes
        assert s["illegal"] == 0 and s["diagonal"] == 0


def test_fresh_state_between_subgames(cfg, signer, commit):
    res = run_series(cfg, Role.THIEF, "amireman-thief", signer, seed=1234, github_commit=commit)
    for s in res["sub_games"]:
        assert s["records"][0]["payload"]["step"] == 0
        assert s["records"][0]["payload"]["github_commit"] == commit
