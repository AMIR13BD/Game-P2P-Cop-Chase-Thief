"""P23 Gmail reporting: gating (six sub-games + counted audit), MIME attachment,
idempotent mocked send, dry-run/draft sends nothing, clear failures, no real creds."""

import base64
import json

import pytest

from thief_agent.infra import gmail_auth as ga
from thief_agent.infra import gmail_report as gr


def _result(n=6, technical=False, tampered=False):
    """A real counted two-peer result (the only kind that may ever be sent)."""
    subs = [
        {
            "sub_game_number": i + 1,
            "result": "technical" if technical else "capture",
            "audit": {"tampered": tampered},
        }
        for i in range(n)
    ]
    ma = {
        "confirmed": True,
        "sha256": "a" * 64,
        "mode": "counted-two-peer",
        "confirmations": {
            "p": {"group": "p", "final_sha256": "h"},
            "t": {"group": "t", "final_sha256": "h"},
        },
    }
    return {"sub_games": subs, "mutual_agreement": ma}


def test_gate_requires_six_clean_counted():
    assert gr.should_send(_result())[0] is True
    assert gr.should_send(_result(n=5))[0] is False
    assert gr.should_send(_result(technical=True))[0] is False
    assert gr.should_send(_result(tampered=True))[0] is False
    assert gr.should_send("nope")[0] is False


def test_self_play_or_dev_result_never_sent():
    # A local-dev (self-play) result has no counted-two-peer agreement -> never sent,
    # even though its 'confirmed' flag is hardcoded True.
    r = _result()
    r["mutual_agreement"] = {"confirmed": True, "sha256": "a" * 64, "mode": "local-dev"}
    assert gr.should_send(r)[0] is False


def test_gate_counted_two_peer_requires_agreeing_confirmations():
    r = _result()
    assert gr.should_send(r)[0] is True
    r["mutual_agreement"]["confirmations"]["t"]["final_sha256"] = "other"
    assert gr.should_send(r)[0] is False  # hashes disagree -> no send


def test_build_message_has_json_attachment():
    msg = gr.build_message("me", "to@x.com", "subj", "body", "report.json", b'{"k":1}')
    raw = base64.urlsafe_b64decode(msg["raw"]).decode()
    assert "to@x.com" in raw and "subj" in raw
    assert 'filename="report.json"' in raw  # JSON report attached (base64 in MIME)
    assert base64.b64encode(b'{"k":1}').decode() in raw


class _FakeSend:
    def __init__(self, mid="MSGID123"):
        self.mid, self.calls = mid, 0

    def users(self):
        return self

    def messages(self):
        return self

    def send(self, userId, body):  # noqa: N803 - Gmail API kwarg name
        self.calls += 1
        return self

    def execute(self):
        return {"id": self.mid}


def test_idempotent_send_only_once(tmp_path):
    svc = _FakeSend()
    marker = str(tmp_path / "sent.json")
    first = gr.send_report(svc, {"raw": "x"}, marker)
    assert first == {"status": "sent", "message_id": "MSGID123"} and svc.calls == 1
    second = gr.send_report(svc, {"raw": "x"}, marker)
    assert second["status"] == "skipped-already-sent" and svc.calls == 1  # no duplicate send


def test_dryrun_writes_attachment_and_sends_nothing(tmp_path, capsys):
    # emit a real result artifact, then dry-run.
    from types import SimpleNamespace

    from thief_agent.infra.gmail_cli import run
    from thief_agent.report import ids

    (tmp_path / ids.result_name("g")).write_text(json.dumps(_result()), encoding="utf-8")
    args = SimpleNamespace(
        action="dryrun", dir=str(tmp_path), game_id="g", recipient="x@y.com", email_mode="draft"
    )
    rc = run(args)
    out = capsys.readouterr().out
    assert rc == 0 and "sent nothing" in out
    dry = json.loads((tmp_path / "gmail_dryrun_g.json").read_text())
    assert dry["sent"] is False and dry["recipient"] == "x@y.com"
    assert not (tmp_path / "gmail_sent_g.json").exists()  # nothing sent


def test_validate_fails_closed_on_incomplete(tmp_path):
    from types import SimpleNamespace

    from thief_agent.infra.gmail_cli import run
    from thief_agent.report import ids

    (tmp_path / ids.result_name("g")).write_text(json.dumps(_result(n=3)), encoding="utf-8")
    args = SimpleNamespace(
        action="validate", dir=str(tmp_path), game_id="g", recipient=None, email_mode=None
    )
    assert run(args) == 1


def test_build_service_blocked_external_without_token(tmp_path, monkeypatch):
    monkeypatch.setenv("PT_GMAIL_TOKEN", str(tmp_path / "absent.json"))
    with pytest.raises(RuntimeError, match="BLOCKED-EXTERNAL"):
        ga.build_service()


def test_bootstrap_blocked_external_without_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("PT_GMAIL_CREDENTIALS", str(tmp_path / "absent.json"))
    with pytest.raises(RuntimeError, match="BLOCKED-EXTERNAL"):
        ga.bootstrap()


def test_gmail_cli_validate_via_main(tmp_path, capsys):
    from thief_agent.cli import main
    from thief_agent.report import ids

    (tmp_path / ids.result_name("g")).write_text(json.dumps(_result()), encoding="utf-8")
    rc = main(["gmail", "--action", "validate", "--dir", str(tmp_path), "--game-id", "g"])
    assert rc == 0 and "would_send=True" in capsys.readouterr().out


def test_email_settings_defaults_to_pdf_recipient(monkeypatch):
    monkeypatch.delenv("PT_GMAIL_RECIPIENT", raising=False)
    monkeypatch.delenv("PT_GMAIL_MODE", raising=False)
    st = ga.email_settings()
    assert st["recipient"] == "rmisegal+uoh26finalgame@gmail.com" and st["mode"] == "draft"
