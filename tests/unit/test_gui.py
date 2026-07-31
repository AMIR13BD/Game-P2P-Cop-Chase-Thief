"""P21 GUI: local-truth board + scent, belief heatmap, status banner + input lock,
bounded event log, and the hidden-opponent-position guarantee."""

from thief_agent.gui.board_view import player_marker_count, render_board
from thief_agent.gui.event_log import EventLog
from thief_agent.gui.heatmap import belief_buckets, render_heatmap
from thief_agent.gui.status_banner import banner, input_locked
from thief_agent.gui.window import leaks_opponent_position, local_view
from thief_agent.strategy.base import Observation


def _obs(**kw):
    base = {
        "role": "police",
        "self_pos": (0, 0),
        "board_size": 7,
        "barriers": frozenset(),
        "scent": {(3, 3): 0.9},
        "step": 4,
        "max_barriers": 14,
        "barriers_used": 0,
    }
    base.update(kw)
    return Observation(**base)


def test_board_renders_only_local_player():
    board = render_board(7, (0, 0), "police", barriers={(1, 1)}, scent={(3, 3): 0.9})
    assert player_marker_count(board) == 1  # only self, never the opponent
    assert "#" in board and "*" in board  # barrier + strong scent overlays present


def test_board_accepts_string_scent_keys():
    board = render_board(5, (0, 0), "thief", scent={"2,2": 0.9})
    assert board.count("T") == 1 and "*" in board


def test_heatmap_buckets_normalised():
    buckets = belief_buckets(7, {(3, 3): 0.9})
    assert max(buckets.values()) == 9  # peak cell is the top bucket
    hm = render_heatmap(7, {(3, 3): 0.9}, barriers={(0, 0)})
    assert "#" in hm and "9" in hm


def test_empty_scent_heatmap_is_uniform_zero_peak():
    # no scent -> uniform belief -> peak bucket still 9 somewhere is not guaranteed; but
    # the renderer must not crash and stays within 0-9.
    hm = render_heatmap(5, {})
    assert all(ch in "0123456789 " for ch in hm.replace("\n", ""))


def test_banner_and_input_lock():
    assert "ONLINE" in banner("MOVE", 3, 30, True)
    assert "OFFLINE" in banner("COMMIT", 3, 30, False)
    assert input_locked("MOVE") is False
    assert input_locked("COMMIT") is True and input_locked("SUBGAME_DONE") is True


def test_event_log_is_bounded():
    log = EventLog(capacity=3)
    for i in range(10):
        log.append(f"e{i}")
    assert len(log) == 3
    assert log.tail(2) == ["e8", "e9"]
    assert log.render(1) == "e9"


def test_local_view_hides_opponent_position():
    obs = _obs(self_pos=(0, 0))
    view = local_view(obs, state="MOVE")
    assert view["input_locked"] is False and view["role"] == "police"
    # even knowing the (secret) opponent cell, the view never reveals it
    assert leaks_opponent_position(view, (3, 3)) is False
    assert leaks_opponent_position(view, (6, 6)) is False


def test_view_input_locked_off_turn():
    assert local_view(_obs(), state="REVEAL")["input_locked"] is True
