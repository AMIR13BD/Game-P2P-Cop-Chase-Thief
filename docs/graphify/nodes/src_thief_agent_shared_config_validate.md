# config_validate.py

- **Source:** `src/thief_agent/shared/config_validate.py` L1
- **Layer:** `shared`  ·  **Degree:** 47
- **Community:** config_validate.py

## Neighbours

- `imports_from` capture_gui.py
- `imports_from` param_sweep.py
- `imports_from` [[nodes/src_thief_agent_commands\|commands.py]]
- `imports_from` commands_gui.py
- `imports_from` commands_report.py
- `imports_from` moveset.py
- `imports` validate_move_set()
- `imports_from` [[nodes/src_thief_agent_exceptions\|exceptions.py]]
- `imports` [[nodes/src_thief_agent_exceptions_configerror\|ConfigError]]
- `imports_from` serve.py
- `imports_from` config_spec.py
- `contains` _check_positions()
- `contains` _check_values()
- `contains` flatten()
- `rationale_for` Strict Appendix F validation. Fail closed on missing/unknown fields, wrong…
- `contains` _require_structure()
- `contains` [[nodes/src_thief_agent_shared_config_validate_validate\|validate()]]
- `imports_from` shared/__init__.py
- `imports_from` scenarios.py
- `imports_from` conftest.py
- `imports_from` test_e2e_fault.py
- `imports_from` test_mutual_audit.py
- `imports_from` test_technical_loss.py
- `imports_from` test_config.py
- `imports_from` test_config_required.py
- `imports_from` test_contain_bayes.py
- `imports_from` test_contain_bayes_play.py
- `imports_from` test_gui_replay_panel.py
- `imports_from` test_gui_tk_layer.py
- `imports_from` test_hints.py

[[index]] · [[hot]] · [[architecture]]
