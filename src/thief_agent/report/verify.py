"""Cross-artifact audit. verify_series = integrity (hash links, per-record commit-
reveal, config schema, 6-sub-game count). verify_match = counted-match strictness
(per-peer signed declaration, distinct Git commits bound to each sub-game, and two
valid signed final-hash confirmations). Both fail closed with precise diagnostics."""

import hashlib
import json
import os

from ..domain.crypto import canonical_json
from ..peer.audit import run_audit
from . import ids, schemas
from .artifacts import log_sha256, terms_of

SUB_GAMES = 6


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _ordered(records: list) -> bool:
    steps = [r["payload"]["step"] for r in records]
    return steps == sorted(steps)


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
        nums = sorted(e["sub_game_number"] for e in result["sub_games"])
        if result["num_sub_games"] != SUB_GAMES or nums != list(range(1, SUB_GAMES + 1)):
            fails.append(f"series must have exactly {SUB_GAMES} sub-games, got {nums}")
        if (
            hashlib.sha256(canonical_json(result["final_result"]).encode()).hexdigest()
            != result["mutual_agreement"]["sha256"]
        ):
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
            if (
                not run_audit(log["records"], signer)["passed"]
                or not log["summary"]["audit"]["passed"]
            ):
                fails.append(f"g{nn}: log audit failed")
            if log_sha256(log["records"]) != entry["log_sha256"]:
                fails.append(f"g{nn}: log_sha256 link broken")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        fails.append(f"{type(exc).__name__}: {exc}")
    return {"passed": not fails, "failures": fails, "game_id": gid}


def verify_match(dirpath: str, gid: str, signer) -> dict:
    base = verify_series(dirpath, gid, signer)
    fails = list(base["failures"])
    try:
        decl = _load(os.path.join(dirpath, ids.declaration_name(gid)))
        result = _load(os.path.join(dirpath, ids.result_name(gid)))
        commits, by_group = [], {}
        for grp in decl["groups"].values():
            ident = {k: v for k, v in grp.items() if k != "signature"}
            if not signer.verify(ident, grp.get("signature", "")):
                fails.append(f"declaration signature invalid for {grp.get('group_id')}")
            commits.append(grp.get("github_commit"))
            by_group[grp["group_id"]] = grp.get("github_commit")
        if None in commits or len(set(commits)) < 2:
            fails.append("declaration Git commits are not distinct per peer")
        for entry in result["sub_games"]:
            for grp, commit in entry["github_commit"].items():
                if by_group.get(grp) != commit:
                    fails.append(
                        f"g{entry['sub_game_number']}: github_commit not bound to declaration"
                    )
        h = result["mutual_agreement"]["sha256"]
        sigs = result["mutual_agreement"].get("signatures", {})
        valid = {g for g, s in sigs.items() if signer.verify({"final_sha256": h}, s)}
        if len(valid) < 2:
            fails.append("mutual agreement lacks two valid signed confirmations")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        fails.append(f"{type(exc).__name__}: {exc}")
    return {"passed": not fails, "failures": fails, "game_id": gid}


def agree(result_self: dict, result_peer: dict) -> bool:
    return result_self["mutual_agreement"]["sha256"] == result_peer["mutual_agreement"]["sha256"]
