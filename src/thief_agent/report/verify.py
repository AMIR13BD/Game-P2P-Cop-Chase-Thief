"""Cross-artifact final audit. Fail closed on missing/malformed/mismatched/reordered
evidence; return precise diagnostics (never raise to the caller)."""

import hashlib
import json
import os

from ..domain.crypto import canonical_json
from ..peer.audit import run_audit
from . import ids, schemas
from .artifacts import log_sha256, terms_of


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _ordered(records: list) -> bool:
    steps = [r["payload"]["step"] for r in records]
    return steps == sorted(steps)  # non-decreasing (two half-turns share a step index)


def verify_series(dirpath: str, gid: str, signer=None) -> dict:
    fails: list[str] = []
    guid = ids.game_uid(gid)
    try:
        decl = schemas.validate(
            "declaration", _load(os.path.join(dirpath, ids.declaration_name(gid)))
        )
        result = schemas.validate("result", _load(os.path.join(dirpath, ids.result_name(gid))))
        for art, name in ((decl, "declaration"), (result, "result")):
            if art["game_uid"] != guid:
                fails.append(f"{name} game_uid mismatch")
        recomputed = hashlib.sha256(canonical_json(result["final_result"]).encode()).hexdigest()
        if recomputed != result["mutual_agreement"]["sha256"]:
            fails.append("result mutual_agreement hash mismatch")
        for entry in result["sub_games"]:
            nn = entry["sub_game_number"]
            cfg = schemas.validate("config", _load(os.path.join(dirpath, ids.config_name(gid, nn))))
            log = schemas.validate("log", _load(os.path.join(dirpath, ids.log_name(gid, nn))))
            if cfg["game_uid"] != guid or log["game_uid"] != guid:
                fails.append(f"g{nn}: game_uid mismatch")
            csha = hashlib.sha256(canonical_json(terms_of(cfg)).encode()).hexdigest()
            if not (csha == cfg["config_sha256"] == entry["config_sha256"]):
                fails.append(f"g{nn}: config_sha256 link broken")
            if not _ordered(log["records"]):
                fails.append(f"g{nn}: records reordered")
            audit = run_audit(log["records"], signer)
            if not audit["passed"] or not log["summary"]["audit"]["passed"]:
                fails.append(f"g{nn}: log audit failed {audit['failed_steps']}")
            if log_sha256(log["records"]) != entry["log_sha256"]:
                fails.append(f"g{nn}: log_sha256 link broken")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        fails.append(f"{type(exc).__name__}: {exc}")
    return {"passed": not fails, "failures": fails, "game_id": gid}


def agree(result_self: dict, result_peer: dict) -> bool:
    return result_self["mutual_agreement"]["sha256"] == result_peer["mutual_agreement"]["sha256"]
