# firewall.py

- **Source:** `src/thief_agent/strategy/firewall.py` L1
- **Layer:** `strategy`  ·  **Degree:** 30
- **Community:** firewall.py

## Neighbours

- `imports_from` rules.py
- `imports` barrier_cell()
- `imports` is_move_legal()
- `imports` legal_barrier_targets()
- `imports_from` [[nodes/src_thief_agent_peer_net_engine\|net_engine.py]]
- `imports_from` [[nodes/src_thief_agent_peer_turn_engine\|turn_engine.py]]
- `imports_from` evaluation.py
- `imports_from` ai_brain.py
- `imports_from` [[nodes/src_thief_agent_strategy_base\|base.py]]
- `imports` [[nodes/src_thief_agent_strategy_base_action\|Action]]
- `imports` [[nodes/src_thief_agent_strategy_base_observation\|Observation]]
- `imports_from` fallback.py
- `imports` [[nodes/src_thief_agent_strategy_fallback_safe_fallback\|safe_fallback()]]
- `contains` enforce()
- `contains` is_legal()
- `rationale_for` Legality firewall: validate a proposed action; substitute a legal fallback.
- `imports_from` [[nodes/src_thief_agent_strategy_meta\|meta.py]]
- `imports_from` test_brains.py
- `imports_from` test_advisor.py
- `imports_from` test_advisor_client.py
- `imports_from` test_belief_firewall.py
- `imports_from` test_decorner.py
- `imports_from` test_helpers_coverage.py
- `imports_from` test_meta.py
- `imports_from` test_opponents_eval.py
- `imports_from` test_police_portfolio.py
- `imports_from` test_production_integration.py
- `imports_from` test_stress.py
- `imports_from` test_thief_portfolio.py
- `imports_from` test_trap_opponents.py

[[index]] · [[hot]] · [[architecture]]
