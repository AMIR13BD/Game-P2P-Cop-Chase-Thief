from thief_agent.domain import smell as s
from thief_agent.domain.board import Board


def test_kernel_exact_values():
    d = s.emission_delta((3, 3), Board(7))
    assert d[(3, 3)] == 0.90  # center
    assert d[(3, 4)] == 0.62 and d[(2, 3)] == 0.62  # orthogonal neighbor
    assert d[(4, 4)] == 0.42  # diagonal neighbor
    assert d[(3, 5)] == 0.20 and d[(5, 3)] == 0.20  # distance-two orthogonal
    assert d[(4, 5)] == 0.14  # (1,2) offset
    assert d[(5, 5)] == 0.04  # corner of the 5x5 field


def test_edge_clipping():
    d = s.emission_delta((0, 0), Board(7))
    assert (-1, 0) not in d and (0, -1) not in d
    assert len(d) == 9  # only the in-bounds 3x3 quadrant
    assert d[(0, 0)] == 0.90 and d[(2, 2)] == 0.04


def test_one_deposit_then_one_decay_is_081():
    assert abs(s.decay({(3, 3): 0.90}, 0.10)[(3, 3)] - 0.81) < 1e-9


def test_repeated_emission_caps_at_max():
    b = Board(7)
    g = s.step_update({}, (3, 3), b, 0.10)
    g = s.step_update(g, (3, 3), b, 0.10)
    assert g[(3, 3)] == 0.9


def test_historical_trail_persists_after_move():
    b = Board(7)
    g = s.step_update({}, (3, 3), b, 0.10)  # deposit at (3,3)
    g = s.step_update(g, (0, 0), b, 0.10)  # emitter moves far away
    assert 0.0 < g[(3, 3)] < 0.9  # old trail decayed but persists
