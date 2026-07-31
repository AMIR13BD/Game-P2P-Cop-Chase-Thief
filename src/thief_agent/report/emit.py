"""Deterministically write the full four-artifact set for a completed series.

Each artifact is structurally validated before writing. Declaration groups carry
per-peer signed identities (distinct Git commits); the result binds per-sub-game
commits to the declaration and carries per-group signed final-hash confirmations."""

import json
import os

from ..constants import Role, complement
from ..peer.audit import run_audit
from . import artifacts, ids, schemas
from .report_writer import build_result


def _write(path: str, kind: str, obj: dict) -> None:
    schemas.validate(kind, obj)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)


def emit_series(
    out_dir: str,
    gid: str,
    cfg: dict,
    self_group: str,
    opp_group: str,
    series: dict,
    github_commit: str,
    repos: dict,
    signer,
    peer_commit: str | None = None,
    peer_ident: dict | None = None,
) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    groups = [self_group, opp_group]
    sc = github_commit
    pc = peer_commit or github_commit
    gc = {self_group: sc, opp_group: pc}
    ident = {
        "group_1": artifacts.group_ident(self_group, repos, signer, sc),
        "group_2": peer_ident or artifacts.group_ident(opp_group, repos, signer, pc),
    }
    paths = {"declaration": os.path.join(out_dir, ids.declaration_name(gid))}
    _write(paths["declaration"], "declaration", artifacts.build_declaration(gid, ident))
    rows = []
    for sg in series["sub_games"]:
        nn = sg["sub_game"]
        self_role = sg["self_role"]
        roles = {self_group: self_role, opp_group: complement(Role(self_role)).value}
        audit = run_audit(sg["records"], signer)
        cfg_art = artifacts.build_config(gid, nn, cfg)
        summary = {
            "sub_game_number": nn,
            "group_id": self_group,
            "role": self_role,
            "opponent_group_id": opp_group,
            "result": sg["outcome"],
            "steps": sg["steps"],
            "tokens_total": 0,
            "audit": audit,
        }
        _write(os.path.join(out_dir, ids.config_name(gid, nn)), "config", cfg_art)
        _write(
            os.path.join(out_dir, ids.log_name(gid, nn)),
            "log",
            artifacts.build_log(gid, nn, summary, sg["records"]),
        )
        rows.append(
            {
                "sub_game_number": nn,
                "roles": roles,
                "outcome": sg["outcome"],
                "scores": {self_group: sg["self_score"], opp_group: sg["opp_score"]},
                "log_file": ids.log_name(gid, nn),
                "config_sha256": cfg_art["config_sha256"],
                "log_sha256": artifacts.log_sha256(sg["records"]),
                "audit_passed": audit["passed"],
            }
        )
    result = build_result(gid, groups, rows, gc, repos)
    h = result["mutual_agreement"]["sha256"]
    confs = series.get("confirmations")
    if confs:  # P22: two real per-peer confirmations exchanged over the protocol
        result["mutual_agreement"]["mode"] = "counted-two-peer"
        result["mutual_agreement"]["confirmations"] = confs
        result["mutual_agreement"]["signatures"] = {
            g: c.get("signature", "") for g, c in confs.items()
        }
    else:  # local single-process artifact (dev/self-play): not a counted agreement
        result["mutual_agreement"]["mode"] = "local-dev"
        result["mutual_agreement"]["signatures"] = {
            self_group: signer.sign({"final_sha256": h}),
            opp_group: signer.sign({"final_sha256": h}),
        }
    paths["result"] = os.path.join(out_dir, ids.result_name(gid))
    _write(paths["result"], "result", result)
    return {"paths": paths, "result": result}
