from thief_agent.domain.crypto import seal
from thief_agent.domain.protocol import build_payload
from thief_agent.peer.audit import run_audit
from thief_agent.peer.sealing import make_step0_record
from thief_agent.security.signer import DevTestSigner


def test_step0_carries_real_commit_and_verifies(commit):
    sig = DevTestSigner()
    rec = make_step0_record("g", 1, sig, commit)
    assert rec["payload"]["github_commit"] == commit
    assert run_audit([rec], sig)["passed"]


def test_audit_rejects_bad_git_field():
    sig = DevTestSigner()
    rec = make_step0_record("g", 1, sig, "unknown")  # not a hex commit
    r = run_audit([rec], sig)
    assert not r["passed"] and r["failed_steps"] == [0]


def test_audit_rejects_bad_step0_signature(commit):
    sig = DevTestSigner()
    rec = make_step0_record("g", 1, sig, commit)
    rec["signature"] = "devtest:deadbeef"
    assert not run_audit([rec], sig)["passed"]


def test_audit_malformed_records_fail_closed():
    r = run_audit([{"bad": 1}, "not-a-dict", {"payload": {"step": 2}}], DevTestSigner())
    assert not r["passed"] and len(r["failed_steps"]) == 3


def test_audit_detects_commit_tamper():
    p = build_payload(1, "police", "state", "MOVE:N", "truth", "hi")
    s = seal(p)
    rec = {"payload": p, "nonce": s["nonce"], "commit": s["commit"]}
    assert run_audit([rec])["passed"]
    rec["commit"] = "0" * 64
    bad = run_audit([rec])
    assert not bad["passed"] and bad["failed_steps"] == [1]
