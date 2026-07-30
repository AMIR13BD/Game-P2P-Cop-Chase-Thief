# Thief Agent — team `amireman`

Thief peer for the distributed P2P Police–Thief league. Independent, self-contained
repository (natural role **THIEF**; full dual-role agent for six-sub-game alternation).

> Day-1 status: local-playable core (`G-MINPLAYABLE`). No networking, GUI, Gmail, tunnels
> or championship strategies yet — those are later batches (see `docs/PLAN.md`).

## Run
```
uv sync
uv run python -m thief_agent series           # local six-sub-game series
uv run python -m thief_agent simulate --turns 10000
uv run pytest                                  # test suite
uv run ruff check . && uv run ruff format --check .
uv run python scripts/check_line_count.py      # max 150 physical lines/file
uv run python scripts/secret_scan.py
```

## Layout
- `src/thief_agent/domain` — board, movement, capture, scoring, scent, crypto, protocol, negotiation
- `src/thief_agent/shared` — config load/validate/hash, sysinfo, version, defaults
- `src/thief_agent/security` — pluggable signer (dev/test; official = BLOCKED-EXTERNAL)
- `src/thief_agent/peer` — state machine, Step-0 sealing, audit, local turn engine
- `src/thief_agent/sdk` — six-sub-game series + role alternation
- `src/thief_agent/strategy` — BrainBase, firewall, RNG, belief, fallback, baseline brains
- `src/thief_agent/sim` — deterministic headless simulator + batch runner
- `docs/` — PRD, PLAN, TODO, REUSE-REGISTER

Sibling repository (Police): see `docs/PLAN.md` (cross-link added at submission).

## Movement & integrity (Day-1 invariants)
Legal moves are exactly **N, S, E, W, STAY**; diagonals are always rejected and malformed
move config fails closed. Every turn is sealed with `SHA256(canonical_json(payload)|nonce)`
and re-verified by a local mutual audit; any payload/nonce/commit change is detected.

Secrets are never committed. Reused reference infrastructure is documented in
`docs/REUSE-REGISTER.md`.
