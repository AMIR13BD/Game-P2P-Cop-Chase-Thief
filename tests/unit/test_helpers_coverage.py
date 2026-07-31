"""Coverage of small boundary/helper modules: config file loading + merge, seed
sequences, server term assembly, git-commit fallback, batch counting, and the
belief/firewall/pathing edge branches not hit by the main behavioural tests."""

import json

from thief_agent.domain.board import Board
from thief_agent.domain.rules import legal_barrier_targets
from thief_agent.infra import serve
from thief_agent.shared import config, gitinfo
from thief_agent.sim import batch, seeds
from thief_agent.strategy.base import Action, Observation
from thief_agent.strategy.belief import BeliefMap
from thief_agent.strategy.firewall import is_legal
from thief_agent.strategy.pathing import bfs_first_step


def test_config_load_and_merge(tmp_path):
    jp = tmp_path / "game.json"
    jp.write_text(json.dumps({"grid_size": 7, "shared": True}), encoding="utf-8")
    tp = tmp_path / "game.toml"
    tp.write_text("grid_size = 5\nprivate = true\n", encoding="utf-8")
    shared = config.load_json(jp)
    private = config.load_toml(tp)
    merged = config.merge(private, shared)
    assert merged["grid_size"] == 7  # signed shared value wins
    assert merged["private"] is True and merged["shared"] is True


def test_seed_sequence():
    assert seeds.seed_sequence(100, 3) == [100, 101, 102]
    assert seeds.seed_sequence(0, 0) == []


def test_make_terms_default_and_grid_override():
    base = serve.make_terms()
    assert base["board_and_agents"]["grid_size"] == 7
    grid9 = serve.make_terms(grid=9)
    assert grid9["board_and_agents"]["grid_size"] == 9
    assert base["board_and_agents"]["grid_size"] == 7  # original not mutated


def test_gitinfo_falls_back_on_failure(monkeypatch):
    def boom(*a, **k):
        raise OSError("no git")

    monkeypatch.setattr(gitinfo.subprocess, "run", boom)
    assert gitinfo.current_commit(default="fallback") == "fallback"


def test_batch_counts_turns(cfg):
    res = batch.run_batch(cfg, min_turns=5, base_seed=1)
    assert res["turns"] >= 5 and res["sub_games"] >= 1
    assert set(res) >= {"turns", "illegal", "diagonal", "timeouts", "exceptions", "outcomes"}


def test_belief_empty_board_has_no_argmax():
    board = Board(2, {(0, 0), (0, 1), (1, 0), (1, 1)})  # every cell blocked
    bm = BeliefMap(board)
    bm.update({(0, 0): 9.0})  # all weights excluded -> empty distribution
    assert bm.dist == {} and bm.argmax() is None


def _obs(**kw):
    base = {
        "role": "police",
        "self_pos": (3, 3),
        "board_size": 7,
        "barriers": frozenset(),
        "scent": {},
        "last_hint": "",
        "step": 1,
        "max_barriers": 14,
        "barriers_used": 0,
    }
    base.update(kw)
    return Observation(**base)


def test_firewall_barrier_rules():
    board = Board(7)
    target = next(iter(legal_barrier_targets((3, 3), board)))
    assert is_legal(Action("BARRIER", target), _obs(), board, "police")
    # thief may never place a barrier
    assert not is_legal(Action("BARRIER", target), _obs(role="thief"), board, "thief")
    # police out of barrier budget
    assert not is_legal(Action("BARRIER", target), _obs(barriers_used=14), board, "police")


def test_bfs_returns_none_when_unreachable():
    board = Board(3, {(0, 1), (1, 0), (1, 1)})  # wall isolating (0,0)
    assert bfs_first_step(board, (0, 0), (2, 2)) is None
    assert bfs_first_step(board, (0, 0), (0, 0)) is None
