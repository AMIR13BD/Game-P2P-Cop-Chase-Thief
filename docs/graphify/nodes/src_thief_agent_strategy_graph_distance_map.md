# distance_map()

- **Source:** `src/thief_agent/strategy/graph.py` L9
- **Layer:** `strategy`  ·  **Degree:** 34
- **Community:** reachable_area

## Neighbours

- `imports` features.py
- `calls` _barrier_candidates()
- `calls` tactical_context()
- `references` [[nodes/src_thief_agent_domain_board_board\|Board]]
- `imports` uoh.py
- `calls` .decide()
- `calls` .decide()
- `imports` varied.py
- `calls` .decide()
- `contains` graph.py
- `calls` component_of()
- `references` Cell
- `rationale_for` BFS hop-distance from `start` to every reachable passable cell.
- `calls` [[nodes/src_thief_agent_strategy_graph_reachable_area\|reachable_area()]]
- `calls` reachable_set()
- `imports` [[nodes/src_thief_agent_strategy_moves\|moves.py]]
- `calls` _dist_to()
- `imports` police_barrier.py
- `calls` best_barrier()
- `imports` police_contain.py
- `calls` .decide()
- `imports` police_ringbreak.py
- `imports` thief_antisqueeze.py
- `calls` .decide()
- `imports` thief_decorner.py
- `calls` .decide()
- `imports` thief_entropy.py
- `calls` ._ranked()
- `imports` thief_escape.py
- `calls` .decide()

[[index]] · [[hot]] · [[architecture]]
