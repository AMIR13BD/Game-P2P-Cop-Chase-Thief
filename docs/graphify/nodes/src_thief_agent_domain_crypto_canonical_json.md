# canonical_json()

- **Source:** `src/thief_agent/domain/crypto.py` L19
- **Layer:** `domain`  ·  **Degree:** 31
- **Community:** canonical_json

## Neighbours

- `contains` [[nodes/src_thief_agent_domain_crypto\|crypto.py]]
- `calls` commit_of()
- `references` Any
- `rationale_for` Key-order-independent, compact JSON so both peers hash identical bytes.
- `imports` negotiation.py
- `calls` .verify_peer()
- `imports` idempotency.py
- `calls` .fingerprint()
- `imports` artifacts_util.py
- `calls` canon_hash()
- `imports` consensus.py
- `calls` consensus_sha()
- `imports` [[nodes/src_thief_agent_interop_friendly\|friendly.py]]
- `calls` _write()
- `imports` interop/ids.py
- `calls` derive_game_ids()
- `imports` report/artifacts.py
- `calls` log_sha256()
- `imports` confirm.py
- `calls` final_hash()
- `imports` report_writer.py
- `calls` build_result()
- `imports` verify.py
- `calls` verify_series()
- `imports` [[nodes/src_thief_agent_security_signer\|signer.py]]
- `calls` .sign()
- `imports` config_hash.py
- `calls` config_sha256()
- `calls` test_canonical_key_order_independent()
- `calls` test_canonical_bytes_are_exact_and_deterministic()

[[index]] · [[hot]] · [[architecture]]
