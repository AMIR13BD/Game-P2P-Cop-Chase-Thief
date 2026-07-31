# Testing & Coverage

## How to run
```bash
uv sync
uv run pytest --cov                 # full unit + integration suite, coverage gate
uv run ruff check . && uv run ruff format --check .
uv run python scripts/check_line_count.py     # every tracked .py <= 150 physical lines
uv run python scripts/secret_scan.py
```

## Gate configuration
- `pyproject.toml` `[tool.coverage.report] fail_under = 85`, `branch = true` — the suite
  fails if branch coverage drops below 85%.
- Ruff: `select` includes `E,F,W,I,N,UP,B,SIM,C4`; `ruff format` enforced.
- Line-count checker enforces the ≤150 physical-lines rule on every tracked `.py`.

## Test layout
- `tests/unit/` — pure logic + fakes: domain rules, crypto, config, strategy portfolio,
  meta-controller, profiling, hints, graph algorithms (vs brute-force oracles),
  two-peer confirmation + fabrication, Gmail (mocked), tunnel, tuning, red-team,
  replay, GUI, rehearsal validation, CLI.
- `tests/integration/` — real FastMCP transport (serve+netplay), determinism, mutual
  audit fail-closed, fault injection (unreachable/technical, retry-recovery), simulation.

## Coverage of external/uncoverable code
Live server bootstrap (`infra/serve.run`) and the google-library calls in
`infra/gmail_auth` are marked `# pragma: no cover` (they require a blocking server or
external OAuth libraries). Their pure logic and the BLOCKED-EXTERNAL error paths ARE
tested.

## Current status (both repos)
- Branch coverage ≈ 89–90% (≥85% gate).
- All Python files ≤150 physical lines.
- Deterministic strategy tests, legality + timeout stress, red-team fail-closed, and a
  live two-process counted rehearsal all pass. See the run report for exact totals.
