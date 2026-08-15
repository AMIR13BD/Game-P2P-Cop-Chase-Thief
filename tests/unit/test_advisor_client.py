"""OpenAI advisor, client half: no-key fallback, usage accounting and response
parsing, malformed-output fallback, and that the AI-primary brain stays deterministic
with no API available. Advisor policy/veto tests live in test_advisor.py."""

import json

from thief_agent.advisor.client import OpenAIClient
from thief_agent.advisor.features import candidate_actions, tactical_context
from thief_agent.domain.board import Board
from thief_agent.domain.smell import step_update
from thief_agent.strategy.ai_brain import AIPrimaryBrain
from thief_agent.strategy.base import Observation
from thief_agent.strategy.belief import BeliefMap
from thief_agent.strategy.firewall import is_legal
from thief_agent.strategy.rng import make_rng


class MockClient:
    def __init__(self, reply, available=True):
        self.reply, self.available = reply, available
        self.usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "errors": 0}
        self.latencies = []

    def choose(self, system, payload):
        self.usage["calls"] += 1
        return self.reply


def _obs(role, self_pos, opp, step=8, barriers=frozenset()):
    return Observation(
        role=role,
        self_pos=self_pos,
        board_size=7,
        barriers=barriers,
        scent=step_update({}, opp, Board(7), 0.1),
        step=step,
        max_barriers=14,
        barriers_used=0,
    )


def _peak(obs, board):
    bel = BeliefMap(board)
    bel.update(obs.scent)
    return bel.argmax()


def _ctx(obs, recommended="A0"):
    board = Board(obs.board_size, set(obs.barriers))
    cands = candidate_actions(obs, board, _peak(obs, board))
    return tactical_context(obs, board, cands, recommended, {}, 35), cands


class _FakeResp:
    def __init__(self, text, usage):
        self.output_text, self.usage = text, usage


class _FakeSDK:
    def __init__(self, text, usage):
        self._text, self._usage = text, usage
        self.responses = self

    def create(self, **kw):
        return _FakeResp(self._text, self._usage)


def test_openai_client_no_key_returns_none():
    import os

    saved = os.environ.pop("OPENAI_API_KEY", None)
    try:
        assert OpenAIClient().choose("s", {"x": 1}) is None
    finally:
        if saved is not None:
            os.environ["OPENAI_API_KEY"] = saved


def test_openai_client_records_usage_and_parses():
    usage = type("U", (), {"input_tokens": 40, "output_tokens": 3})()
    c = OpenAIClient()
    c.available = True
    c._client = _FakeSDK(json.dumps({"action_id": "A2"}), usage)
    assert c.choose("sys", {"role": "thief"}) == "A2"
    assert c.usage["calls"] == 1 and c.usage["input_tokens"] == 40


def test_openai_client_malformed_output_falls_back():
    c = OpenAIClient()
    c.available = True
    c._client = _FakeSDK("not json", None)
    assert c.choose("s", {}) is None and c.usage["errors"] == 1


def test_ai_brain_deterministic_without_api():
    obs = _obs("thief", (3, 3), (0, 0))
    ai = AIPrimaryBrain(
        "thief", make_rng(2), horizon=35, policy="C", client=MockClient(None, False)
    )
    assert is_legal(ai.decide(obs), obs, Board(7), "thief")
