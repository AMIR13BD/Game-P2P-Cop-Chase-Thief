from thief_agent.domain.scoring import score_outcome


def test_fixed_scoring():
    assert score_outcome("capture") == (20, 5)
    assert score_outcome("survival") == (5, 10)
    assert score_outcome("technical") == (0, 0)
