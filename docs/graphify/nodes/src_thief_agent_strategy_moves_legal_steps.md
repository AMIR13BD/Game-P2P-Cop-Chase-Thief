# legal_steps()

- **Source:** `src/thief_agent/strategy/moves.py` L12
- **Layer:** `strategy`  ·  **Degree:** 43
- **Community:** Action

## Neighbours

- `imports` features.py
- `calls` candidate_actions()
- `references` [[nodes/src_thief_agent_domain_board_board\|Board]]
- `calls` legal_move_dirs()
- `imports` reference.py
- `calls` .decide()
- `imports` simple.py
- `calls` .decide()
- `calls` .decide()
- `calls` .decide()
- `imports` tricky.py
- `calls` .decide()
- `imports` uoh.py
- `calls` .decide()
- `calls` .decide()
- `uses` [[nodes/src_thief_agent_strategy_base_observation\|Observation]]
- `contains` [[nodes/src_thief_agent_strategy_moves\|moves.py]]
- `calls` move_away()
- `calls` move_toward()
- `references` Cell
- `rationale_for` (direction, resulting_cell) for every legal move, STAY first.
- `imports` police_contain.py
- `calls` .decide()
- `imports` police_herding.py
- `calls` .decide()
- `imports` police_hybrid.py
- `calls` .decide()
- `imports` police_ringbreak.py
- `calls` .decide()
- `imports` thief_antisqueeze.py

[[index]] · [[hot]] · [[architecture]]
