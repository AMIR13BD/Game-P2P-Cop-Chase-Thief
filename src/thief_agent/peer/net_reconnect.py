"""Session isolation + transport-error classification for reconnect-safe series play.

Each network session attempt runs in its OWN child task (`run_isolated`) so that when a
session's streaming connection drops -- which cancels the FastMCP client's internal task
group -- the cancellation stays contained in the child and cannot poison the parent task's
cancel scope. That isolation is what lets the driver open a fresh, *usable* session and
continue the series after a mid-series drop (without it, the reconnect raises a bare
RuntimeError and the series is abandoned). Exceptions are classified so recoverable
transport failures -- bare or wrapped in an ExceptionGroup -- drive a reconnect, while a
genuine programmer error is reported so the caller re-raises it and never swallows a bug."""

import anyio

from .net_driver import TRANSPORT_ERRORS, transport_reason

# substrings that mark a RuntimeError as transport/session-level (not a logic bug)
_CONNECTISH = ("connect", "transport", "session", "closed", "stream", "pool", "peer")


async def run_isolated(make_coro):
    """Run make_coro() in a child task; return the exception it raised (or None) WITHOUT
    letting it cancel the parent, so the next attempt starts from a clean parent scope."""
    box: dict = {"exc": None}

    async def runner():
        try:
            await make_coro()
        except Exception as exc:  # captured for classification; re-raised by caller if fatal
            box["exc"] = exc

    async with anyio.create_task_group() as tg:
        tg.start_soon(runner)
    return box["exc"]


def _leaves(exc):
    if isinstance(exc, BaseExceptionGroup):
        out: list = []
        for e in exc.exceptions:
            out.extend(_leaves(e))
        return out
    return [exc]


def _leaf_ok(e) -> bool:
    if isinstance(e, TRANSPORT_ERRORS):
        return True
    return isinstance(e, RuntimeError) and any(w in str(e).lower() for w in _CONNECTISH)


def is_recoverable(exc) -> bool:
    """True iff EVERY leaf is a transport-class failure, so the series may reconnect. A mix
    that includes a real programmer error returns False -> the caller re-raises (fail loud)."""
    leaves = _leaves(exc)
    return bool(leaves) and all(_leaf_ok(e) for e in leaves)


def recoverable_reason(exc) -> str:
    for e in _leaves(exc):
        if _leaf_ok(e):
            return transport_reason(e)
    return transport_reason(exc)
