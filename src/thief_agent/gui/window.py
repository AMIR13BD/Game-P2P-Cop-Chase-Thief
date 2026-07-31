"""Live GUI view assembly with the hidden-opponent-position guarantee (P21).

`local_view` builds the whole renderable view from an Observation only -- own board,
belief heatmap, status banner, input lock. Because an Observation carries no opponent
position, the view provably cannot reveal it; `leaks_opponent_position` proves this by
checking that exactly one player marker is drawn and no true opponent cell is shown."""

from ..strategy.base import Observation
from .board_view import player_marker_count, render_board
from .heatmap import render_heatmap
from .status_banner import banner, input_locked


def local_view(
    obs: Observation, state: str = "MOVE", connected: bool = True, deadline_s=30
) -> dict:
    return {
        "board": render_board(obs.board_size, obs.self_pos, obs.role, obs.barriers, obs.scent),
        "heatmap": render_heatmap(obs.board_size, obs.scent, obs.barriers),
        "banner": banner(state, obs.step, deadline_s, connected),
        "input_locked": input_locked(state),
        "self_pos": list(obs.self_pos),
        "role": obs.role,
    }


def leaks_opponent_position(view: dict, opponent_pos) -> bool:
    """True if the view would reveal the opponent's true cell. It must always be False:
    the board draws exactly one player marker (the local player) and never the opponent."""
    if player_marker_count(view.get("board", "")) != 1:
        return True
    return f"self={list(opponent_pos)}" in (view.get("board", "") + view.get("heatmap", ""))
