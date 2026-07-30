from thief_agent.domain.board import Board
from thief_agent.domain.capture import barrier_captures, captured_by_landing, thief_trapped


def test_capture_by_landing():
    assert captured_by_landing((2, 2), (2, 2))
    assert not captured_by_landing((2, 2), (2, 3))


def test_barrier_on_thief_captures():
    assert barrier_captures((4, 4), (4, 4))
    assert not barrier_captures((4, 3), (4, 4))


def test_trapped_thief_corner_sealed():
    # corner (0,0): neighbors (1,0) and (0,1). Seal both -> trapped.
    b = Board(7, {(1, 0), (0, 1)})
    assert thief_trapped((0, 0), b)


def test_not_trapped_when_escape_exists():
    b = Board(7, {(1, 0)})
    assert not thief_trapped((0, 0), b)
