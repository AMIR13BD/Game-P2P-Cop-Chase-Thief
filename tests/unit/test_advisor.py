"""OpenAI tactical-advisor tests. ZERO real API calls (mock client / fake SDK): proves
fallback safety, hard-safety veto, strict validation, compact/legal/no-hidden-truth
context, usage tracking, and key hygiene."""

import json

from thief_agent.advisor.advisor import TacticalAdvisor
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
    return Observation(role=role, self_pos=self_pos, board_size=7, barriers=barriers,
                       scent=step_update({}, opp, Board(7), 0.1), step=step,
                       max_barriers=14, barriers_used=0)


def _peak(obs, board):
    bel = BeliefMap(board)
    bel.update(obs.scent)
    return bel.argmax()


def _ctx(obs, recommended="A0"):
    board = Board(obs.board_size, set(obs.barriers))
    cands = candidate_actions(obs, board, _peak(obs, board))
    return tactical_context(obs, board, cands, recommended, {}, 35), cands


def test_missing_key_falls_back():
    obs = _obs("thief", (3, 3), (0, 0))
    adv = TacticalAdvisor(MockClient(None, available=False), policy="C")
    assert adv.select(obs, _ctx(obs)[0], "A0") == ("A0", "det-skip")


def test_valid_choice_accepted():
    obs = _obs("thief", (3, 3), (0, 0))
    ctx, _ = _ctx(obs)
    adv = TacticalAdvisor(MockClient(ctx["candidates"][1]["id"]), policy="C")
    aid, source = adv.select(obs, ctx, "A0")
    assert source == "openai" and aid == ctx["candidates"][1]["id"]


def test_invalid_action_id_falls_back():
    obs = _obs("thief", (3, 3), (0, 0))
    adv = TacticalAdvisor(MockClient("A999"), policy="C")
    assert adv.select(obs, _ctx(obs)[0], "A0") == ("A0", "fallback")


def test_hard_safety_veto_blocks_unsafe_thief_move():
    # Cop two cells away: stepping toward it is capturable-next, but a safe move exists,
    # so the deterministic layer must VETO the model's unsafe pick.
    obs = _obs("thief", (3, 3), (3, 5), step=10)
    ctx, _ = _ctx(obs)
    unsafe = [c["id"] for c in ctx["candidates"] if c.get("capturable_next") or c["opp_distance"] == 0]
    safe = [c for c in ctx["candidates"] if not c.get("capturable_next") and c["opp_distance"] != 0]
    assert unsafe and safe, "need both a safe and an unsafe candidate for this test"
    aid, source = TacticalAdvisor(MockClient(unsafe[0]), policy="C").select(obs, ctx, "A0")
    assert source == "veto" and aid == "A0"


def test_candidates_are_all_legal():
    obs = _obs("police", (3, 3), (4, 4))
    board = Board(7)
    for act in candidate_actions(obs, board, _peak(obs, board)):
        assert is_legal(act, obs, board, "police")


def test_context_compact_and_no_hidden_truth():
    obs = _obs("thief", (3, 3), (1, 1))
    ctx, _ = _ctx(obs)
    assert set(ctx) == {"role", "turn", "max_turns", "board_size", "self", "belief_peak",
                        "remaining_barriers", "opponent_profile", "recommended_id", "candidates"}
    assert len(ctx["candidates"]) <= 9
    assert "sk-" not in json.dumps(ctx) and "OPENAI_API_KEY" not in json.dumps(ctx)


def test_policy_b_only_calls_on_high_risk():
    adv = TacticalAdvisor(MockClient("A0"), policy="B")
    safe = _obs("thief", (3, 3), (0, 0), step=2)
    risky = _obs("thief", (5, 6), (5, 5), step=13)
    assert adv.should_call(safe, _ctx(safe)[0]) is False
    assert adv.should_call(risky, _ctx(risky)[0]) is True


def test_openai_client_no_key_returns_none():
    import os
    saved = os.environ.pop("OPENAI_API_KEY", None)
    try:
        assert OpenAIClient().choose("s", {"x": 1}) is None
    finally:
        if saved is not None:
            os.environ["OPENAI_API_KEY"] = saved


class _FakeResp:
    def __init__(self, text, usage):
        self.output_text, self.usage = text, usage


class _FakeSDK:
    def __init__(self, text, usage):
        self._text, self._usage = text, usage
        self.responses = self

    def create(self, **kw):
        return _FakeResp(self._text, self._usage)


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
    ai = AIPrimaryBrain("thief", make_rng(2), horizon=35, policy="C", client=MockClient(None, False))
    assert is_legal(ai.decide(obs), obs, Board(7), "thief")
