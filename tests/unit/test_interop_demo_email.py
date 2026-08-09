"""FRIENDLY CLI auto-email: with --demo-email-recipient a CLEAN run auto-sends the
generated result JSON to that address via the existing (mocked) Gmail send path; without
the flag nothing is sent; a non-clean run sends nothing. No real match or email runs."""

from thief_agent.interop import cli
from thief_agent.interop.friendly import FriendlyResult


class _Rec:
    def __init__(self):
        self.calls = 0
        self.args = None

    def __call__(self, args):
        self.calls += 1
        self.args = args
        return 0


def _setup(monkeypatch, clean=True):
    fake = FriendlyResult(clean=clean, game_id="amireman-vs-opp", summaries=[], result_doc={})
    monkeypatch.setattr(cli, "run_friendly", lambda **kw: fake)
    rec = _Rec()
    monkeypatch.setattr("thief_agent.infra.gmail_cli.run", rec)
    return rec


def test_friendly_auto_emails_result_with_flag(monkeypatch):
    rec = _setup(monkeypatch)
    rc = cli.main(
        [
            "friendly",
            "--peer",
            "http://x/mcp",
            "--out",
            "runs/x",
            "--demo-email-recipient",
            "aicoursenew@gmail.com",
        ]
    )
    assert rc == 0 and rec.calls == 1
    a = rec.args
    assert a.action == "send" and a.email_mode == "send" and a.demo_allow_uncounted is True
    assert a.recipient == "aicoursenew@gmail.com"  # our demo recipient, never the lecturer
    assert a.game_id == "amireman-vs-opp" and a.dir == "runs/x"


def test_friendly_without_flag_sends_nothing(monkeypatch):
    rec = _setup(monkeypatch)
    cli.main(["friendly", "--peer", "http://x/mcp"])
    assert rec.calls == 0


def test_friendly_no_email_when_not_clean(monkeypatch):
    rec = _setup(monkeypatch, clean=False)
    rc = cli.main(
        ["friendly", "--peer", "http://x/mcp", "--demo-email-recipient", "aicoursenew@gmail.com"]
    )
    assert rec.calls == 0 and rc == 6
