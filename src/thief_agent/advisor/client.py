"""Thin, defensive wrapper over the official OpenAI SDK (Responses API).

Contract: returns a chosen ``action_id`` string or ``None`` -- it NEVER raises and
NEVER blocks past its hard timeout, so the game always falls back deterministically.
Auth is read only from the ``OPENAI_API_KEY`` environment variable by the SDK; the
key is never read into a variable here, never logged, never returned, never stored.
Model is chosen via ``OPENAI_MODEL`` (falls back to ``DEFAULT_MODEL``)."""

import json
import os
import time

# Chosen after the real-state benchmark (fast, strong, reliable structured output);
# always overridable at runtime via OPENAI_MODEL without code changes.
DEFAULT_MODEL = "gpt-5.4-mini"

_SCHEMA = {
    "type": "json_schema",
    "name": "action_choice",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {"action_id": {"type": "string"}},
        "required": ["action_id"],
    },
}


def model_name() -> str:
    return os.environ.get("OPENAI_MODEL") or DEFAULT_MODEL


class OpenAIClient:
    """One client per agent. Lazily constructs the SDK client; degrades to None."""

    def __init__(self, timeout_s: float = 6.0) -> None:
        self.timeout_s = timeout_s
        self.available = bool(os.environ.get("OPENAI_API_KEY"))
        self._client = None
        self.usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "errors": 0}
        self.latencies: list[float] = []

    def _ensure(self):
        if self._client is None:
            from openai import OpenAI  # lazy: missing package => stays unavailable

            self._client = OpenAI(timeout=self.timeout_s, max_retries=0)
        return self._client

    def choose(self, system: str, payload: dict) -> str | None:
        """Ask the model to select an action_id. Returns the id or None (fallback)."""
        if not self.available:
            return None
        started = time.perf_counter()
        try:
            client = self._ensure()
            resp = client.responses.create(
                model=model_name(),
                input=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": json.dumps(payload, separators=(",", ":"))},
                ],
                text={"format": _SCHEMA},
                max_output_tokens=2000,
            )
            self.latencies.append(time.perf_counter() - started)
            self.usage["calls"] += 1
            usage = getattr(resp, "usage", None)
            if usage is not None:
                self.usage["input_tokens"] += getattr(usage, "input_tokens", 0) or 0
                self.usage["output_tokens"] += getattr(usage, "output_tokens", 0) or 0
            data = json.loads(resp.output_text)
            action_id = data.get("action_id")
            return action_id if isinstance(action_id, str) else None
        except Exception:  # any provider/timeout/parse failure => deterministic fallback
            self.usage["errors"] += 1
            self.latencies.append(time.perf_counter() - started)
            return None
