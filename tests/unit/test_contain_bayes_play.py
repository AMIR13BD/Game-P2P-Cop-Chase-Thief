"""ContainBayes police, play half: legality/determinism against evaders, the
cornered-stationary-thief case, the no-hidden-state guarantee, opt-in selection, and
that the plain `contain` police stays untouched. Filter-internals tests live in
test_contain_bayes.py."""

import inspect

from thief_agent.domain.board import Board
from thief_agent.domain.smell import emission_delta
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy.base import Action, BrainBase
from thief_agent.strategy.police_contain import ContainBrain
from thief_agent.strategy.police_contain_bayes import ContainBayesBrain
from thief_agent.strategy.production import police_specialist
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_distance import ThiefDistanceBrain

CFG = validate(DEFAULT_GAME_CONFIG)

N = CFG["grid_size"]

EMPTY = frozenset()


def _game(police, thief):
    return run_sub_game(
        police, thief, {**CFG, "sub_game_number": 1}, "t", DevTestSigner(), "0" * 40
    )


def _sup(b):
    return {c for c, p in b.items() if p > 1e-9}


class _Adversary(BrainBase):
    """Direction changes + reversals + STAY (stresses delta tracking); always legal."""

    SEQ = ["S", "S", "STAY", "N", "E", "STAY", "W", "S"]
    D = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1), "STAY": (0, 0)}

    def __init__(self, rng):
        super().__init__(rng)
        self.t = 0

    def decide(self, obs):
        board = Board(obs.board_size, set(obs.barriers))
        d = self.SEQ[self.t % len(self.SEQ)]
        self.t += 1
        dr, dc = self.D[d]
        if d == "STAY" or not board.passable((obs.self_pos[0] + dr, obs.self_pos[1] + dc)):
            return Action("STAY")
        return Action("MOVE", d)


def test_legal_deterministic_and_captures_evaders():
    for thief in (_Adversary, ThiefDistanceBrain):
        a = _game(ContainBayesBrain(make_rng(0), seed=0), thief(make_rng(7)))
        b = _game(ContainBayesBrain(make_rng(0), seed=0), thief(make_rng(7)))
        assert a["illegal"] == 0 and a["diagonal"] == 0
        assert a["outcome"] == b["outcome"] and a["steps"] == b["steps"]
    res = _game(ContainBayesBrain(make_rng(0), seed=0), ThiefDistanceBrain(make_rng(7)))
    assert res["outcome"] == "capture" and res["steps"] <= CFG["max_moves"]


def test_stationary_thief_is_legal_and_cornered():
    class _Stay(BrainBase):
        def decide(self, obs):
            return Action("STAY")

    res = _game(ContainBayesBrain(make_rng(0), seed=0), _Stay(make_rng(1)))
    assert res["illegal"] == 0 and res["outcome"] == "capture"


def test_no_hidden_state_only_board_and_scent():
    assert set(inspect.signature(ContainBayesBrain._locate).parameters) == {
        "self",
        "board",
        "scent",
    }
    board, s = Board(N), emission_delta((5, 2), Board(N))
    e1 = ContainBayesBrain(make_rng(0), seed=0)._locate(board, dict(s))
    e2 = ContainBayesBrain(make_rng(0), seed=0)._locate(board, dict(s))
    assert e1 == e2 and board.in_bounds(e1)  # depends only on scent+board


def test_selection_is_opt_in(monkeypatch):
    monkeypatch.delenv("POLICE_STRATEGY", raising=False)
    assert police_specialist(0, 35) is None
    monkeypatch.setenv("POLICE_STRATEGY", "contain")
    assert type(police_specialist(0, 35)).__name__ == "ContainBrain"
    monkeypatch.setenv("POLICE_STRATEGY", "contain_bayes")
    assert type(police_specialist(0, 35)).__name__ == "ContainBayesBrain"


def test_old_contain_untouched_and_subclass_reuse():
    a = _game(ContainBrain(make_rng(0), seed=0), ThiefDistanceBrain(make_rng(7)))
    b = _game(ContainBrain(make_rng(0), seed=0), ThiefDistanceBrain(make_rng(7)))
    assert a["illegal"] == 0 and a["outcome"] == b["outcome"] and a["steps"] == b["steps"]
    assert issubclass(ContainBayesBrain, ContainBrain)
    assert ContainBayesBrain.decide is ContainBrain.decide
    assert ContainBayesBrain._locate is not ContainBrain._locate
