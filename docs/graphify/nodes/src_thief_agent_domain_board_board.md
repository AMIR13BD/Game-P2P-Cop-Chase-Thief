# Board

- **Source:** `src/thief_agent/domain/board.py` L8
- **Layer:** `domain`  ·  **Degree:** 216
- **Community:** Board

## Neighbours

- `imports` features.py
- `references` _barrier_candidates()
- `references` candidate_actions()
- `references` _dest()
- `contains` [[nodes/src_thief_agent_domain_board\|board.py]]
- `method` .add_barrier()
- `method` .all_cells()
- `method` .in_bounds()
- `method` .__init__()
- `method` .neighbors()
- `method` .passable()
- `imports` capture.py
- `uses` thief_trapped()
- `imports` rules.py
- `uses` is_move_legal()
- `uses` legal_barrier_targets()
- `uses` legal_move_dirs()
- `imports` smell.py
- `uses` compat_update()
- `uses` emission_delta()
- `uses` step_update()
- `imports` evidence.py
- `calls` observation_at()
- `imports` heatmap.py
- `calls` belief_buckets()
- `imports` [[nodes/src_thief_agent_peer_net_engine\|net_engine.py]]
- `calls` .__init__()
- `imports` [[nodes/src_thief_agent_peer_turn_engine\|turn_engine.py]]
- `calls` [[nodes/src_thief_agent_peer_turn_engine_run_sub_game\|run_sub_game()]]
- `imports` evaluation.py

[[index]] · [[hot]] · [[architecture]]
