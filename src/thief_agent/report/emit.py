"""Deterministically write the full four-artifact set for a completed local series.

Every artifact is structurally validated (schema of record) before it is written."""

import json
import os

from ..constants import Role, complement
from ..peer.audit import run_audit
from ..shared.sysinfo import system_spec
from . import artifacts, ids, schemas
from .report_writer import build_result


def _write(path: str, kind: str, obj: dict) -> None:
    schemas.validate(kind, obj)  # fail closed before emit (FR-ARTIFACT-01)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)


def _group_ident(group: str, repos: dict, signer) -> dict:
    base = {
        "group_id": group,
        "group_name": group,
        "members": [],
        "repos": repos.get(group, {"cop": "local", "thief": "local"}),
        "mcp_servers": {"cop": "", "thief": ""},
        "llm_model": "template",
        "hardware_spec": system_spec(),
    }
    return {**base, "signature": signer.sign(base)}


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
) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    groups = [self_group, opp_group]
    gc = {self_group: github_commit, opp_group: github_commit}
    ident = {
        "group_1": _group_ident(self_group, repos, signer),
        "group_2": _group_ident(opp_group, repos, signer),
    }
    paths = {"declaration": os.path.join(out_dir, ids.declaration_name(gid))}
    _write(paths["declaration"], "declaration", artifacts.build_declaration(gid, ident))
    rows = []
    for sg in series["sub_games"]:
        nn = sg["sub_game"]
        self_role = sg["self_role"]
        roles = {self_group: self_role, opp_group: complement(Role(self_role)).value}
        scores = {self_group: sg["self_score"], opp_group: sg["opp_score"]}
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
        log_art = artifacts.build_log(gid, nn, summary, sg["records"])
        _write(os.path.join(out_dir, ids.config_name(gid, nn)), "config", cfg_art)
        _write(os.path.join(out_dir, ids.log_name(gid, nn)), "log", log_art)
        rows.append(
            {
                "sub_game_number": nn,
                "roles": roles,
                "outcome": sg["outcome"],
                "scores": scores,
                "log_file": ids.log_name(gid, nn),
                "config_sha256": cfg_art["config_sha256"],
                "log_sha256": artifacts.log_sha256(sg["records"]),
                "audit_passed": audit["passed"],
            }
        )
    result = build_result(gid, groups, rows, gc, repos)
    paths["result"] = os.path.join(out_dir, ids.result_name(gid))
    _write(paths["result"], "result", result)
    return {"paths": paths, "result": result}
