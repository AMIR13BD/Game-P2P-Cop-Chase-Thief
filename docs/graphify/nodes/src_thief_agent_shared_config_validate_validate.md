# validate()

- **Source:** `src/thief_agent/shared/config_validate.py` L52
- **Layer:** `shared`  ·  **Degree:** 46
- **Community:** validate

## Neighbours

- `calls` capture_live()
- `calls` capture_replay()
- `calls` sweep()
- `imports` [[nodes/src_thief_agent_commands\|commands.py]]
- `calls` cmd_artifacts()
- `calls` cmd_netplay()
- `calls` cmd_series()
- `calls` cmd_simulate()
- `imports` commands_gui.py
- `calls` _cfg()
- `imports` commands_report.py
- `calls` cmd_tournament()
- `imports` serve.py
- `calls` run()
- `contains` [[nodes/src_thief_agent_shared_config_validate\|config_validate.py]]
- `calls` _check_positions()
- `calls` _check_values()
- `calls` flatten()
- `calls` _require_structure()
- `imports` scenarios.py
- `calls` cfg()
- `calls` test_unreachable_opponent_yields_technical_series()
- `calls` _build()
- `calls` test_invalid_config_maps_to_technical()
- `calls` test_missing_category_fails_closed()
- `calls` test_missing_one_field_fails_closed()
- `calls` test_start_position_off_board_rejected()
- `calls` test_unknown_field_rejected()
- `calls` test_diagonal_moveset_rejected()
- `calls` test_empty_map_area_defaults_new_york()

[[index]] · [[hot]] · [[architecture]]
