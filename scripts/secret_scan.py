#!/usr/bin/env python3
"""Scan the working tree for likely committed secrets. Non-zero exit on any hit."""

import pathlib
import re
import sys

PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*sk-[A-Za-z0-9]"),
    re.compile(r"\"private_key\"\s*:\s*\"-----BEGIN"),
]
SKIP_DIRS = {".git", ".venv", "__pycache__", ".ruff_cache", ".pytest_cache"}
SKIP_NAMES = {"secret_scan.py"}
SENSITIVE_FILES = {"credentials.json", "token.json", ".env"}


def scan(base: pathlib.Path) -> list[str]:
    hits: list[str] = []
    for path in base.rglob("*"):
        if not path.is_file() or set(path.parts) & SKIP_DIRS or path.name in SKIP_NAMES:
            continue
        if path.name in SENSITIVE_FILES:
            hits.append(f"SENSITIVE FILE PRESENT: {path.relative_to(base)}")
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in PATTERNS:
            if pat.search(text):
                hits.append(f"SECRET MATCH {pat.pattern[:24]!r} in {path.relative_to(base)}")
    return hits


def main() -> int:
    base = pathlib.Path(__file__).resolve().parent.parent
    hits = scan(base)
    for h in hits:
        print(h)
    if hits:
        return 1
    print("secret-scan OK: no secrets detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
