"""Server-side idempotency: dedup by (session, request_id). A repeated request_id
returns the cached response without re-processing; a changed payload is rejected.
Bounded (LRU-ish eviction) and scoped by the authenticated session token."""

import hashlib

from ..domain.crypto import canonical_json


class IdemCache:
    def __init__(self, cap: int = 512) -> None:
        self.cap = cap
        self._d: dict = {}
        self._order: list = []

    @staticmethod
    def fingerprint(payload: dict) -> str:
        body = {k: v for k, v in payload.items() if k not in ("_rid", "_sid")}
        return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()

    def get_or_run(self, key, fingerprint: str, compute):
        if key in self._d:
            old_fp, resp = self._d[key]
            if old_fp != fingerprint:
                raise ValueError("request id reused with a different payload")
            return resp
        resp = compute()
        self._d[key] = (fingerprint, resp)
        self._order.append(key)
        while len(self._order) > self.cap:
            self._d.pop(self._order.pop(0), None)
        return resp
