"""Counted netplay: after the audit passes on the FULL artifacts, write the ONE
reference-shaped result JSON and email THAT exact file once to the lecturer. The full audit
is untouched (runs first); the final result is structurally identical to result_G002.json.
Fully mocked: no match, no real email."""

import json
from argparse import Namespace

from netplay_email_fixtures import G1, G2, LINKS, MA, SUB, TOP, FakeSDK

from thief_agent import commands


class _BM:  # capture build_message(recipient, attachment name)
    def __init__(self):
        self.recipient = self.name = None

    def __call__(self, sender, recipient, subject, body, name, blob):
        self.recipient, self.name = recipient, name
        return {"raw": "x"}


class _SR:  # count send_report calls
    def __init__(self):
        self.calls = 0

    def __call__(self, service, message, marker):
        self.calls += 1
        return {"status": "sent", "message_id": "X"}


def _args(out, counted=True):
    return Namespace(
        opponent_url="http://x/mcp",
        token="",
        out=str(out),
        game_id="G001",
        opponent=G2,
        seed=1234,
        counted=counted,
    )


def _wire(monkeypatch, sdk):
    monkeypatch.delenv("PT_GMAIL_RECIPIENT", raising=False)
    monkeypatch.setattr(commands, "_sdk", lambda: sdk)
    monkeypatch.setattr("thief_agent.infra.gmail_auth.build_service", lambda: object())
    bm, sr = _BM(), _SR()
    monkeypatch.setattr("thief_agent.infra.gmail_report.build_message", bm)
    monkeypatch.setattr("thief_agent.infra.gmail_report.send_report", sr)
    return bm, sr


def test_counted_writes_g002_shaped_result_and_emails_once(monkeypatch, tmp_path):
    bm, sr = _wire(monkeypatch, FakeSDK())
    rc = commands.cmd_netplay(_args(tmp_path))
    assert rc == 0 and sr.calls == 1  # exactly ONE email
    doc = json.loads((tmp_path / "result_G001.json").read_text())  # the ONE final result
    assert set(doc) == TOP and set(doc["links"]) == LINKS and set(doc["mutual_agreement"]) == MA
    assert set(doc["sub_games"][0]) == SUB
    assert doc["sub_games"][0]["steps"] == 10  # real value from the series
    assert doc["sub_games"][0]["started_at"] == ""  # unavailable -> empty, never fabricated
    assert set(doc["links"]["github"]) == {G1, G2}  # per-group repo map, from real repos
    assert bm.name == "result_G001.json"  # emailed THAT exact file
    assert bm.recipient == "rmisegal+uoh26finalgame@gmail.com"  # lecturer default


def test_gate_failure_keeps_artifacts_no_send(monkeypatch, tmp_path):
    _bm, sr = _wire(monkeypatch, FakeSDK(mode="local-dev"))  # not counted-two-peer
    rc = commands.cmd_netplay(_args(tmp_path))
    assert rc == 3 and sr.calls == 0
    assert (tmp_path / "result_G001.json").exists()  # artifacts kept


def test_audit_failure_blocks_email(monkeypatch, tmp_path):
    _bm, sr = _wire(monkeypatch, FakeSDK(m_pass=False))
    assert commands.cmd_netplay(_args(tmp_path)) == 1 and sr.calls == 0


def test_non_counted_never_emails(monkeypatch, tmp_path):
    _bm, sr = _wire(monkeypatch, FakeSDK())
    commands.cmd_netplay(_args(tmp_path, counted=False))
    assert sr.calls == 0
