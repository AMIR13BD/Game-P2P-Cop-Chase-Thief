"""Positive + negative tests for the CI quality-gate scripts (line-count, secret-scan)."""

import importlib.util
import pathlib


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


def test_secret_scan_positive_and_negative(tmp_path):
    m = _load("secret_scan")
    (tmp_path / "clean.txt").write_text("nothing to see here")
    assert m.scan(tmp_path) == []
    (tmp_path / "leak.txt").write_text(
        "AKIA" + "A" * 16
    )  # built at runtime; no literal key in source
    assert m.scan(tmp_path)
