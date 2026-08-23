"""Positive + negative tests for the CI quality-gate scripts (line-count, secret-scan)."""

import importlib.util
import pathlib
import subprocess


def _load(name: str):
    path = pathlib.Path(__file__).resolve().parents[2] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_line_count_flags_oversize_only(tmp_path):
    m = _load("check_line_count")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "big.py").write_text("\n".join(["x = 1"] * 200))
    (tmp_path / "src" / "small.py").write_text("x = 1\n")
    names = [n for n, _ in m.offenders(tmp_path)]
    assert "src/big.py" in names
    assert "src/small.py" not in names


def _scan(tmp_path):
    """Run the scanner fresh: it accumulates ignored paths in a module global."""
    m = _load("secret_scan")
    return m.scan(tmp_path)


def test_secret_scan_positive_and_negative(tmp_path):
    """Outside a git tree the scanner falls back to walking every file present."""
    (tmp_path / "clean.txt").write_text("nothing to see here")
    fatal, _ = _scan(tmp_path)
    assert fatal == []
    (tmp_path / "leak.txt").write_text(
        "AKIA" + "A" * 16
    )  # built at runtime; no literal key in source
    fatal, _ = _scan(tmp_path)
    assert fatal


def test_secret_scan_flags_present_but_unignored_sensitive_file(tmp_path):
    """A credential sitting in the tree with no .gitignore rule is one `git add .` away."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "token.json").write_text("{}")
    fatal, _ = _scan(tmp_path)
    assert any("NOT GIT-IGNORED" in h for h in fatal)


def test_secret_scan_tolerates_correctly_ignored_credentials(tmp_path):
    """The same file, properly ignored, is informational -- git will never publish it."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "token.json").write_text("{}")
    (tmp_path / ".gitignore").write_text("token.json\n")
    fatal, info = _scan(tmp_path)
    assert fatal == []
    assert any("correctly git-ignored" in i for i in info)


def test_secret_scan_flags_tracked_credentials_despite_gitignore(tmp_path):
    """Force-added credentials are tracked, so git *would* publish them: still fatal."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "token.json").write_text("{}")
    (tmp_path / ".gitignore").write_text("token.json\n")
    subprocess.run(["git", "-C", str(tmp_path), "add", "-f", "token.json"], check=True)
    fatal, _ = _scan(tmp_path)
    assert any("TRACKED BY GIT" in h for h in fatal)
