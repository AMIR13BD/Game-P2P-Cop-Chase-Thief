# PRD — API Gatekeeper, rate limiting and overflow queueing

*Per-mechanism PRD required by the software guidelines §2.3 (and the mechanism the
guidelines mandate in §5). Documents
[`shared/gatekeeper.py`](../src/thief_agent/shared/gatekeeper.py) and
[`shared/rate_limiter.py`](../src/thief_agent/shared/rate_limiter.py).*

---

## 1. Description and theoretical background

Every peer in this league is simultaneously a server and a client, and its MCP endpoint is
publicly reachable through a tunnel during a match. Two distinct risks follow: an opponent
(or an accident) can overload our endpoint, and our own outgoing calls can exceed a
third-party service's quota. A **single central gatekeeper** guards both directions so that
no call path can bypass the policy.

Two independent mechanisms are combined:

**Token bucket (rate).** Tokens accrue continuously at `requests_per_minute / 60` per
second up to a capacity, and each admitted request consumes one. A token bucket is chosen
over a fixed window because a fixed window permits a *burst at the boundary* — up to twice
the nominal rate across two adjacent windows — whereas a bucket smooths to a stable
long-run rate while still allowing a bounded burst equal to its capacity. Per rulebook
rule #28, the per-minute limiter targets the **outgoing Gmail report path**.

**Bounded admission (concurrency + queue).** Admission capacity is
`concurrent_requests + queue_depth`. Work beyond that is refused with `QueueFullError`
rather than being accepted and dropped, or accepted until memory is exhausted. This is the
"queue, don't crash" requirement: bounded queueing converts an unbounded overload into a
predictable, explicit rejection — an application of Little's law, since an unbounded queue
under sustained overload grows without limit and latency diverges.

## 2. Requirements, expected input/output, performance metrics

| # | Requirement |
|---|---|
| R1 | Every guarded call passes through `Gatekeeper.admit()` / `.release()` |
| R2 | Limits come from **configuration**, never hardcoded at call sites |
| R3 | Exceeding the per-minute rate raises `RateLimitError` |
| R4 | Exceeding admission capacity raises `QueueFullError` — never an unbounded queue, never a crash |
| R5 | The long-run admitted rate converges to the configured rate |
| R6 | Time is injectable so the behaviour is deterministically testable |

**Configuration** — from the `rate_limiter_gatekeeper` block of the game config:

| Key | Value | Meaning |
|---|---:|---|
| `requests_per_minute` | 30 | Token-bucket refill rate |
| `concurrent_requests` | 2 | Simultaneous in-flight requests |
| `retry_backoff_sec` | 5 | Client-side backoff between retries |
| `max_retries` | 3 | Retry ceiling |
| `queue_depth` | 100 | Additional admission slots beyond concurrency |

**Input / Output** — `admit()` returns `None` on success and raises on refusal;
`release()` decrements the in-flight counter. The `now` callable is injectable
(defaults to `time.monotonic`), which is what makes rate behaviour testable without sleeping.

**Performance metrics** — admitted vs refused counts; observed long-run rate against the
configured rate; peak in-flight; time spent in `admit()` (must be negligible).

## 3. Constraints, limitations, alternatives considered

**Constraints.** `time.monotonic` is used rather than wall-clock so that NTP adjustments
cannot corrupt the refill computation. All five parameters are part of the shared config contract
and are validated at load.

**Deliberate guidelines exception — `rate_limits.version`.** Guidelines Table 2 asks for a
`version` key inside the rate-limit configuration as well as at the top level. It is
**not** implemented here, by decision rather than oversight. The config validator
(`shared/config_validate.py`) uses a single closed field list per category for both
*required* and *allowed* keys, so introducing the key would make it mandatory in **every**
config the agent loads — including a future opponent's Appendix-F contract file, which
will not contain it. That would turn a documentation requirement into an interoperability
failure. The code-version and top-level config-version requirements of Table 2 are
satisfied (`shared/version.py`, `config/game.json`), together with the startup
compatibility validation the same section asks for.

**Limitations.**
- The gatekeeper is **per process**. Two peer processes on one host each get their own
  bucket; there is no distributed coordination, which is correct for this architecture but
  would not be for a horizontally scaled service.
- `release()` must be paired with `admit()` by the caller; a leaked `release` would inflate
  capacity. It is invoked through a narrow set of call sites rather than a context manager.

**Alternatives considered**

| Alternative | Why rejected |
|---|---|
| Fixed-window counter | Allows a 2× burst across the window boundary; the bucket gives a stable long-run rate |
| Leaky bucket (queue-shaped) | Smooths output but adds latency; we want fast refusal, not buffering |
| Unbounded queue | The failure mode the requirement explicitly forbids — memory growth then collapse |
| Per-call-site limits | Any missed call site silently bypasses the policy; a single central guard is auditable |
| Sleeping/blocking on limit | Blocks the async MCP handlers, which must never block (see README §2.1) |

## 4. Success criteria and test scenarios

**Success criteria**
- S1 A burst beyond `concurrent_requests + queue_depth` raises `QueueFullError` and the
  process stays healthy.
- S2 Sustained load converges to `requests_per_minute`.
- S3 Limits change purely by editing configuration, with no code change.
- S4 Tests are deterministic — no reliance on real elapsed time.

**Test scenarios**

| Scenario | Test |
|---|---|
| Token-bucket refill and long-run rate with injected clock | `tests/unit/test_rate_limiter.py` |
| Admission capacity and `QueueFullError` on overflow | `tests/unit/test_gatekeeper.py` |
| Config-driven limits (no hardcoded values) | `tests/unit/test_config_validate.py` |
| Server path integration | `tests/unit/test_interop_transport.py` |

**Operational note.** During the counted matches the endpoint was exposed through an
ephemeral Cloudflare tunnel; the gatekeeper is the reason an unexpected burst from a peer
degrades into explicit refusals rather than taking the match process down.
