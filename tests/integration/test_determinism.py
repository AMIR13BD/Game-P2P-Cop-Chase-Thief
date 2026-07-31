from thief_agent.constants import Role
from thief_agent.sdk.series import run_series


def _trace(res):
    return [
        (s["self_role"], s["outcome"], s["self_score"], s["opp_score"], s["trajectory"])
        for s in res["sub_games"]
    ]


def test_same_seed_same_trajectory(cfg, signer, commit):
    a = run_series(cfg, Role.THIEF, "g", signer, seed=777, github_commit=commit)
    b = run_series(cfg, Role.THIEF, "g", signer, seed=777, github_commit=commit)
    assert _trace(a) == _trace(b)
    assert a["self_total"] == b["self_total"] and a["role_sequence"] == b["role_sequence"]


def test_different_seed_stays_legal(cfg, signer, commit):
    for seed in (1, 2):
        res = run_series(cfg, Role.THIEF, "g", signer, seed=seed, github_commit=commit)
        for s in res["sub_games"]:
            assert s["illegal"] == 0 and s["diagonal"] == 0
