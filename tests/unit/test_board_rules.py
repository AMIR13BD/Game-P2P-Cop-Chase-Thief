from thief_agent.domain.board import Board
from thief_agent.domain.rules import barrier_cell, legal_barrier_targets, legal_move_dirs


def test_bounds_and_neighbors():
    b = Board(7)
    assert b.in_bounds((0, 0)) and not b.in_bounds((7, 0))
    assert set(b.neighbors((0, 0))) == {(1, 0), (0, 1)}  # corner: no diagonals, no off-board


def test_barriers_block():
    b = Board(7, {(0, 1)})
    assert not b.passable((0, 1))
    assert "E" not in legal_move_dirs((0, 0), b)
    assert "S" in legal_move_dirs((0, 0), b) and "STAY" in legal_move_dirs((0, 0), b)


def test_legal_move_dirs_only_orthogonal():
    b = Board(7)
    dirs = legal_move_dirs((3, 3), b)
    assert set(dirs) == {"STAY", "N", "S", "E", "W"}


def test_barrier_targets_and_cell():
    b = Board(7)
    assert barrier_cell((3, 3), "SELF") == (3, 3)
    assert barrier_cell((3, 3), "N") == (2, 3)
    assert "SELF" in legal_barrier_targets((3, 3), b)
