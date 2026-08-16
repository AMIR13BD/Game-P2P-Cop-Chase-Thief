# exceptions.py

- **Source:** `src/thief_agent/exceptions.py` L1
- **Layer:** `(package root)`  ·  **Degree:** 50
- **Community:** exceptions.py

## Neighbours

- `imports_from` [[nodes/src_thief_agent_commands\|commands.py]]
- `imports_from` [[nodes/src_thief_agent_domain_crypto\|crypto.py]]
- `imports_from` moveset.py
- `imports_from` negotiation.py
- `contains` ArtifactError
- `contains` [[nodes/src_thief_agent_exceptions_configerror\|ConfigError]]
- `contains` CryptoError
- `contains` ExhaustedRetriesError
- `contains` IllegalTransitionError
- `contains` NetworkError
- `contains` ProtocolError
- `contains` QueueFullError
- `contains` RateLimitError
- `rationale_for` Typed errors for fail-closed behavior across the agent.
- `contains` TechnicalLossError
- `imports_from` replay_verify.py
- `imports_from` reliability.py
- `imports_from` tunnel.py
- `imports_from` interop/client.py
- `imports_from` negotiate.py
- `imports_from` [[nodes/src_thief_agent_interop_series\|interop/series.py]]
- `imports_from` server.py
- `imports_from` terms.py
- `imports_from` audit.py
- `imports_from` deadline.py
- `imports_from` handshake.py
- `imports_from` [[nodes/src_thief_agent_peer_net_driver\|net_driver.py]]
- `imports_from` [[nodes/src_thief_agent_peer_net_runtime\|net_runtime.py]]
- `imports_from` state_machine.py
- `imports_from` technical.py

[[index]] · [[hot]] · [[architecture]]
