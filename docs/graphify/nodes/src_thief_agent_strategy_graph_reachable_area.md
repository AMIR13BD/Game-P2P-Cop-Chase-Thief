# reachable_area()

- **Source:** `src/thief_agent/strategy/graph.py` L27
- **Layer:** `strategy`  ·  **Degree:** 39
- **Community:** reachable_area

## Neighbours

- `imports` features.py
- `calls` _barrier_candidates()
- `calls` tactical_context()
- `references` [[nodes/src_thief_agent_domain_board_board\|Board]]
- `imports` uoh.py
- `calls` .decide()
- `imports` selfplay.py
- `calls` ._b_police()
- `imports` varied.py
- `calls` .decide()
- `contains` graph.py
- `calls` [[nodes/src_thief_agent_strategy_graph_distance_map\|distance_map()]]
- `references` Cell
- `rationale_for` Size of `start`'s connected component (number of reachable cells).
- `imports` [[nodes/src_thief_agent_strategy_meta\|meta.py]]
- `calls` ._police_choice()
- `imports` police_barrier.py
- `calls` best_barrier()
- `calls` _thief_area()
- `imports` police_contain.py
- `calls` _containment()
- `imports` police_herding.py
- `calls` herd_target()
- `imports` police_hybrid.py
- `calls` .decide()
- `imports` police_intercept.py
- `calls` ._intercept_cell()
- `imports` police_ringbreak.py
- `calls` ._cut()
- `imports` thief_antisqueeze.py

[[index]] · [[hot]] · [[architecture]]
