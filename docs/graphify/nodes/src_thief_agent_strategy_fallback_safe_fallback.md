# safe_fallback()

- **Source:** `src/thief_agent/strategy/fallback.py` L7
- **Layer:** `strategy`  ·  **Degree:** 30
- **Community:** Action

## Neighbours

- `calls` legal_move_dirs()
- `imports` reference.py
- `calls` .decide()
- `imports` simple.py
- `calls` .decide()
- `calls` .decide()
- `imports` trap.py
- `calls` _flee()
- `imports` tricky.py
- `calls` .decide()
- `imports` uoh.py
- `calls` .decide()
- `uses` [[nodes/src_thief_agent_strategy_base_action\|Action]]
- `uses` [[nodes/src_thief_agent_strategy_base_observation\|Observation]]
- `contains` fallback.py
- `rationale_for` Always returns a legal action: prefer a real move, else STAY.
- `imports` [[nodes/src_thief_agent_strategy_firewall\|firewall.py]]
- `calls` enforce()
- `imports` police_barrier.py
- `calls` .decide()
- `imports` police_contain.py
- `calls` .decide()
- `imports` police_greedy.py
- `calls` .decide()
- `imports` police_herding.py
- `calls` .decide()
- `imports` police_hybrid.py
- `calls` .decide()
- `imports` police_intercept.py
- `calls` .decide()

[[index]] · [[hot]] · [[architecture]]
