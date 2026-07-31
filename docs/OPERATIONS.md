# Operations Manual — launch, replay, GUI, Gmail, tunnels, recovery

All commands run from a repo with `uv sync` already done. Replace `thief_agent` with
`thief_agent` in the thief repo.

## Launch commands (both roles)
Local (single machine):
```bash
# Responder (one terminal), e.g. the thief peer:
uv run python -m thief_agent serve --port 8002 --token <shared-token> --group amireman-thief
# Driver (another terminal), the police peer:
uv run python -m thief_agent netplay --opponent-url http://127.0.0.1:8002/mcp \
    --token <shared-token> --out artifacts_net --game-id <gid> --opponent amireman-thief --counted
```
Two different computers (public counted match):
```bash
# On each machine, bind publicly and expose via a tunnel provider (see below):
uv run python -m thief_agent serve --port 8001 --token <token>   # host 127.0.0.1; tunnel maps public->local
# The driver connects to the opponent's PUBLIC https URL:
uv run python -m thief_agent netplay --opponent-url https://<opponent-public-host>/mcp \
    --token <token> --game-id <gid> --opponent <opp-group> --counted
```
Public counted matches must use `https://` (TLS enforced). Per-peer signing key is read
from `PT_SIGNER_KEY` (hex) in the environment (never committed/logged).

## Replay viewer (P20)
```bash
uv run python -m thief_agent replay --dir <artifacts-dir> --game-id <gid>
```
Prints, per sub-game, `frames=N VERIFIED OK` (or `TAMPERED at steps ...`) and renders the
post-audit truth board. Malformed/missing logs are handled safely.

## GUI (P21, headless text)
```bash
uv run python -m thief_agent view          # local-truth board + belief heatmap
```
The live view shows only the local player's truth and never the opponent's position.

## Gmail reporting (P23)
```bash
uv run python -m thief_agent gmail --action validate --dir <dir> --game-id <gid>   # gating check
uv run python -m thief_agent gmail --action dryrun   --dir <dir> --game-id <gid>   # builds attachment, sends nothing
uv run python -m thief_agent gmail --action bootstrap                               # OAuth (needs credentials.json)
uv run python -m thief_agent gmail --action send     --dir <dir> --game-id <gid>   # real send (needs token.json)
```
Send only fires after six sub-games + a confirmed final audit, is idempotent (a marker
prevents duplicate sends), and uses scope `gmail.send` only. Default recipient
`rmisegal+uoh26finalgame@gmail.com`, mode `draft` (never sends). See
`docs/GMAIL-OAUTH.md` for the one-time external setup (BLOCKED-EXTERNAL).

## Tunnel setup (provider-neutral)
`infra/tunnel.py` abstracts the provider. Localhost needs no tunnel. For a public match,
start any provider (e.g. ngrok / Localtonet) pointing at your local `serve` port and
export the public URL:
```bash
export PT_TUNNEL_URL="https://<your-public-host>/mcp"   # ignored env; never committed
```
Obtaining a real public URL / provider account is **BLOCKED-EXTERNAL**. Endpoint format
and TLS are validated; health is checked via `ConfiguredTunnel.healthy()`.

## Local counted-match rehearsal (P26)
```bash
uv run python scripts/counted_rehearsal.py     # run from the police repo, with ../thief present
```
Runs two real processes with distinct keys, validates the counted evidence, replays it,
proves a tampered copy is rejected, and produces a Gmail dry-run that sends nothing.

## Failure & recovery behaviour
- Unreachable/incompatible opponent, exhausted retries, protocol error, stalled peer,
  failed audit, config disagreement -> **technical loss (0/0)**, never an illegal move.
- Transient drops are retried with backoff (`infra/reliability`); a mid-series
  disconnect that cannot recover yields technical for the remaining sub-games.
- Deadline pressure -> anytime search returns the best legal move; the firewall + safe
  fallback guarantee legality.
