# turn_engine.py

- **Source:** `src/thief_agent/peer/turn_engine.py` L1
- **Layer:** `peer`  ·  **Degree:** 44
- **Community:** turn_engine.py

## Neighbours

- `imports_from` champion_eval.py
- `imports_from` constants.py
- `imports_from` [[nodes/src_thief_agent_domain_board\|board.py]]
- `imports` [[nodes/src_thief_agent_domain_board_board\|Board]]
- `imports_from` capture.py
- `imports_from` [[nodes/src_thief_agent_domain_crypto\|crypto.py]]
- `imports` seal()
- `imports_from` domain/__init__.py
- `imports_from` protocol.py
- `imports` build_payload()
- `imports_from` rules.py
- `imports` barrier_cell()
- `imports` step()
- `imports_from` domain/scoring.py
- `imports_from` smell.py
- `imports_from` peer/__init__.py
- `imports_from` sealing.py
- `imports` make_step0_record()
- `imports_from` state_machine.py
- `contains` _obs()
- `rationale_for` Local sub-game engine: commit-reveal per turn, scent, capture/survival checks.…
- `contains` [[nodes/src_thief_agent_peer_turn_engine_run_sub_game\|run_sub_game()]]
- `contains` _state_str()
- `imports_from` sdk/series.py
- `imports_from` sim/engine.py
- `imports_from` evaluation.py
- `imports_from` varied.py
- `imports_from` [[nodes/src_thief_agent_strategy_base\|base.py]]
- `imports` [[nodes/src_thief_agent_strategy_base_observation\|Observation]]
- `imports_from` [[nodes/src_thief_agent_strategy_firewall\|firewall.py]]

[[index]] · [[hot]] · [[architecture]]
