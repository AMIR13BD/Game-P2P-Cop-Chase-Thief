"""Counted netplay auto-emails the official result to the lecturer ONLY after a clean
series + verified artifacts + passing match audit, via the existing Gmail send path
(counted should_send gate, lecturer default). Fully mocked: no match, no real email."""

from argparse import Namespace

from thief_agent import commands
from thief_agent.infra import gmail_auth as ga


class _FakeSDK:
    def __init__(self, v_pass=True, m_pass=True):
        self._v = {"passed": v_pass, "failures": []}
        self._m = {"passed": m_pass, "failures": []}

    async def networked_series(self, url, token, cfg, seed, terms):
        return {
            "sub_games": [{"sub_game": i + 1, "outcome": "capture"} for i in range(6)],
            "role_sequence": [],
            "peer_commit": "c" * 40,
            "peer_ident": {},
        }

    def emit_and_verify(self, *a, **k):
        return self._v

    def verify_match(self, *a, **k):
        return self._m


class _Rec:
    def __init__(self, rc=0):
        self.rc = rc
        self.calls = 0
        self.args = None

    def __call__(self, args):
        self.calls += 1
        self.args = args
        return self.rc


def _args(counted=True):
    return Namespace(
        opponent_url="http://x/mcp",
        token="t",
        out="artifacts_net",
        game_id="G001",
        opponent="uoh-ay26",
        seed=1234,
        counted=counted,
    )


def _wire(monkeypatch, sdk, rec):
    monkeypatch.setattr(commands, "_sdk", lambda: sdk)
    monkeypatch.setattr("thief_agent.infra.gmail_cli.run", rec)


def test_counted_success_auto_emails_lecturer(monkeypatch):
    rec = _Rec(rc=0)
    _wire(monkeypatch, _FakeSDK(), rec)
    rc = commands.cmd_netplay(_args(counted=True))
    assert rc == 0 and rec.calls == 1
    a = rec.args
    assert a.action == "send" and a.email_mode == "send"
    assert a.recipient is None  # -> lecturer default
    assert a.dir == "artifacts_net" and a.game_id == "G001"
    assert getattr(a, "demo_allow_uncounted", False) is False  # counted gate, no demo override
    # the default recipient really is the lecturer
    monkeypatch.delenv("PT_GMAIL_RECIPIENT", raising=False)
    assert ga.email_settings(None)["recipient"] == "rmisegal+uoh26finalgame@gmail.com"


def test_email_failure_keeps_artifacts_and_reports(monkeypatch, capsys):
    _wire(monkeypatch, _FakeSDK(), _Rec(rc=2))
    rc = commands.cmd_netplay(_args(counted=True))
    assert rc == 3 and "EMAIL FAILED" in capsys.readouterr().out


def test_non_counted_never_emails(monkeypatch):
    rec = _Rec()
    _wire(monkeypatch, _FakeSDK(), rec)
    commands.cmd_netplay(_args(counted=False))
    assert rec.calls == 0


def test_counted_audit_failure_blocks_email(monkeypatch):
    rec = _Rec()
    _wire(monkeypatch, _FakeSDK(m_pass=False), rec)
    rc = commands.cmd_netplay(_args(counted=True))
    assert rec.calls == 0 and rc == 1
