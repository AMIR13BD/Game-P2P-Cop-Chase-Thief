# ConfigError

- **Source:** `src/thief_agent/exceptions.py` L4
- **Layer:** `(package root)`  ·  **Degree:** 42
- **Community:** config_validate.py

## Neighbours

- `imports` [[nodes/src_thief_agent_commands\|commands.py]]
- `uses` cmd_series()
- `imports` moveset.py
- `calls` validate_move_set()
- `contains` [[nodes/src_thief_agent_exceptions\|exceptions.py]]
- `rationale_for` Raised on missing, malformed, or spec-violating configuration.
- `imports` tunnel.py
- `calls` tunnel_headers()
- `imports` terms.py
- `calls` validate_terms()
- `imports` handshake.py
- `calls` agree_config()
- `calls` check_compatibility()
- `imports` [[nodes/src_thief_agent_peer_net_runtime\|net_runtime.py]]
- `calls` _run_session()
- `imports` technical.py
- `imports` [[nodes/src_thief_agent_shared_config_validate\|config_validate.py]]
- `calls` _check_positions()
- `calls` _check_values()
- `calls` _require_structure()
- `imports` version.py
- `calls` check_config_version()
- `uses` test_agree_config_match_and_mismatch()
- `uses` test_incompatible_refused()
- `uses` test_missing_category_fails_closed()
- `uses` test_missing_one_field_fails_closed()
- `uses` test_start_position_off_board_rejected()
- `uses` test_unknown_field_rejected()
- `uses` test_diagonal_moveset_rejected()
- `uses` test_fixed_value_change_rejected()

[[index]] · [[hot]] · [[architecture]]
