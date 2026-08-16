# net_engine.py

- **Source:** `src/thief_agent/peer/net_engine.py` L1
- **Layer:** `peer`  ·  **Degree:** 33
- **Community:** net_engine.py

## Neighbours

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
- `imports_from` smell.py
- `imports_from` mcp_server.py
- `imports_from` interop/engine.py
- `imports_from` [[nodes/src_thief_agent_peer_net_driver\|net_driver.py]]
- `contains` _grid_in()
- `contains` _grid_out()
- `contains` PeerHalf
- `rationale_for` One peer's half of a distributed sub-game: computes its own (secret) moves and…
- `imports_from` sealing.py
- `imports` make_step0_record()
- `imports_from` [[nodes/src_thief_agent_strategy_base\|base.py]]
- `imports` [[nodes/src_thief_agent_strategy_base_observation\|Observation]]
- `imports_from` [[nodes/src_thief_agent_strategy_firewall\|firewall.py]]
- `imports` enforce()
- `imports_from` hint_filter.py
- `imports` sanitize()
- `imports_from` test_interop_barrier_encoding.py
- `imports_from` test_interop_capture_claim_policy.py
- `imports_from` test_interop_capture_semantics.py

[[index]] · [[hot]] · [[architecture]]
