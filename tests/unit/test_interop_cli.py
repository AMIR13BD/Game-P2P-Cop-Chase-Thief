"""The interop CLI: argument parsing and the friendly command's console output. The
network is stubbed so this stays a fast unit test; the real dial/serve path is covered by
tests/integration/test_interop_network.py."""

from thief_agent.interop import cli
from thief_agent.interop.friendly import FriendlyResult


def test_build_parser_friendly_defaults():
    args = cli.build_parser().parse_args(["friendly", "--peer", "http://x/mcp"])
    assert args.command == "friendly" and args.role == "police"
    assert args.games == 6 and args.port == 8901 and args.peer == "http://x/mcp"


def test_friendly_command_prints_mode_and_no_email(monkeypatch, capsys):
    fake = FriendlyResult(
        game_id="amireman-vs-x",
        game_uid="u",
        summaries=[
            {
                "sub_game_number": 1,
                "role": "police",
                "result": "capture",
                "steps": 12,
                "audit": {"log_verified": True},
            },
            {
                "sub_game_number": 2,
                "role": "thief",
                "result": "survival",
                "steps": 35,
                "audit": {"skipped": True},
            },
        ],
        artifacts=["a", "b"],
        result_doc={"final_result": {"total_score": {"amireman": 20}, "winner_group": "amireman"}},
        clean=True,
    )
    monkeypatch.setattr(cli, "run_friendly", lambda **kwargs: fake)
    rc = cli.main(["friendly", "--peer", "http://x/mcp", "--out", "/tmp/interop-cli-test"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "match_mode=friendly" in out
    assert "lecturer_report_sent=False" in out
    assert "game_uid u" in out


def test_friendly_command_returns_6_when_not_clean(monkeypatch):
    fake = FriendlyResult(clean=False, summaries=[], result_doc={})
    monkeypatch.setattr(cli, "run_friendly", lambda **kwargs: fake)
    assert cli.main(["friendly", "--peer", "http://x/mcp"]) == 6
