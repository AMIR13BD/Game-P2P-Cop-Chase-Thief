import pytest

from thief_agent.exceptions import ProtocolError, QueueFullError, RateLimitError
from thief_agent.peer.deadline import Deadline
from thief_agent.peer.watchdog import Watchdog
from thief_agent.shared.gatekeeper import Gatekeeper
from thief_agent.shared.rate_limiter import TokenBucket


def test_token_bucket_rate_and_refill():
    clk = [0.0]
    b = TokenBucket(2, now=lambda: clk[0])
    assert b.allow() and b.allow()
    assert not b.allow()
    clk[0] = 60.0
    assert b.allow()


def test_gatekeeper_rate_limit():
    gk = Gatekeeper(1, 5, 100, now=lambda: 0.0)
    gk.admit()
    gk.release()
    with pytest.raises(RateLimitError):
        gk.admit()


def test_gatekeeper_concurrency_queue_overflow():
    gk = Gatekeeper(100, 1, 0, now=lambda: 0.0)
    gk.admit()
    with pytest.raises(QueueFullError):
        gk.admit()


def test_deadline_check():
    Deadline(10.0, now=lambda: 0.0).check()
    with pytest.raises(ProtocolError):
        Deadline(0.0, now=lambda: 0.0).check()


def test_watchdog_stall_detection():
    clk = [0.0]
    w = Watchdog(5.0, now=lambda: clk[0])
    w.heartbeat()
    assert not w.stalled()
    clk[0] = 6.0
    assert w.stalled()


def test_gatekeeper_queue_depth_capacity():
    gk = Gatekeeper(100, 1, 2, now=lambda: 0.0)  # capacity = concurrent(1) + depth(2) = 3
    gk.admit()
    gk.admit()
    gk.admit()  # up to capacity
    with pytest.raises(QueueFullError):
        gk.admit()
    gk.release()
    gk.admit()  # frees one slot
