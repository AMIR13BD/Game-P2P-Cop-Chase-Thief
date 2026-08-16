# net_driver.py

- **Source:** `src/thief_agent/peer/net_driver.py` L1
- **Layer:** `peer`  ·  **Degree:** 32
- **Community:** net_runtime.py

## Neighbours

- `imports_from` constants.py
- `imports` complement()
- `imports` Role
- `imports_from` domain/__init__.py
- `imports_from` domain/scoring.py
- `imports_from` [[nodes/src_thief_agent_exceptions\|exceptions.py]]
- `imports` ExhaustedRetriesError
- `imports` ProtocolError
- `imports_from` tunnel.py
- `imports` tunnel_headers()
- `contains` brain()
- `contains` default_connect()
- `contains` exchange_confirmation()
- `contains` make_send()
- `contains` play_subgame()
- `rationale_for` Driver-side helpers for the networked series: reliable send, per-sub-game loop,…
- `contains` role_for()
- `contains` score_row()
- `contains` technical_row()
- `contains` transport_reason()
- `imports_from` [[nodes/src_thief_agent_peer_net_engine\|net_engine.py]]
- `imports` PeerHalf
- `imports_from` net_reconnect.py
- `imports_from` [[nodes/src_thief_agent_peer_net_runtime\|net_runtime.py]]
- `imports_from` confirm.py
- `imports` confirmation_summary()
- `imports` final_hash()
- `imports` make_confirmation()
- `imports_from` [[nodes/src_thief_agent_strategy_production\|production.py]]
- `imports` make_gameplay_brain()

[[index]] · [[hot]] · [[architecture]]
