# MetaController

- **Source:** `src/thief_agent/strategy/meta.py` L27
- **Layer:** `strategy`  ·  **Degree:** 43
- **Community:** make_rng

## Neighbours

- `uses` main()
- `imports` selfplay.py
- `inherits` BaselineMeta
- `imports` ai_brain.py
- `uses` AIPrimaryBrain
- `calls` .__init__()
- `uses` [[nodes/src_thief_agent_strategy_base_action\|Action]]
- `uses` [[nodes/src_thief_agent_strategy_base_brainbase\|BrainBase]]
- `uses` [[nodes/src_thief_agent_strategy_base_observation\|Observation]]
- `uses` [[nodes/src_thief_agent_strategy_belief_beliefmap\|BeliefMap]]
- `contains` [[nodes/src_thief_agent_strategy_meta\|meta.py]]
- `method` ._brain()
- `method` .decide()
- `method` .hint()
- `method` ._hint_biased()
- `method` .__init__()
- `method` ._police_choice()
- `method` .select()
- `method` ._thief_choice()
- `method` .update_score()
- `imports` [[nodes/src_thief_agent_strategy_production\|production.py]]
- `uses` police_specialist()
- `uses` production_brain()
- `uses` thief_specialist()
- `uses` test_thief_selects_survivor_in_interior()
- `uses` test_thief_selects_survivor_when_cornered()
- `uses` test_controlled_exploration_bounded_and_logged()
- `uses` test_meta_actions_always_legal_in_game()
- `uses` test_meta_deterministic_same_seed()
- `uses` test_meta_logs_strategy_and_reason()

[[index]] · [[hot]] · [[architecture]]
