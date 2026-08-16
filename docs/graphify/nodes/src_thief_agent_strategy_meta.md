# meta.py

- **Source:** `src/thief_agent/strategy/meta.py` L1
- **Layer:** `strategy`  ·  **Degree:** 33
- **Community:** Board

## Neighbours

- `imports_from` champion_eval.py
- `imports_from` [[nodes/src_thief_agent_domain_board\|board.py]]
- `imports` [[nodes/src_thief_agent_domain_board_board\|Board]]
- `imports_from` selfplay.py
- `imports_from` ai_brain.py
- `imports_from` [[nodes/src_thief_agent_strategy_base\|base.py]]
- `imports` [[nodes/src_thief_agent_strategy_base_action\|Action]]
- `imports` [[nodes/src_thief_agent_strategy_base_brainbase\|BrainBase]]
- `imports` [[nodes/src_thief_agent_strategy_base_observation\|Observation]]
- `imports_from` [[nodes/src_thief_agent_strategy_belief\|belief.py]]
- `imports` [[nodes/src_thief_agent_strategy_belief_beliefmap\|BeliefMap]]
- `imports_from` [[nodes/src_thief_agent_strategy_firewall\|firewall.py]]
- `imports` enforce()
- `imports_from` graph.py
- `imports` [[nodes/src_thief_agent_strategy_graph_reachable_area\|reachable_area()]]
- `imports_from` hints.py
- `imports` biased_target()
- `contains` _confidence()
- `contains` [[nodes/src_thief_agent_strategy_meta_metacontroller\|MetaController]]
- `rationale_for` Adaptive meta-controller (P16): selects a whole strategy from the portfolio…
- `imports_from` [[nodes/src_thief_agent_strategy_moves\|moves.py]]
- `imports` move_toward()
- `imports_from` [[nodes/src_thief_agent_strategy_production\|production.py]]
- `imports_from` [[nodes/src_thief_agent_strategy_registry\|strategy/registry.py]]
- `imports` make_brain()
- `imports` portfolio()
- `imports_from` test_decorner.py
- `imports_from` test_meta.py
- `imports_from` test_production_integration.py
- `imports_from` test_selfplay.py

[[index]] · [[hot]] · [[architecture]]
