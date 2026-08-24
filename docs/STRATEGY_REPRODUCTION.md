# Reproduction (corrected)

Baselines: Police `00de656`, Thief `ac8d585`. Candidates: `improve/police-strategy`,
`improve/thief-strategy`. New: `sim/{scenarios,varied,stats}.py`, `tests/unit/test_varied.py`.

## Scenario-diverse benchmark
```
uv run python - <<'PY'
from thief_agent.sim.scenarios import generate
from thief_agent.sim.varied import evaluate
from thief_agent.sim.stats import paired_diff_ci
from thief_agent.sim.selfplay import BaselineMeta
from thief_agent.strategy.meta import MetaController
fac=lambda c,r: (lambda rng,h: c(r,rng,horizon=h,epsilon=0.0))
CP,BP=fac(MetaController,"police"),fac(BaselineMeta,"police")
CT,BT=fac(MetaController,"thief"),fac(BaselineMeta,"thief")
S=generate(600, seed=12345)
a=evaluate(S,BP,BT,"police",True); b=evaluate(S,CP,BT,"police",True)
at=evaluate(S,BP,BT,"thief");      ct=evaluate(S,BP,CT,"thief")
print("police", a["rate"], b["rate"], paired_diff_ci(a["ok_vector"],b["ok_vector"]))
print("thief ", at["rate"], ct["rate"], paired_diff_ci(at["ok_vector"],ct["ok_vector"]))
PY
```
The committed `evidence/strategy_summary.json` was produced by this same harness; the numbers
above regenerate from the modules listed here.
Gates: `uv run pytest --cov -q`, `ruff check .`, `ruff format --check .`,
`scripts/check_line_count.py`, `scripts/secret_scan.py`. Seeds are fixed and never tuned on.
