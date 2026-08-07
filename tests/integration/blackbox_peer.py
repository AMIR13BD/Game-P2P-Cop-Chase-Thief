"""An INDEPENDENT minimal reference-v3 peer built ONLY from the wire spec, stdlib alone.

It imports NONE of our adapter (no server/client/negotiate/engine/wire/crypto module),
re-derives every construction from scratch, and plays a full series against our runtime.
This approximates a random compliant student team (SPEC §15). Natural role: thief."""

import hashlib
import json
import queue
import secrets
import uuid

MAX_STEPS = 35


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def commit(payload, nonce):
    return hashlib.sha256(f"{canon(payload)}|{nonce}".encode()).hexdigest()


def game_uid(terms, a, b):
    pair = sorted([a, b])
    return str(
        uuid.UUID(bytes=hashlib.sha256(f"{canon(terms)}|{'|'.join(pair)}".encode()).digest()[:16])
    )


class BlackBoxPeer:
    def __init__(self, group, terms, own, peer):
        self.group = group
        self.terms = terms
        self.own = own
        self.peer = peer
        self.results: list = []

    def _poll(self, name, timeout):
        try:
            return getattr(self.own, name).get(timeout=timeout)
        except queue.Empty:
            return None

    def run_series(self, num_games=6):
        known = None
        for n in range(1, num_games + 1):
            role = "thief" if n % 2 == 1 else "police"
            nonce = secrets.token_hex(16)
            greeting = {
                "terms": self.terms,
                "nonce": nonce,
                "signature": commit(self.terms, nonce),
                "group_id": self.group,
                "role": role,
                "sub_game_number": n,
                "identity": {"group_id": self.group},
            }
            if known:
                greeting["game_uid"] = game_uid(self.terms, self.group, known)
            self.peer.agreements.put(greeting)
            theirs = self._poll("agreements", 10)
            known = theirs.get("group_id") or theirs["identity"]["group_id"]
            self.results.append(self._play(role, n, known))

    def _record(self, step, role, pos):
        nonce = secrets.token_hex(16)
        payload = {
            "step": step,
            "role": role,
            "state": f"self={list(pos)}",
            "move": "STAY",
            "intent": "truth",
            "hint": "bb",
        }
        return {"payload": payload, "nonce": nonce, "commit": commit(payload, nonce)}

    def _turn(self, step, role, records, pos, response, survived):
        return {
            "step": step,
            "sender": role,
            "commit": records[-1]["commit"],
            "hint": "bb",
            "smell_grid": {},
            "timestamp": "",
            "barrier_placed": None,
            "capture_claim": (list(pos) if role == "police" else None),
            "claim_response": response,
            "win_claim": ({"type": "survival"} if survived else None),
        }

    def _play(self, role, n, opponent):
        start = self.terms["thief_start"] if role == "thief" else self.terms["cop_start"]
        pos = tuple(start)
        records = [self._record(0, role, pos)]
        state = {"step": 0, "pending": None}

        def my_turn():
            state["step"] += 1
            records.append(self._record(state["step"], role, pos))
            survived = role == "thief" and state["step"] >= MAX_STEPS
            self.peer.turns.put(
                self._turn(state["step"], role, records, pos, state["pending"], survived)
            )
            state["pending"] = None
            return survived

        result = "survival" if (role == "thief" and my_turn()) else None
        while result is None:
            incoming = self._poll("turns", 8)
            if incoming is None:
                result = "timeout"
            elif role == "police" and (incoming.get("claim_response") or {}).get("caught"):
                result = "capture"
            elif incoming.get("win_claim"):
                result = "survival"
            else:
                if role == "thief" and incoming.get("capture_claim") is not None:
                    caught = list(pos) == incoming["capture_claim"]
                    state["pending"] = {"claim": incoming["capture_claim"], "caught": caught}
                    if caught:
                        my_turn()
                        result = "capture"
                        continue
                if my_turn():
                    result = "survival"
        return self._audit(role, records, result)

    def _audit(self, role, records, result):
        self.peer.audits.put({"sender": role, "records": records, "result_claim": result})
        theirs = self._poll("audits", 8)
        ok = theirs is not None and all(
            commit(r["payload"], r["nonce"]) == r["commit"] for r in theirs["records"]
        )
        return {"role": role, "result": result, "opponent_audit_ok": ok}
