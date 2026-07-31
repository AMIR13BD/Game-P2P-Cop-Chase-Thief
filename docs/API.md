# SDK / API reference

External consumers use the single entry point `AgentSDK`
(`thief_agent.sdk.sdk.AgentSDK` / `thief_agent.sdk.sdk.AgentSDK`) and never import
internal modules directly.

```python
from thief_agent.sdk.sdk import AgentSDK
from thief_agent.constants import Role
from thief_agent.security.signer import signer_from_env
from thief_agent.shared.config_validate import validate
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG

sdk = AgentSDK(Role.POLICE, "amireman-police", signer_from_env("amireman-police"), "uncommitted")
cfg = validate(DEFAULT_GAME_CONFIG)
```

## AgentSDK methods
| Method | Purpose |
|---|---|
| `local_series(cfg, seed=1234)` | Run a local six-sub-game series (role alternation, mutual audit, adaptive MetaController for both roles, per-opponent profiling). |
| `networked_series(url, token, cfg, seed=1234, terms=None)` (async) | Drive a distributed series over real FastMCP transport, incl. the P22 two-peer confirmation exchange. |
| `simulate(cfg, turns=10000)` | Deterministic headless batch (counters). |
| `emit_and_verify(out, gid, opponent, series, cfg, peer_commit=None, peer_ident=None)` | Write the four artifacts and run the integrity audit. |
| `verify_match(out, gid)` | Strict counted-match audit over emitted artifacts. |
| `tournament(cfg, role, seeds)` | Held-out champion selection (P12/P24). |

## Key building blocks (stable within the package)
- `strategy.production.make_gameplay_brain(role, seed, horizon, profile, credibility, baseline)`
  — the single production brain factory (adaptive `MetaController` by default).
- `strategy.meta.MetaController` — deterministic strategy selection; `.decide(obs)`,
  `.select(obs)`, `.log` (per-turn strategy + reason).
- `report.confirm` — `final_hash`, `make_confirmation`, `verify_confirmation`,
  `verify_mutual`, `confirmation_summary`, `responder_confirmation` (P22).
- `sim.rehearsal.validate_counted_evidence(dir, gid, signer_by_group)` — counted evidence check.
- `infra.tunnel.make_tunnel(cfg)` / `validate_public_endpoint(url)` — connectivity.
- `gui.replay_data` / `gui.window` — replay reconstruction and local-truth view.

Observations (`strategy.base.Observation`) expose only legally-visible fields
(self position, board size, barriers, received scent, last hint, step, barrier budget).
There is no opponent position field — the hidden-information boundary is structural.
