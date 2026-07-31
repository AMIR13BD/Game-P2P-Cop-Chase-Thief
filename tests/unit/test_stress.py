"""Legality + timeout stress (P13/P14/P16): across many seeded full games the
adaptive controllers and search brains never emit an illegal or diagonal action,
respect a tight decision deadline, and always return a legal move."""

import time

from thief_agent.domain.board import Board
from thief_agent.peer.turn_engine import run_sub_game
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG
from thief_agent.strategy.base import Observation
from thief_agent.strategy.firewall import is_legal
from thief_agent.strategy.meta import MetaController
from thief_agent.strategy.rng import make_rng
from thief_agent.strategy.thief_endgame import EndgameBrain

CFG = validate(DEFAULT_GAME_CONFIG)
HORIZON = CFG["survival_threshold"]


def test_meta_vs_meta_zero_illegal_over_many_seeds():
    for seed in range(1, 25):
        res = run_sub_game(
            MetaController("police", make_rng(seed), horizon=HORIZON, epsilon=0.2),
            MetaController("thief", make_rng(seed + 500), horizon=HORIZON, epsilon=0.2),
            {**CFG, "sub_game_number": 1},
            "grp",
            DevTestSigner(),
            "0" * 40,
        )
        assert res["illegal"] == 0 and res["diagonal"] == 0


def test_endgame_respects_tight_deadline_and_stays_legal():
    rng = make_rng(3)
    brain = EndgameBrain(make_rng(1), max_depth=50, deadline_s=0.005)
    for _ in range(60):
        n = rng.randint(4, 7)
        cells = [(r, c) for r in range(n) for c in range(n)]
        barriers = frozenset(rng.sample(cells, rng.randint(0, n)))
        free = [c for c in cells if c not in barriers]
        obs = Observation(
            role="thief",
            self_pos=rng.choice(free),
            board_size=n,
            barriers=barriers,
            scent={rng.choice(free): 0.9},
            step=rng.randint(28, 34),
            max_barriers=14,
            barriers_used=0,
        )
        t0 = time.perf_counter()
        act = brain.decide(obs)
        elapsed = time.perf_counter() - t0
        assert is_legal(act, obs, Board(n, set(barriers)), "thief")
        assert elapsed < 0.5  # generous ceiling; anytime search must stay bounded
