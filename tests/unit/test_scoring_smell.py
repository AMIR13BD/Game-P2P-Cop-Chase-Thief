from thief_agent.domain.board import Board
from thief_agent.domain.scoring import score_outcome
from thief_agent.domain.smell import decay, emit


def test_fixed_scoring():
    assert score_outcome("capture") == (20, 5)
    assert score_outcome("survival") == (5, 10)
    assert score_outcome("technical") == (0, 0)


def test_emission_centre_and_radial():
    b = Board(7)
    g: dict = {}
    emit(g, (3, 3), b, 0.9, 5)
    assert g[(3, 3)] == 0.9
    assert 0 < g[(3, 4)] < 0.9  # radial falloff


def test_decay_rate():
    g = {(3, 3): 0.9}
    d = decay(g, 0.10)
    assert abs(d[(3, 3)] - 0.81) < 1e-9
