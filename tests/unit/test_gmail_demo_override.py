"""The DEMO-ONLY --demo-allow-uncounted override: a friendly/uncounted result may be
emailed to OURSELVES (never the lecturer), while the default and counted/official paths
stay byte-for-byte unchanged. No real Gmail service is ever built or called here."""

import json
from types import SimpleNamespace

import pytest

from thief_agent.infra import gmail_auth as ga
from thief_agent.infra import gmail_cli
from thief_agent.infra import gmail_report as gr
from thief_agent.report import ids

DEMO_TO = "aicoursenew@gmail.com"


def _friendly_result():
    """Six clean sub-games but NO counted-two-peer agreement (a friendly result)."""
    subs = [
        {
            "sub_game_number": i + 1,
            "result": "capture",
            "audit": {"log_verified": True, "tampered": False},
        }
        for i in range(6)
    ]
    return {"sub_games": subs, "report_type": "final_game_result"}


def _counted_result():
    subs = [
        {"sub_game_number": i + 1, "result": "capture", "audit": {"tampered": False}}
        for i in range(6)
    ]
    ma = {
        "mode": "counted-two-peer",
        "confirmations": {
            "p": {"group": "p", "final_sha256": "h"},
            "t": {"group": "t", "final_sha256": "h"},
        },
    }
    return {"sub_games": subs, "mutual_agreement": ma}


class _SendRecorder:
    def __init__(self):
        self.calls = 0

    def __call__(self, service, msg, marker):
        self.calls += 1
        return {"status": "sent", "message_id": "TEST"}


@pytest.fixture(autouse=True)
def no_real_send(monkeypatch):
    """Hard guarantee: no test can build a real service or send a real message."""
    rec = _SendRecorder()
    monkeypatch.setattr(gr, "send_report", rec)
    monkeypatch.setattr(ga, "build_service", lambda: object())
    return rec


def _args(tmp_path, **kw):
    base = {
        "action": "send",
        "dir": str(tmp_path),
        "game_id": "g",
        "recipient": None,
        "email_mode": "send",
        "demo_allow_uncounted": False,
    }
    base.update(kw)
    return SimpleNamespace(**base)


def _write(tmp_path, result):
    (tmp_path / ids.result_name("g")).write_text(json.dumps(result), encoding="utf-8")


# 1) friendly WITHOUT the flag = blocked (default behaviour unchanged) --------------------
def test_friendly_blocked_without_flag(tmp_path, capsys, no_real_send):
    assert gr.should_send(_friendly_result())[0] is False  # default gate unchanged
    _write(tmp_path, _friendly_result())
    rc = gmail_cli.run(_args(tmp_path, recipient=DEMO_TO, demo_allow_uncounted=False))
    assert rc == 1 and "NOT SENDING (fail-closed)" in capsys.readouterr().out
    assert no_real_send.calls == 0  # never reached the sender


# 2) friendly WITH the flag + our demo recipient = allowed --------------------------------
def test_friendly_allowed_with_flag_to_demo_recipient(tmp_path, capsys, no_real_send):
    assert gr.should_send(_friendly_result(), allow_uncounted=True)[0] is True
    _write(tmp_path, _friendly_result())
    rc = gmail_cli.run(_args(tmp_path, recipient=DEMO_TO, demo_allow_uncounted=True))
    out = capsys.readouterr().out
    assert rc == 0 and no_real_send.calls == 1  # sent via the (mocked) sender exactly once
    assert DEMO_TO in out and "lecturer NOT used" in out


# 3) counted/official + default gate unchanged -------------------------------------------
def test_counted_and_default_gate_unchanged():
    assert gr.should_send(_counted_result())[0] is True  # counted still sends by default
    assert gr.should_send(_friendly_result())[0] is False  # friendly still blocked by default
    assert gr.should_send(_counted_result(), allow_uncounted=True)[0] is True  # flag harmless


# 4) the flag NEVER lets us email the lecturer, and requires an explicit recipient --------
def test_demo_flag_requires_explicit_recipient(tmp_path, capsys, no_real_send):
    _write(tmp_path, _friendly_result())
    rc = gmail_cli.run(_args(tmp_path, recipient=None, demo_allow_uncounted=True))
    assert rc == 1 and "requires an explicit --recipient" in capsys.readouterr().out
    assert no_real_send.calls == 0


def test_demo_flag_refuses_lecturer_address(tmp_path, capsys, no_real_send):
    _write(tmp_path, _friendly_result())
    rc = gmail_cli.run(_args(tmp_path, recipient=ga.DEFAULT_RECIPIENT, demo_allow_uncounted=True))
    assert rc == 1 and "must not target the lecturer" in capsys.readouterr().out
    assert no_real_send.calls == 0
