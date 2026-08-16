# DevTestSigner

- **Source:** `src/thief_agent/security/signer.py` L23
- **Layer:** `security`  ·  **Degree:** 59
- **Community:** DevTestSigner

## Neighbours

- `contains` [[nodes/src_thief_agent_security_signer\|signer.py]]
- `method` .__init__()
- `method` .sign()
- `method` .verify()
- `references` peer_signer()
- `rationale_for` Development/test signer. Signatures are labelled 'devtest:'. Each instance may…
- `references` signer_from_env()
- `imports` sim/engine.py
- `calls` simulate()
- `imports` evaluation.py
- `calls` evaluate_matchup()
- `imports` varied.py
- `calls` run_one()
- `uses` signer()
- `uses` test_unreachable_opponent_yields_technical_series()
- `uses` test_e2e_networked_series()
- `uses` _game()
- `uses` _game()
- `uses` _records()
- `uses` _records()
- `uses` _records()
- `uses` test_credibility_only_from_audited_evidence()
- `uses` _police()
- `uses` _cop()
- `uses` test_cop_capture_claim_is_sealed_in_signed_record()
- `uses` test_meta_actions_always_legal_in_game()
- `uses` _half()
- `uses` test_play_subgame_capture()
- `uses` test_six_subgames_cross_boundary_without_technical()
- `uses` test_baseline_mode_available()

[[index]] · [[hot]] · [[architecture]]
