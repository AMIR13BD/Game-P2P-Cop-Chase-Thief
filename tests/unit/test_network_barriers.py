"""Network barrier protocol: the Police declares and applies a barrier, the peer
validates and applies the same barrier (both boards stay identical), a barrier on the
Thief captures, the Thief can never place one, and explicit baseline mode still runs."""

import thief_agent.sdk.series as series_mod
from thief_agent.constants import Role
from thief_agent.peer.net_engine import PeerHalf
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy.base import Action
from thief_agent.strategy.production import make_gameplay_brain

CFG = validate(DEFAULT_GAME_CONFIG)


class _AlwaysBarrier:
    def __init__(self, target):
        self.target = target

    def decide(self, obs):
        return Action("BARRIER", self.target)

    def hint(self, obs):
        return "setting up a checkpoint"


def _thief(seed=1):
    return PeerHalf(
        "thief",
        CFG,
        make_gameplay_brain("thief", seed, baseline=True),
        "g",
        "0" * 40,
        DevTestSigner(),
        1,
    )


def test_network_barriers_synchronize():
    police = PeerHalf("police", CFG, _AlwaysBarrier("S"), "g", "0" * 40, DevTestSigner(), 1)
    thief = _thief()
    msg = police.act()
    assert msg["barrier_placed"] == [1, 0] and police.barriers_used == 1
    thief.receive(msg)
    assert police.board.barriers == thief.board.barriers == {(1, 0)}  # synchronized
    # duplicate + out-of-bounds + malformed declarations are rejected, board unchanged
    assert thief._apply_barrier([1, 0]) is False
    assert thief._apply_barrier([99, 99]) is False
    assert thief._apply_barrier("bad") is False
    assert thief.board.barriers == {(1, 0)}


def test_network_barrier_capture_and_thief_cannot_place():
    thief = _thief()
    thief.pos = (2, 2)
    assert thief.receive({"barrier_placed": [2, 2]}) is True  # barrier on thief = capture
    # a Thief proposing a barrier is firewalled: it never declares one
    rogue = PeerHalf("thief", CFG, _AlwaysBarrier("S"), "g", "0" * 40, DevTestSigner(), 1)
    out = rogue.act()
    assert out["barrier_placed"] is None and rogue.barriers_used == 0


def test_baseline_mode_available(monkeypatch):
    seen = []
    orig = series_mod.run_sub_game

    def spy(p, t, *a, **k):
        seen.append((type(p).__name__, type(t).__name__))
        return orig(p, t, *a, **k)

    monkeypatch.setattr(series_mod, "run_sub_game", spy)
    res = series_mod.run_series(
        CFG, Role.POLICE, "g", DevTestSigner(), seed=1, github_commit="0" * 40, baseline=True
    )
    assert all(pt == ("PoliceGreedyBrain", "ThiefDistanceBrain") for pt in seen)
    assert len(res["sub_games"]) == 6
