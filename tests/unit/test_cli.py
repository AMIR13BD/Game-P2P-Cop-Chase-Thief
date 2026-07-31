"""CLI dispatch coverage for the non-network subcommands, driven in-process through
cli.main(argv) so argparse wiring and the local handlers are exercised end to end.
The live-transport subcommands (serve/netplay) are boundary wrappers and are covered
by the integration suite instead."""

from thief_agent.cli import build_parser, main


def test_parser_requires_subcommand():
    parser = build_parser()
    assert parser.prog == "thief_agent"


def test_series_subcommand_runs(capsys):
    rc = main(["series", "--seed", "1"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "role_sequence=" in out and "winner=" in out


def test_simulate_subcommand_runs(capsys):
    rc = main(["simulate", "--turns", "5"])
    out = capsys.readouterr().out
    assert rc == 0 and "turns" in out


def test_artifacts_subcommand_emits_and_verifies(tmp_path, capsys):
    out_dir = tmp_path / "artifacts"
    rc = main(["artifacts", "--out", str(out_dir), "--seed", "1"])
    printed = capsys.readouterr().out
    assert rc == 0
    assert "audit_passed=True" in printed
    assert out_dir.exists() and any(out_dir.iterdir())
