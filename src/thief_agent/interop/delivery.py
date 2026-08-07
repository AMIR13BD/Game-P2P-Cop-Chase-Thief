"""The at-least-once receiver contract (SPEC §7.1) — exactly-once logical processing.

HTTP is at-least-once: a push whose ack is lost is retried by a correct client, so the
same message arrives twice by design. ``delivery_decision`` is an independent
re-implementation of the reference truth table (locked by the kit's
``vectors/delivery_contract.json``); ``Inbox`` is the state it reads. Keyed on the
COMMIT, not (kind, step): a redelivery cannot vary its commit, so a second DIFFERENT
commit for a played step stays loud as tampering evidence.
"""

from dataclasses import dataclass, field


class EquivocationError(Exception):
    """A second, DIFFERENT commit for a step already played — tampering evidence."""


class ProtocolViolationError(Exception):
    """An arrival past the reorder window — the flood rule."""


def delivery_decision(state: dict, arrival: dict) -> str:
    """absorb | discard | equivocation | apply | buffer | violation (SPEC §7.1)."""
    played, step, commit = state["played"], arrival["step"], arrival["commit"]
    if str(step) in played or step in played:
        seen = played.get(str(step), played.get(step))
        return "absorb" if seen == commit else "equivocation"
    if step == state["next"]:
        return "apply"
    if step < state["next"]:
        return "discard"  # below next and never played -> can never apply
    if step - state["next"] <= state["window"]:
        return "buffer"
    return "violation"


@dataclass
class Inbox:
    """Ordered, exactly-once delivery over an unordered, duplicating transport."""

    window: int = 4
    next_step: int = 1
    played: dict = field(default_factory=dict)
    buffered: dict = field(default_factory=dict)
    absorbed: int = 0

    def _state(self) -> dict:
        return {
            "played": {str(k): v for k, v in self.played.items()},
            "window": self.window,
            "next": self.next_step,
        }

    def offer(self, message: dict) -> list[dict]:
        """Take one inbound message; return messages now ready to apply, in step order.

        Empty list = nothing to do yet (absorbed duplicate or buffered ahead of a gap);
        never "something went wrong" — that is an exception.
        """
        arrival = {"step": int(message["step"]), "commit": message["commit"]}
        decision = delivery_decision(self._state(), arrival)
        if decision in ("absorb", "discard"):
            self.absorbed += 1
            return []
        if decision == "equivocation":
            raise EquivocationError(
                f"step {arrival['step']} already played under {self.played.get(arrival['step'])}, "
                f"different commit {arrival['commit']} arrived — two commitments for one step"
            )
        if decision == "violation":
            raise ProtocolViolationError(
                f"step {arrival['step']} is more than {self.window} ahead of next "
                f"({self.next_step}) — past the reorder window"
            )
        if decision == "buffer":
            self.buffered[arrival["step"]] = message
            return []
        ready = [message]
        self.played[arrival["step"]] = arrival["commit"]
        self.next_step = arrival["step"] + 1
        while self.next_step in self.buffered:
            nxt = self.buffered.pop(self.next_step)
            self.played[self.next_step] = nxt["commit"]
            ready.append(nxt)
            self.next_step += 1
        return ready
