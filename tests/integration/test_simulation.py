from thief_agent.sim.batch import run_batch


def test_batch_clean(cfg):
    r = run_batch(cfg, min_turns=2000, base_seed=1)
    assert r["turns"] >= 2000
    assert r["illegal"] == 0
    assert r["diagonal"] == 0
    assert r["timeouts"] == 0
    assert r["exceptions"] == 0
    assert sum(r["outcomes"].values()) == r["sub_games"]
