"""OFFICIAL counted mode on the friendly transport: --counted reuses the exact friendly
run/transport and, after a clean final audit, emails the ONE result JSON to the LECTURER
(never the demo address). Without --counted the lecturer is never emailed; demo mode is
unchanged. Fully mocked: no match, no real email."""

from thief_agent.interop import cli
from thief_agent.interop.friendly import FriendlyResult


class _BM:  # capture build_message(recipient, attachment name)
    def __init__(self):
        self.recipient = self.name = None

    def __call__(self, sender, recipient, subject, body, name, blob):
        self.recipient, self.name = recipient, name
        return {"raw": "x"}


class _SR:  # count send_report calls (the official sender)
    def __init__(self):
        self.calls = 0

    def __call__(self, service, message, marker):
        self.calls += 1
        return {"status": "sent", "message_id": "X"}


class _DemoRun:  # count gmail_cli.run calls (the demo sender)
    def __init__(self):
        self.calls = 0

    def __call__(self, args):
        self.calls += 1
        return 0


def _wire(monkeypatch, clean=True):
    monkeypatch.delenv("PT_GMAIL_RECIPIENT", raising=False)
    fake = FriendlyResult(clean=clean, game_id="amireman-vs-uoh-ay26", summaries=[], result_doc={})
    monkeypatch.setattr(cli, "run_friendly", lambda **kw: fake)
    bm, sr, demo = _BM(), _SR(), _DemoRun()
    monkeypatch.setattr(
        "thief_agent.infra.gmail_report.report_attachment",
        lambda d, g: (f"result_{g}.json", b'{"k":1}'),
    )
    monkeypatch.setattr("thief_agent.infra.gmail_report.build_message", bm)
    monkeypatch.setattr("thief_agent.infra.gmail_report.send_report", sr)
    monkeypatch.setattr("thief_agent.infra.gmail_auth.build_service", lambda: object())
    monkeypatch.setattr("thief_agent.infra.gmail_cli.run", demo)
    return bm, sr, demo


def test_counted_emails_lecturer_once(monkeypatch):
    bm, sr, demo = _wire(monkeypatch)
    rc = cli.main(["friendly", "--peer", "http://x/mcp", "--out", "runs/x", "--counted"])
    assert rc == 0 and sr.calls == 1 and demo.calls == 0  # one official email, no demo send
    assert bm.recipient == "rmisegal+uoh26finalgame@gmail.com"  # lecturer, never aicoursenew
    assert bm.name == "result_amireman-vs-uoh-ay26.json"  # the ONE generated result JSON


def test_friendly_no_flag_never_emails_lecturer(monkeypatch):
    bm, sr, demo = _wire(monkeypatch)
    cli.main(["friendly", "--peer", "http://x/mcp"])
    assert sr.calls == 0 and demo.calls == 0


def test_counted_not_clean_sends_nothing(monkeypatch):
    bm, sr, demo = _wire(monkeypatch, clean=False)
    rc = cli.main(["friendly", "--peer", "http://x/mcp", "--counted"])
    assert sr.calls == 0 and rc == 6


def test_demo_mode_unchanged_targets_demo_not_lecturer(monkeypatch):
    bm, sr, demo = _wire(monkeypatch)
    cli.main(
        ["friendly", "--peer", "http://x/mcp", "--demo-email-recipient", "aicoursenew@gmail.com"]
    )
    assert demo.calls == 1 and sr.calls == 0  # demo path used; official lecturer sender not used
