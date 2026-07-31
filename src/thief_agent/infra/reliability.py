"""Reliability wrapper around an async transport send: request IDs + correlation,
idempotency/dedup, timeout, retry+backoff, gatekeeper admission, deadline, and a
deterministic technical-loss on exhausted/defined failures. Bounded memory."""

import anyio

from ..exceptions import ExhaustedRetriesError, ProtocolError, QueueFullError, RateLimitError
from ..peer.technical import technical_result


class ReliableCaller:
    def __init__(
        self,
        send,
        *,
        timeout_s: float,
        retries: int,
        backoff_s: float,
        gatekeeper=None,
        deadline=None,
        session_id: str = "s",
        cache_max: int = 256,
    ) -> None:
        self._send = send
        self.timeout = timeout_s
        self.retries = max(1, retries)
        self.backoff = backoff_s
        self.gk = gatekeeper
        self.deadline = deadline
        self.session_id = session_id
        self.cache_max = cache_max
        self._seen: dict = {}
        self._order: list = []
        self._seq = 0

    def _next_id(self) -> str:
        self._seq += 1
        return f"{self.session_id}-{self._seq}"

    def _bound(self) -> None:
        while len(self._order) > self.cache_max:
            self._seen.pop(self._order.pop(0), None)

    async def _attempt(self, rid: str, payload: dict) -> dict:
        last: Exception | None = None
        for i in range(self.retries):
            try:
                if self.deadline is not None:
                    self.deadline.check()
                with anyio.fail_after(self.timeout):
                    resp = await self._send(
                        {"request_id": rid, "session_id": self.session_id, "payload": payload}
                    )
                if not isinstance(resp, dict):
                    raise ProtocolError("malformed response")
                if resp.get("request_id") != rid:
                    raise ProtocolError("response correlation mismatch")
                if resp.get("session_id") != self.session_id:
                    raise ProtocolError("stale session")
                return resp
            except (TimeoutError, ConnectionError, ProtocolError) as exc:
                last = exc
                if i < self.retries - 1:
                    await anyio.sleep(self.backoff)
        raise ExhaustedRetriesError(f"after {self.retries} tries: {last}")

    async def call(self, payload: dict, request_id: str | None = None) -> dict:
        rid = request_id or self._next_id()
        if rid in self._seen:  # duplicate request -> cached response (idempotent)
            return self._seen[rid]
        if self.gk is not None:
            self.gk.admit()
        try:
            resp = await self._attempt(rid, payload)
        finally:
            if self.gk is not None:
                self.gk.release()
        self._seen[rid] = resp
        self._order.append(rid)
        self._bound()
        return resp

    async def call_or_technical(self, payload: dict) -> dict:
        try:
            return await self.call(payload)
        except (ExhaustedRetriesError, ProtocolError, RateLimitError, QueueFullError) as exc:
            return technical_result(f"{type(exc).__name__}: {exc}")
