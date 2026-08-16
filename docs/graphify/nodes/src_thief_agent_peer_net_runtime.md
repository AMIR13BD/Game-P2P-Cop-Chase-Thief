# net_runtime.py

- **Source:** `src/thief_agent/peer/net_runtime.py` L1
- **Layer:** `peer`  ·  **Degree:** 33
- **Community:** net_runtime.py

## Neighbours

- `imports_from` [[nodes/src_thief_agent_exceptions\|exceptions.py]]
- `imports` [[nodes/src_thief_agent_exceptions_configerror\|ConfigError]]
- `imports_from` reliability.py
- `imports` new_session_id()
- `imports` ReliableCaller
- `imports_from` tunnel.py
- `imports` validate_public_endpoint()
- `imports_from` handshake.py
- `imports` local_hello()
- `imports_from` [[nodes/src_thief_agent_peer_net_driver\|net_driver.py]]
- `imports` default_connect()
- `imports` exchange_confirmation()
- `imports` make_send()
- `imports` play_subgame()
- `imports` role_for()
- `imports` score_row()
- `imports` technical_row()
- `imports_from` net_reconnect.py
- `imports` is_recoverable()
- `imports` recoverable_reason()
- `imports` run_isolated()
- `rationale_for` Driver of a distributed six-sub-game series over real FastMCP transport…
- `contains` run_networked()
- `contains` _run_session()
- `contains` _Series
- `imports_from` watchdog.py
- `imports` Watchdog
- `imports_from` config_hash.py
- `imports` config_sha256()
- `imports_from` profiling.py

[[index]] · [[hot]] · [[architecture]]
