"""Replay viewer controls (P20): the VERIFIED OK / TAMPERED status line and the
stepper bounds (prev/next), so the viewer can never index outside the frame list."""


def status_line(status: dict) -> str:
    """Human-readable integrity banner for a replay."""
    if status.get("verified"):
        return "VERIFIED OK"
    failed = status.get("failed_steps") or []
    if not failed:
        return "TAMPERED (no verifiable steps)"
    return "TAMPERED at steps " + ", ".join(str(s) for s in failed)


def clamp_index(idx: int, n: int) -> int:
    if n <= 0:
        return 0
    return max(0, min(idx, n - 1))


def step_controls(idx: int, n: int) -> dict:
    """Stepper state: clamped index plus whether prev/next are available."""
    i = clamp_index(idx, n)
    return {"index": i, "has_prev": i > 0, "has_next": i < n - 1, "total": n}
