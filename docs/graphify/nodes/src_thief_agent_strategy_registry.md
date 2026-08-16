# strategy/registry.py

- **Source:** `src/thief_agent/strategy/registry.py` L1
- **Layer:** `strategy`  ·  **Degree:** 36
- **Community:** reachable_area

## Neighbours

- `imports_from` selfplay.py
- `imports_from` tournament.py
- `imports_from` tuning.py
- `imports_from` [[nodes/src_thief_agent_strategy_meta\|meta.py]]
- `imports_from` police_barrier.py
- `imports` BarrierBrain
- `imports_from` police_contain.py
- `imports` ContainBrain
- `imports_from` police_greedy.py
- `imports` PoliceGreedyBrain
- `imports_from` police_herding.py
- `imports` HerdBrain
- `imports_from` police_hybrid.py
- `imports` PoliceHybridBrain
- `imports_from` police_intercept.py
- `imports` InterceptBrain
- `contains` make_brain()
- `contains` portfolio()
- `rationale_for` Named strategy portfolio: brain factories keyed by role. Used by the adaptive…
- `imports_from` thief_decorner.py
- `imports` DecornerBrain
- `imports_from` thief_distance.py
- `imports` ThiefDistanceBrain
- `imports_from` thief_endgame.py
- `imports` EndgameBrain
- `imports_from` thief_entropy.py
- `imports` EntropyBrain
- `imports_from` thief_escape.py
- `imports` EscapeBrain
- `imports_from` thief_evade.py

[[index]] · [[hot]] · [[architecture]]
