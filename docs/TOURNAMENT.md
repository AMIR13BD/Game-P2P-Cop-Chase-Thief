# Tournament methodology & results

## Methodology (bounded, reproducible, held-out)
Tuning is **not** an unlimited search. `sim/tuning.py`:
1. Scores every portfolio strategy for each role on a **tuning** opponent set over a
   fixed tuning seed list.
2. Re-validates each strategy on a **disjoint held-out** opponent set over a disjoint
   held-out seed list.
3. Selects the champion by the held-out **primary metric** (Police: capture rate;
   Thief: survival rate) — never by self-play or tuning results alone.

Opponent sets (`sim/opponents/registry.py`):
- Tuning: `greedy`, `random`, `shortest`, `mobility`.
- Held-out (never seen during tuning): `corner_trap`, `barrier_heavy`, `deceptive`,
  `reference`. A latency-injected wrapper (`sim/opponents/latency.py`) is available for
  robustness runs.

Metrics available per matchup (`sim/metrics.py`): capture rate, survival rate, score,
illegal/diagonal actions, fallback rate, timeout rate, decision-time mean/p50/p95, and
per-opponent/per-role breakdowns. Runs are deterministic in game logic (wall-clock
timing excluded from equality).

## Reproduce
```bash
uv run python -c "import json;from thief_agent.shared.config_validate import validate; \
from thief_agent.shared.defaults import DEFAULT_GAME_CONFIG; from thief_agent.sim.tuning import run_tuning; \
print(json.dumps(run_tuning(validate(DEFAULT_GAME_CONFIG), range(1,6), range(100,106)), indent=2))"
```
Full record (seeds, opponent sets, per-strategy tuning + held-out scores, runtime):
[`docs/tournament/champions.json`](tournament/champions.json).

## Results (held-out, tuning seeds 1–5, held-out seeds 100–105; 484 bounded games)
- **Police champion: `barrier`** — held-out capture rate **0.583** (others 0.29–0.33).
- **Thief champion: `endgame`** — held-out survival rate **0.958** (others 0.708–0.75).

The champions were selected on the held-out set; they beat every baseline and the
reference opponent there, so the selection is not overfit to self-play. Superiority is
claimed only from these measured held-out results.
