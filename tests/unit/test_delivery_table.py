"""The at-least-once receiver contract, as the published cross-team decision table.

HTTP is at-least-once: a push whose ack is lost is retried by a CORRECT client, so the
same message arrives twice by design. Dedupe is keyed on the COMMIT, never on
(kind, step) — a second DIFFERENT commit for a played step is equivocation and must stay
loud rather than collapsing silently into the redelivery row.
"""

import pytest

from thief_agent.interop.delivery import delivery_decision

STATE: dict = {"played": {"1": "c1", "2": "c2"}, "window": 2, "next": 3}

TABLE: list[tuple[int, str, str]] = [
    (3, "c3", "apply"),  # the next expected step
    (2, "c2", "absorb"),  # redelivery: SAME commit for a played step
    (2, "cX", "equivocation"),  # a DIFFERENT commit for a played step
    (4, "c4", "buffer"),  # one ahead, inside the reorder window
    (5, "c5", "buffer"),  # at the window bound
    (6, "c6", "violation"),  # past the window -> the flood rule
    (0, "c0", "discard"),  # below `next` and never played
]


@pytest.mark.parametrize(("step", "commit", "decision"), TABLE)
def test_delivery_decision_matches_the_agreed_table(step, commit, decision):
    assert delivery_decision(STATE, {"step": step, "commit": commit}) == decision
