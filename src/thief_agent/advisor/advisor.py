"""Tactical advisor: decides WHEN to consult OpenAI (call policy A/B/C), validates
its choice against the deterministic legal candidate list, and otherwise returns the
deterministic pick. OpenAI can only ever move probability among legal candidates; it
can never produce an illegal action, protocol effect, or capture-claim change."""

SYSTEM = {
    "police": (
        "You are the tactical selector for the POLICE (cop) in a turn-based pursuit on an "
        "NxN grid. Orthogonal moves only; capture = occupying the thief's cell. Equal speed, "
        "so naive chasing fails: prefer candidates that cut off the thief's escape, reduce its "
        "reachable area, drive it toward an edge/corner, or place a value-positive barrier. "
        "Use opp_distance, mobility, reachable_area and the opponent profile. Choose exactly one "
        'candidate. Reply ONLY as {"action_id":"A#"} with an id from candidates.'
    ),
    "thief": (
        "You are the tactical selector for the THIEF in a turn-based pursuit on an NxN grid. "
        "Orthogonal moves only; you are caught if the cop reaches your cell. Survive to max_turns. "
        "NEVER pick a candidate with capturable_next=true unless all are. Prefer larger opp_distance "
        "and safe_exits, keep high mobility and reachable_area, and avoid corners/dead-ends where the "
        "cop could trap you in two moves. Choose exactly one candidate. Reply ONLY as "
        '{"action_id":"A#"} with an id from candidates.'
    ),
}


class TacticalAdvisor:
    """Wraps an OpenAIClient with a benchmarkable call policy and hard validation."""

    def __init__(self, client, policy: str = "B", endgame_window: int = 5) -> None:
        self.client = client
        self.policy = policy  # "A" ambiguous-only, "B" high-risk, "C" every turn
        self.endgame_window = endgame_window
        self.telemetry = {"turns": 0, "consults": 0, "accepted": 0, "overrides": 0, "fallback": 0}

    def _high_risk(self, obs, context) -> bool:
        cands = context["candidates"]
        near = min((c["opp_distance"] for c in cands if c["opp_distance"] >= 0), default=99)
        if context["role"] == "thief":
            if any(c.get("capturable_next") for c in cands):
                return True
            return near <= 3
        return near <= 3 or (context["max_turns"] - obs.step) <= self.endgame_window

    def should_call(self, obs, context) -> bool:
        if not self.client.available:
            return False
        if self.policy == "C":
            return True
        if self.policy == "A":
            return len(context["candidates"]) >= 3 and self._high_risk(obs, context)
        return self._high_risk(obs, context)

    def _unsafe_ids(self, context) -> set[str]:
        """Hard-safety veto set: OpenAI may never move the Thief onto a cell the cop can
        capture next turn while a safe candidate exists (the deterministic layer, not the
        model, owns hard safety). The Police has no such veto -- landing on the thief is a
        capture, which is the objective."""
        if context["role"] != "thief":
            return set()
        cands = context["candidates"]
        safe = [c for c in cands if not c.get("capturable_next") and c["opp_distance"] != 0]
        if not safe:
            return set()
        return {c["id"] for c in cands if c.get("capturable_next") or c["opp_distance"] == 0}

    def select(self, obs, context, recommended_id: str) -> tuple[str, str]:
        """Return (action_id, source). source in {det-skip, openai, veto, fallback}."""
        self.telemetry["turns"] += 1
        if not self.should_call(obs, context):
            return recommended_id, "det-skip"
        self.telemetry["consults"] += 1
        valid = {c["id"] for c in context["candidates"]}
        unsafe = self._unsafe_ids(context)
        chosen = self.client.choose(SYSTEM[context["role"]], context)
        if chosen in unsafe:  # model tried a hard-unsafe move -> deterministic veto
            self.telemetry["fallback"] += 1
            return recommended_id, "veto"
        if chosen in valid:
            self.telemetry["accepted"] += 1
            if chosen != recommended_id:
                self.telemetry["overrides"] += 1
            return chosen, "openai"
        self.telemetry["fallback"] += 1
        return recommended_id, "fallback"
