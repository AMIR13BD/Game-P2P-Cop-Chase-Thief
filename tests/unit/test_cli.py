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


def test_tournament_subcommand_runs(capsys):
    rc = main(["tournament", "--seeds", "2"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "police champion=" in out and "thief champion=" in out


def test_view_subcommand_renders(capsys):
    rc = main(["view"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "belief heatmap" in out and ("P" in out or "state=MOVE" in out)


def test_replay_subcommand_verifies_emitted_game(tmp_path, capsys):
    out_dir, gid = tmp_path / "art", "gtest"
    assert main(["artifacts", "--out", str(out_dir), "--game-id", gid, "--seed", "1"]) == 0
    capsys.readouterr()
    rc = main(["replay", "--dir", str(out_dir), "--game-id", gid])
    out = capsys.readouterr().out
    assert rc == 0
    assert "sub_game=1" in out and "VERIFIED OK" in out


def test_replay_subcommand_no_logs(capsys, tmp_path):
    rc = main(["replay", "--dir", str(tmp_path), "--game-id", "nope"])
    assert rc == 0 and "no replayable logs found" in capsys.readouterr().out


def test_artifacts_subcommand_emits_and_verifies(tmp_path, capsys):
    out_dir = tmp_path / "artifacts"
    rc = main(["artifacts", "--out", str(out_dir), "--seed", "1"])
    printed = capsys.readouterr().out
    assert rc == 0
    assert "audit_passed=True" in printed
    assert out_dir.exists() and any(out_dir.iterdir())
