#!/usr/bin/env python3
"""Fail if a secret could reach the remote.

Appendix C and rules #39/#40 forbid *publishing* credentials, not holding them locally, so
the fatal check is scoped to what git would actually send: tracked files, plus any sensitive
file that is present and NOT ignored (one `git add .` away from being committed). A
credentials.json that exists locally and is correctly ignored is reported as INFO, not a
failure -- otherwise the gate is permanently red on any machine that can really send mail.
"""

import pathlib
import re
import subprocess
import sys

PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?:ANTHROPIC|OPENAI)_API_KEY\s*=\s*sk-[A-Za-z0-9]"),
    re.compile(r"\"private_key\"\s*:\s*\"-----BEGIN"),
    re.compile(r"sk-(?:proj-|ant-)[A-Za-z0-9_-]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30}"),
]
SKIP_NAMES = {"secret_scan.py"}
SENSITIVE_FILES = {"credentials.json", "token.json", ".env"}
SKIP_DIRS = {".git", ".venv", "__pycache__", ".ruff_cache", ".pytest_cache"}


def _git(base: pathlib.Path, *args: str) -> list[str]:
    out = subprocess.run(["git", *args], cwd=base, capture_output=True, text=True, check=False)
    return [ln for ln in out.stdout.splitlines() if ln.strip()] if out.returncode == 0 else []


def tracked(base: pathlib.Path) -> list[pathlib.Path] | None:
    """Files git would publish. None when this is not a git work tree."""
    if not (base / ".git").exists():
        return None
    return [base / p for p in _git(base, "ls-files")]


def unignored_sensitive(base: pathlib.Path) -> list[pathlib.Path]:
    """Sensitive files present in the tree that .gitignore does NOT exclude."""
    found = []
    for path in base.rglob("*"):
        if path.name not in SENSITIVE_FILES or set(path.parts) & SKIP_DIRS:
            continue
        rc = subprocess.run(
            ["git", "check-ignore", "-q", str(path)], cwd=base, capture_output=True, check=False
        )
        (found if rc.returncode != 0 else IGNORED).append(path)
    return found


IGNORED: list[pathlib.Path] = []


def scan(base: pathlib.Path) -> tuple[list[str], list[str]]:
    """Return (fatal hits, informational notes)."""
    fatal, info = [], []
    files = tracked(base)
    if files is None:  # not a git tree: fall back to scanning everything present
        files = [p for p in base.rglob("*") if p.is_file() and not set(p.parts) & SKIP_DIRS]
    for path in files:
        if not path.is_file() or path.name in SKIP_NAMES:
            continue
        rel = path.relative_to(base)
        if path.name in SENSITIVE_FILES:
            fatal.append(f"SENSITIVE FILE TRACKED BY GIT: {rel}")
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in PATTERNS:
            if pat.search(text):
                fatal.append(f"SECRET MATCH {pat.pattern[:28]!r} in {rel}")
    seen = {ln.rsplit(": ", 1)[-1] for ln in fatal}
    for path in unignored_sensitive(base):
        rel = str(path.relative_to(base))
        if rel not in seen:  # already reported as tracked; don't say "not ignored" too
            fatal.append(f"SENSITIVE FILE PRESENT AND NOT GIT-IGNORED: {rel}")
    for path in IGNORED:
        info.append(f"info: {path.relative_to(base)} present locally, correctly git-ignored")
    return fatal, info


def main() -> int:
    base = pathlib.Path(__file__).resolve().parent.parent
    fatal, info = scan(base)
    for line in info:
        print(line)
    for line in fatal:
        print(line)
    if fatal:
        return 1
    print("secret-scan OK: nothing publishable contains a secret")
    return 0


if __name__ == "__main__":
    sys.exit(main())
