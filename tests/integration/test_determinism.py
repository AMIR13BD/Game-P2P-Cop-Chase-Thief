from thief_agent.constants import Role
from thief_agent.sdk.series import run_series
from thief_agent.security.signer import DevTestSigner


def _trace(res):
    return [
        (s["self_role"], s["outcome"], s["self_score"], s["opp_score"], s["trajectory"])
        for s in res["sub_games"]
    ]


def test_same_seed_same_trajectory(cfg):
    a = run_series(cfg, Role.THIEF, "g", DevTestSigner(), seed=777)
    b = run_series(cfg, Role.THIEF, "g", DevTestSigner(), seed=777)
    assert _trace(a) == _trace(b)
    assert a["self_total"] == b["self_total"] and a["role_sequence"] == b["role_sequence"]


def test_different_seed_may_differ_but_stays_legal(cfg):
    a = run_series(cfg, Role.THIEF, "g", DevTestSigner(), seed=1)
    b = run_series(cfg, Role.THIEF, "g", DevTestSigner(), seed=2)
    for res in (a, b):
        for s in res["sub_games"]:
            assert s["illegal"] == 0 and s["diagonal"] == 0
