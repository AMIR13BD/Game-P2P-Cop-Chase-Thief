#!/usr/bin/env python3
"""Fail if any tracked Python file exceeds 150 physical lines. No bypass."""

import pathlib
import sys

LIMIT = 150
ROOTS = ("src", "tests", "scripts")


def offenders(base: pathlib.Path) -> list[tuple[str, int]]:
    bad: list[tuple[str, int]] = []
    for root in ROOTS:
        for path in (base / root).rglob("*.py"):
            n = sum(1 for _ in path.open("r", encoding="utf-8"))
            if n > LIMIT:
                bad.append((str(path.relative_to(base)), n))
    return bad


def main() -> int:
    base = pathlib.Path(__file__).resolve().parent.parent
    bad = offenders(base)
    for name, n in bad:
        print(f"LINE-LIMIT FAIL: {name} has {n} physical lines (max {LIMIT})")
    if bad:
        return 1
    print(f"line-count OK: all tracked .py <= {LIMIT} physical lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
