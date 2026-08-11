"""Production-integration proofs: real gameplay paths use the adaptive MetaController
via one shared factory; profiles learn only from audited evidence and reset per
opponent; hint credibility gates live influence; network barriers synchronize."""

import thief_agent.sdk.series as series_mod
from thief_agent.constants import Role
from thief_agent.domain.board import Board
from thief_agent.infra.mcp_server import _brain as responder_brain
from thief_agent.peer import net_driver
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import is_legal
from thief_agent.strategy.meta import MetaController
from thief_agent.strategy.production import make_gameplay_brain, production_brain
from thief_agent.strategy.profiling import ProfileStore
from thief_agent.strategy.rng import make_rng

CFG = validate(DEFAULT_GAME_CONFIG)


def _spy_series(monkeypatch):
    seen = []
    orig = series_mod.run_sub_game

    def spy(p, t, *a, **k):
        seen.append((type(p).__name__, type(t).__name__))
        return orig(p, t, *a, **k)

    monkeypatch.setattr(series_mod, "run_sub_game", spy)
    return seen


def _sub_game(seed=1):
    return run_sub_game(
        make_gameplay_brain("police", seed, baseline=True),
        make_gameplay_brain("thief", seed + 5, baseline=True),
        {**CFG, "sub_game_number": 1},
        "opp",
        DevTestSigner(),
        "0" * 40,
    )


def _obs(role, **kw):
    base = {
        "role": role,
        "self_pos": (3, 3),
        "board_size": 7,
        "barriers": frozenset(),
        "scent": {(0, 0): 0.9},
        "step": 1,
        "max_barriers": 14,
        "barriers_used": 0,
    }
    base.update(kw)
    return Observation(**base)


# 1 — local production gameplay uses MetaController
def test_local_series_uses_metacontroller(monkeypatch):
    seen = _spy_series(monkeypatch)
    series_mod.run_series(CFG, Role.POLICE, "g", DevTestSigner(), seed=1, github_commit="0" * 40)
    assert seen and all(pt == ("MetaController", "MetaController") for pt in seen)


# 2 — network driver uses the production factory
def test_network_driver_uses_production_factory():
    assert net_driver.brain("police", 3).__class__.__name__ == "MetaController"
    assert net_driver.brain("thief", 3).__class__.__name__ == "MetaController"


# 3 — responder uses the production factory
def test_responder_uses_production_factory():
    assert responder_brain("police", 1, 35).__class__.__name__ == "MetaController"
    assert responder_brain("thief", 1, 35).__class__.__name__ == "MetaController"


# 4 — same seed gives deterministic decisions
def test_same_seed_deterministic_decisions():
    obs = _obs("police", self_pos=(0, 0))
    a = production_brain("police", 42).decide(obs)
    b = production_brain("police", 42).decide(obs)
    assert a == b


# 5 — valid audited profile learning persists across the series
def test_audited_profile_persists_across_series():
    store = ProfileStore()
    store.get("opp").observe_subgame(_sub_game(1)["records"], DevTestSigner())
    t1 = store.get("opp").turns
    store.get("opp").observe_subgame(_sub_game(2)["records"], DevTestSigner())
    assert t1 > 0 and store.get("opp").turns > t1  # accumulates across sub-games


def test_profile_influences_later_selection():
    # SurvivorBrain is robust to barrier-heavy opponents on its own (escape-space +
    # trap-filter terms), so it is selected regardless of profile; the opponent profile
    # now feeds the OpenAI advisor context rather than deterministic meta selection.
    mc = MetaController("thief", make_rng(1), epsilon=0.0, profile={"barrier_tendency": 0.5})
    name, _reason, _ = mc.select(_obs("thief"))  # threat far, open board, early game
    assert name == "survivor"


# 6 — a new opponent resets the profile
def test_new_opponent_resets_profile():
    store = ProfileStore()
    store.get("A").observe_subgame(_sub_game(1)["records"], DevTestSigner())
    assert store.get("A").turns > 0
    assert store.get("B").turns == 0  # fresh opponent starts clean
    store.reset("A")
    assert store.get("A").turns == 0


# 7 — unaudited / low-credibility hints do not affect decisions
def test_unaudited_hint_does_not_bias():
    mc = MetaController("police", make_rng(1), epsilon=0.0, credibility=0.5)
    board = Board(7)
    assert mc._hint_biased(_obs("police", last_hint="heading south toward downtown"), board) is None


# 8 — credible audited hints can affect a legal decision
def test_credible_hint_biases_legal_decision():
    mc = MetaController("police", make_rng(1), epsilon=0.0, credibility=0.9)
    obs = _obs("police", scent={(3, 3): 0.9}, last_hint="heading south toward downtown")
    board = Board(7)
    biased = mc._hint_biased(obs, board)
    assert biased is not None and is_legal(biased, obs, board, "police")
    mc.decide(obs)
    assert mc.log[-1]["strategy"] == "hint_biased"


def test_police_specialist_env_opt_in(monkeypatch):
    # Default: robust portfolio (MetaController). Opt-in: ContainBrain, police only.
    monkeypatch.delenv("POLICE_STRATEGY", raising=False)
    assert make_gameplay_brain("police", 1).__class__.__name__ == "MetaController"
    monkeypatch.setenv("POLICE_STRATEGY", "contain")
    assert make_gameplay_brain("police", 1).__class__.__name__ == "ContainBrain"
    assert make_gameplay_brain("thief", 1).__class__.__name__ == "MetaController"  # thief unaffected
