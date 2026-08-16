# SubEngine

- **Source:** `src/thief_agent/interop/engine.py` L31
- **Layer:** `interop`  ·  **Degree:** 29
- **Community:** SubEngine

## Neighbours

- `contains` interop/engine.py
- `rationale_for` One side of one sub-game against a remote opponent (fresh per sub-game).
- `method` .concede()
- `method` .__init__()
- `method` .receive()
- `method` .records()
- `method` .step()
- `method` .survived()
- `method` .take_turn()
- `method` .tokens_used()
- `imports` runtime.py
- `uses` SubGameRuntime
- `calls` .__init__()
- `uses` TurnMessage
- `uses` test_capture_leg_is_truthful_with_no_post_capture_move()
- `uses` test_g1_5_6_regression_landing_becomes_capture()
- `uses` test_missing_claim_is_not_a_capture_even_on_coincidence()
- `uses` test_move_to_empty_cell_claims_post_move_cell_and_thief_is_not_caught()
- `uses` test_coincidence_without_capture_claim_is_not_capture()
- `uses` test_valid_capture_claim_captures_seals_response_and_holds()
- `uses` test_wrong_capture_claim_continues_and_seals_false_response()
- `uses` test_caught_concession_holds_position_and_seals_claim_response()
- `uses` test_missed_claim_is_not_caught_and_thief_continues()
- `uses` test_real_police_engine_marks_win_on_caught_claim()
- `uses` test_subengine_binds_the_given_commit_into_step0()
- `uses` test_caught_concession_seals_stay_not_hold_and_no_physical_move()
- `uses` test_wrong_capture_claim_continues()
- `uses` _thief_turns()
- `uses` test_subengine_emits_spec_additive_scent_not_compat_beacon()

[[index]] · [[hot]] · [[architecture]]
