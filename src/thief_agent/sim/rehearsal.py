"""Local counted-match rehearsal validation (P26).

Given an emitted evidence directory and each peer's signer, assert the counted match
is authentic and complete: six sub-games, both roles per sub-game, distinct real Git
commits, a counted-two-peer agreement whose confirmations verify under the peers' own
keys, and which is NOT forgeable (verification under swapped keys must fail)."""

import json
import os

from ..report import ids
from ..report.confirm import verify_mutual


def _load(dirpath: str, name: str) -> dict:
    with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
        return json.load(fh)


def validate_counted_evidence(evidence_dir: str, gid: str, signer_by_group: dict) -> dict:
    """Return {passed, failures, ...} for an emitted counted-match evidence directory."""
    fails: list[str] = []
    result = _load(evidence_dir, ids.result_name(gid))
    subs = result["sub_games"]
    if len(subs) != 6:
        fails.append(f"expected 6 sub-games, got {len(subs)}")
    if any(set(s["roles"].values()) != {"police", "thief"} for s in subs):
        fails.append("a sub-game does not have both roles")
    decl = _load(evidence_dir, ids.declaration_name(gid))
    commits = [g.get("github_commit") for g in decl["groups"].values()]
    if any(not c for c in commits) or len(set(commits)) < 2:
        fails.append("Git commits are not distinct and real per peer")
    ma = result["mutual_agreement"]
    if ma.get("mode") != "counted-two-peer":
        fails.append("not a counted-two-peer mutual agreement")
    confs = list(ma.get("confirmations", {}).values())
    if len(confs) != 2:
        fails.append("missing two peer confirmations")
    else:
        a, b = confs
        sa, sb = signer_by_group.get(a["group"]), signer_by_group.get(b["group"])
        vm = verify_mutual(a, b, sa, sb)
        if not vm["passed"]:
            fails.append("confirmations do not verify: " + "; ".join(vm["failures"]))
        if sa and sb and verify_mutual(a, b, sb, sa)["passed"]:
            fails.append("confirmations verify under swapped keys (forgeable)")
    return {"passed": not fails, "failures": fails, "sub_games": len(subs)}
