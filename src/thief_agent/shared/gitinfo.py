"""Resolve the current repository Git commit at the application boundary only.

Domain/series code never calls this; the resolved string is passed in explicitly."""

import subprocess


def current_commit(default: str = "uncommitted") -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        return out.stdout.strip() or default
    except Exception:  # noqa: BLE001 - boundary helper: any failure -> documented default
        return default
