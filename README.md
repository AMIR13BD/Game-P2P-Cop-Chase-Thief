# Thief Agent — team `amireman`

Thief peer for the distributed P2P Police–Thief league. Independent, self-contained
repository (natural role **THIEF**; full dual-role agent for six-sub-game alternation).

> Day-1/2 status: local-playable core plus networked series over real FastMCP transport.
> No GUI, Gmail, or tunnels yet — those are later batches (see `docs/PLAN.md`).

## Requirements
- Python **3.13+**
- [`uv`](https://docs.astral.sh/uv/) (dependency and virtual-env manager)
- `git` (used only at the application boundary to stamp the current commit)

## Installation
```bash
uv sync                              # create .venv and install locked dependencies
cp .env-example .env                 # optional: fill in local tokens (never committed)
cp config/game.json.example config/game.json    # signed shared contract (optional)
cp config/game.toml.example config/game.toml    # private overrides (optional)
```
No secrets are required to run the local commands below. Network play needs a bearer
token supplied via `--token` (or your local `.env`).

## Usage
All operations run through the CLI, which delegates to the `AgentSDK` facade:
```bash
uv run python -m thief_agent series --seed 1234         # local six-sub-game series
uv run python -m thief_agent simulate --turns 10000     # deterministic headless batch
uv run python -m thief_agent artifacts --out artifacts  # emit + verify the 4 artifacts
uv run python -m thief_agent serve --port 8002 --token dev-token           # run as peer
uv run python -m thief_agent netplay --opponent-url http://host:8002/mcp \
    --token dev-token --counted                          # drive a networked series
```

### Programmatic use (SDK)
`AgentSDK` is the single entry point; external consumers never import internal modules:
```python
from thief_agent.sdk.sdk import AgentSDK
from thief_agent.constants import Role
from thief_agent.security.signer import DevTestSigner
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

sdk = AgentSDK(Role.THIEF, "amireman-thief", DevTestSigner(), "uncommitted")
result = sdk.local_series(validate(DEFAULT_GAME_CONFIG), seed=1234)
```

## Configuration
Configuration is data, never hardcoded. Values live in separate files:
- `config/game.json.example` / `config/game.toml.example` — copy to the un-suffixed
  names for a signed shared contract and private overrides (signed keys always win).
- `.env-example` — placeholder environment template; copy to `.env` (git-ignored).
- `src/thief_agent/shared/defaults.py` — the canonical default game contract used when
  no file is supplied.

## Testing & quality gates
```bash
uv run pytest --cov                 # unit + integration suite, ≥85% coverage enforced
uv run ruff check . && uv run ruff format --check .
uv run python scripts/check_line_count.py      # max 150 physical lines/file
uv run python scripts/secret_scan.py           # fails if any secret is detected
```

## Layout
- `src/thief_agent/domain` — board, movement, capture, scoring, scent, crypto, protocol, negotiation
- `src/thief_agent/shared` — config load/validate/hash, sysinfo, version, defaults
- `src/thief_agent/security` — pluggable signer (dev/test; official = BLOCKED-EXTERNAL)
- `src/thief_agent/peer` — state machine, Step-0 sealing, audit, local + networked turn engines
- `src/thief_agent/infra` — real FastMCP server/client, reliability, idempotency
- `src/thief_agent/sdk` — `AgentSDK` facade + six-sub-game series with role alternation
- `src/thief_agent/strategy` — BrainBase, firewall, RNG, belief, fallback, baseline brains
- `src/thief_agent/sim` — deterministic headless simulator + batch runner
- `docs/` — PRD, PLAN, TODO, REUSE-REGISTER, COMPLIANCE-CHECKLIST

Sibling repository (Police): independent repo; cross-link added at submission.

## Movement & integrity (invariants)
Legal moves are exactly **N, S, E, W, STAY**; diagonals are always rejected and malformed
move config fails closed. Every turn is sealed with `SHA256(canonical_json(payload)|nonce)`
and re-verified by a mutual audit; any payload/nonce/commit change is detected.

## Contributing
- Work on a feature branch; never initialise git in the parent directory.
- Before every commit, run all quality gates above (tests, ruff, line-count, secret-scan).
- Keep every file ≤150 physical lines and free of hardcoded secrets.
- No cross-repository imports, symlinks, or shared runtime state with the Police repo.

## License
Academic course project (P2P Police–Thief league). All rights reserved by team
`amireman`; not licensed for redistribution. Reused reference infrastructure is
attributed in `docs/REUSE-REGISTER.md`.
