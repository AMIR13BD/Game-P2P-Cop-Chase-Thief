"""P14 Thief portfolio: legality (firewall never substitutes), no diagonals,
determinism, controlled randomisation reproducibility, and endgame survival search."""

from thief_agent.domain.board import Board
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy import (
    thief_endgame,
    thief_entropy,
    thief_escape,
    thief_evade,
    thief_hybrid,
)
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import enforce
from thief_agent.strategy.police_greedy import PoliceGreedyBrain
from thief_agent.strategy.rng import make_rng

BRAINS = [
    thief_escape.EscapeBrain,
    thief_evade.EvadeBrain,
    thief_entropy.EntropyBrain,
    thief_endgame.EndgameBrain,
    thief_hybrid.ThiefHybridBrain,
]


def _rand_obs(rng):
    n = rng.randint(4, 7)
    cells = [(r, c) for r in range(n) for c in range(n)]
    barriers = frozenset(rng.sample(cells, rng.randint(0, n)))
    free = [c for c in cells if c not in barriers]
    pos = rng.choice(free)
    scent = {rng.choice(free): round(rng.random(), 3) for _ in range(rng.randint(0, 4))}
    return Observation(
        role="thief",
        self_pos=pos,
        board_size=n,
        barriers=barriers,
        scent=scent,
        step=rng.randint(1, 30),
        max_barriers=14,
        barriers_used=0,
    )


def test_thief_brains_emit_legal_nondiagonal_actions():
    rng = make_rng(4)
    for cls in BRAINS:
        brain = cls(make_rng(2))
        for _ in range(120):
            obs = _rand_obs(rng)
            board = Board(obs.board_size, set(obs.barriers))
            act = brain.decide(obs)
            _, substituted = enforce(act, obs, board, "thief")
            assert not substituted, (cls.__name__, act)
            assert act.kind != "BARRIER"  # thieves can never place barriers
            assert not (act.kind == "MOVE" and act.direction not in ("N", "S", "E", "W"))


def test_thief_brains_zero_illegal_in_full_game():
    cfg = validate(DEFAULT_GAME_CONFIG)
    for cls in BRAINS:
        res = run_sub_game(
            PoliceGreedyBrain(make_rng(5)),
            cls(make_rng(9)),
            {**cfg, "sub_game_number": 1},
            "grp",
            DevTestSigner(),
            "0" * 40,
        )
        assert res["illegal"] == 0 and res["diagonal"] == 0


def test_entropy_is_seed_reproducible():
    obs = Observation(
        role="thief",
        self_pos=(3, 3),
        board_size=7,
        barriers=frozenset(),
        scent={(0, 0): 0.9},
        step=3,
        max_barriers=14,
        barriers_used=0,
    )
    a = [thief_entropy.EntropyBrain(make_rng(7)).decide(obs) for _ in range(3)]
    assert a[0] == a[1] == a[2]  # same seed -> identical controlled-random choice


def test_endgame_prefers_survival():
    # Open board, pursuer inferred far away: endgame must not walk into it.
    obs = Observation(
        role="thief",
        self_pos=(3, 3),
        board_size=7,
        barriers=frozenset(),
        scent={(3, 4): 0.9},
        step=32,
        max_barriers=14,
        barriers_used=0,
    )
    act = thief_endgame.EndgameBrain(make_rng(1)).decide(obs)
    assert act.kind in ("MOVE", "STAY")
    if act.kind == "MOVE":  # never step toward the single inferred pursuer cell
        from thief_agent.domain.rules import step as step_move

        assert step_move((3, 3), act.direction) != (3, 4)
