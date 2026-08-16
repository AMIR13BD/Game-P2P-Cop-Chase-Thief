# production.py

- **Source:** `src/thief_agent/strategy/production.py` L1
- **Layer:** `strategy`  ·  **Degree:** 37
- **Community:** production.py

## Neighbours

- `imports_from` param_sweep.py
- `imports_from` mcp_server.py
- `imports_from` interop/engine.py
- `imports_from` [[nodes/src_thief_agent_peer_net_driver\|net_driver.py]]
- `imports_from` sdk/series.py
- `imports` AIPrimaryBrain
- `imports_from` [[nodes/src_thief_agent_strategy_meta\|meta.py]]
- `imports` [[nodes/src_thief_agent_strategy_meta_metacontroller\|MetaController]]
- `imports` ContainBayesBrain
- `imports` ContainBrain
- `imports_from` police_greedy.py
- `imports` PoliceGreedyBrain
- `imports` RingBreakerBrain
- `contains` advisor_policy()
- `contains` baseline_brain()
- `contains` default_police()
- `contains` default_thief()
- `contains` make_gameplay_brain()
- `contains` police_specialist()
- `contains` production_brain()
- `rationale_for` Production brain factory (single source of truth for real gameplay). Selection…
- `contains` thief_specialist()
- `imports_from` rng.py
- `imports` [[nodes/src_thief_agent_strategy_rng_make_rng\|make_rng()]]
- `imports` AntiSqueezeBrain
- `imports_from` thief_distance.py
- `imports` ThiefDistanceBrain
- `imports` SurvivorBrain
- `imports_from` test_contain_bayes_play.py
- `imports_from` test_gui_replay_panel.py

[[index]] · [[hot]] · [[architecture]]
