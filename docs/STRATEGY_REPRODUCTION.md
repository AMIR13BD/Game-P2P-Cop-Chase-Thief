# Reproduction

Baseline commits: Police `00de656`, Thief `ac8d585`. Candidate branches:
`improve/police-strategy`, `improve/thief-strategy`. Change: `src/<agent>/strategy/meta.py`
selection; harness `src/<agent>/sim/selfplay.py`; tests `tests/unit/test_{meta,selfplay}.py`.

## Faithfulness (frozen baseline)
```
git worktree add /tmp/base <BASELINE_COMMIT>
PYTHONPATH=/tmp/base/src .venv/bin/python -c "<baseline-vs-baseline per-seed dump>"
# compare to sim.selfplay.BaselineMeta per-seed dump -> identical
```

## Held-out benchmark (regenerates evidence/strategy_summary.json)
```
.venv/bin/python - <<'PY'
from <agent>.sim.selfplay import BaselineMeta, run_matchup
from <agent>.strategy.meta import MetaController
from <agent>.shared.config_validate import validate
from <agent>.shared.defaults import DEFAULT_GAME_CONFIG
cfg=validate(DEFAULT_GAME_CONFIG); ho=list(range(20000,20500))
print("cand police cap", run_matchup(cfg, MetaController, BaselineMeta, ho, "police")["capture_rate"])
print("cand thief surv", run_matchup(cfg, BaselineMeta, MetaController, ho, "thief")["survival_rate"])
PY
```

## Quality gates
```
uv run pytest --cov -q   # >=85% coverage (excl. 4 sandbox-blocked live-server tests)
uv run ruff check . && uv run ruff format --check .
python scripts/check_line_count.py && python scripts/secret_scan.py
python -m <agent> artifacts --out /tmp/x --game-id g --opponent o --seed 4242  # audit_passed=True
```
Seeds: dev 1–300 & 500–649; held-out 20000–20499 / 20000–20299 / 21000–21299 (never tuned).
