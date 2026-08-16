# moves.py

- **Source:** `src/thief_agent/strategy/moves.py` L1
- **Layer:** `strategy`  ·  **Degree:** 38
- **Community:** Action

## Neighbours

- `imports_from` features.py
- `imports_from` constants.py
- `imports_from` [[nodes/src_thief_agent_domain_board\|board.py]]
- `imports` [[nodes/src_thief_agent_domain_board_board\|Board]]
- `imports_from` rules.py
- `imports` legal_move_dirs()
- `imports_from` reference.py
- `imports_from` simple.py
- `imports_from` trap.py
- `imports_from` tricky.py
- `imports_from` uoh.py
- `imports_from` selfplay.py
- `imports_from` [[nodes/src_thief_agent_strategy_base\|base.py]]
- `imports` [[nodes/src_thief_agent_strategy_base_action\|Action]]
- `imports` [[nodes/src_thief_agent_strategy_base_observation\|Observation]]
- `imports_from` graph.py
- `imports` [[nodes/src_thief_agent_strategy_graph_distance_map\|distance_map()]]
- `imports_from` [[nodes/src_thief_agent_strategy_meta\|meta.py]]
- `contains` _dist_to()
- `contains` [[nodes/src_thief_agent_strategy_moves_legal_steps\|legal_steps()]]
- `contains` manhattan()
- `contains` move_away()
- `contains` move_toward()
- `rationale_for` Movement-selection helpers shared by every strategy. All return legal actions…
- `imports_from` police_barrier.py
- `imports_from` police_contain.py
- `imports_from` police_herding.py
- `imports_from` police_hybrid.py
- `imports_from` police_intercept.py
- `imports_from` police_ringbreak.py

[[index]] · [[hot]] · [[architecture]]
