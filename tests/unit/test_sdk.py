"""Direct coverage of the AgentSDK facade: the single entry point through which
external consumers run series, simulate, and emit/verify artifacts without touching
internal modules."""

from thief_agent.constants import Role
from thief_agent.sdk.sdk import AgentSDK
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG


def _sdk():
    return AgentSDK(Role.THIEF, "amireman-thief", DevTestSigner(), "0" * 40)


def test_local_series_and_simulate():
    sdk = _sdk()
    cfg = validate(DEFAULT_GAME_CONFIG)
    res = sdk.local_series(cfg, seed=1)
    assert len(res["sub_games"]) == 6 and res["winner"] in {"self", "opp", "tie"}
    batch = sdk.simulate(cfg, turns=5)
    assert batch["turns"] >= 5


def test_emit_verify_and_match_audit(tmp_path):
    sdk = _sdk()
    series = sdk.local_series(validate(DEFAULT_GAME_CONFIG), seed=2)
    out, gid = str(tmp_path / "art"), "amireman-thief-vs-opp"
    v = sdk.emit_and_verify(out, gid, "opp", series, DEFAULT_GAME_CONFIG)
    assert v["passed"]
    m = sdk.verify_match(out, gid)
    assert "passed" in m and "failures" in m
