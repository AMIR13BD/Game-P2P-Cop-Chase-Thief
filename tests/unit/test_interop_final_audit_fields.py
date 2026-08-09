"""Final-audit metadata the peer checks: our members are non-empty and our real roster,
and the audit's github_commit is the current 40-char HEAD SHA. The caught -> final-audit
transition is proven in ``test_interop_caught_transition``. No strategy/scoring/gameplay
code is touched — these pin the interop wiring only.
"""

import re

from thief_agent.interop import DEFAULT_GROUP_ID, DEFAULT_MEMBERS, cli
from thief_agent.interop.artifacts import build_declaration, build_result
from thief_agent.interop.engine import SubEngine
from thief_agent.interop.friendly import FriendlyResult
from thief_agent.interop.negotiate import Negotiator
from thief_agent.interop.series import identity_for
from thief_agent.interop.terms import default_terms

SHA40 = re.compile(r"^[0-9a-f]{40}$")


# ---- members ---------------------------------------------------------------------------


def test_default_identity_members_are_our_team():
    ident = identity_for(DEFAULT_GROUP_ID)
    assert ident["members"] == ["Amir Fadila", "Eman Sarhan"]
    assert ident["members"] == DEFAULT_MEMBERS
    assert ident["members"], "members must never be empty — the peer's final audit rejects []"


def test_outgoing_negotiate_payload_carries_members():
    ident = identity_for(DEFAULT_GROUP_ID)
    wire = Negotiator(default_terms(), ident, DEFAULT_GROUP_ID).signed("thief", 1).to_wire()
    assert wire["identity"]["members"] == ["Amir Fadila", "Eman Sarhan"]


def test_explicit_members_still_honoured():
    assert identity_for("x", members=["Solo"])["members"] == ["Solo"]


# ---- git commit in the negotiated identity (NOT in the signed terms) --------------------


def test_negotiate_identity_carries_full_sha_outside_terms():
    sha = "b" * 40
    ident = identity_for(DEFAULT_GROUP_ID, github_commit=sha)
    assert ident["git_commit_hash"] == sha and ident["github_commit"] == sha
    wire = Negotiator(default_terms(), ident, DEFAULT_GROUP_ID).signed("thief", 1).to_wire()
    assert wire["identity"]["git_commit_hash"] == sha
    assert wire["identity"]["github_commit"] == sha
    assert "github_commit" not in wire["terms"] and "git_commit_hash" not in wire["terms"]


def test_declaration_and_result_carry_github_commit():
    sha = "c" * 40
    own, peer = identity_for("amireman", github_commit=sha), identity_for("opp", github_commit=sha)
    decl = build_declaration("g", "u", own, peer, 1)
    assert decl["groups"]["group_1"]["github_commit"] == sha
    assert decl["groups"]["group_2"]["github_commit"] == sha
    summaries = [
        {
            "sub_game_number": 1,
            "result": "capture",
            "role": "police",
            "audit": {"log_verified": True, "tampered": False},
        }
    ]
    res = build_result("g", "u", "amireman", "opp", summaries, {"amireman": sha, "opp": sha})
    assert res["sub_games"][0]["github_commit"] == {"amireman": sha, "opp": sha}


# ---- git_commit_hash -------------------------------------------------------------------


def _capture_friendly(monkeypatch, argv):
    captured: dict = {}

    def fake_run_friendly(**kwargs):
        captured.update(kwargs)
        return FriendlyResult(clean=True, summaries=[], result_doc={})

    monkeypatch.setattr(cli, "run_friendly", fake_run_friendly)
    cli.main(argv)
    return captured


def test_cli_defaults_github_commit_to_real_head_sha(monkeypatch):
    captured = _capture_friendly(monkeypatch, ["friendly", "--peer", "http://x/mcp"])
    assert SHA40.match(captured["github_commit"]), captured["github_commit"]


def test_cli_explicit_commit_overrides(monkeypatch):
    override = "a" * 40
    captured = _capture_friendly(
        monkeypatch, ["friendly", "--peer", "http://x/mcp", "--commit", override]
    )
    assert captured["github_commit"] == override


def test_subengine_binds_the_given_commit_into_step0(commit):
    eng = SubEngine("thief", default_terms(max_steps=10), DEFAULT_GROUP_ID, commit, 1)
    step0 = eng.records[0]["payload"]
    assert step0["step"] == 0
    assert step0["github_commit"] == commit
    assert SHA40.match(commit)
