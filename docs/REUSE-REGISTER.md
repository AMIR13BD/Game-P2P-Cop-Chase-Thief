# Reuse register (course EULA)

The official reference (`_reference/Game-P2P-Cop-Chase`, © Dr. Yoram Segal / GTAI,
Educational-Use EULA) was studied and its **formats/patterns** adapted. Nothing was
copied wholesale; the code below is our own re-implementation. Attribution notes are
kept in the relevant source files.

| Our module | Reference source | What was reused | Modifications |
|---|---|---|---|
| `domain/crypto.py` | `domain/crypto.py` | canonical JSON + `SHA256(canonical|nonce)` commit format and audit shape (interop) | re-implemented; `secrets.compare_digest`; our exceptions |
| `domain/negotiation.py` | `domain/negotiation.py` | sign-terms / refuse-on-mismatch handshake shape | re-implemented; returns peer identity |
| `domain/protocol.py` | `domain/protocol.py` | public wire-field shape (`TurnMessage`) + sealed `StepRecord` | trimmed to Day-1 needs |
| `domain/board.py`,`constants.py` | `domain/board.py`,`constants.py` | grid geometry & neighbor idea | **king/diagonal movement removed**; orthogonal-only, fail-closed |
| `peer/sealing.py`,`shared/sysinfo.py` | `peer/sealing.py`,`shared/sysinfo.py` | Step-0 system-spec sealing idea | pluggable signer; official key BLOCKED-EXTERNAL |
| `shared/config.py` | `shared/config.py` | JSON-overrides-TOML precedence | re-implemented; stdlib `tomllib` |

(Thief repository — identical reuse posture.) Not reused (built fresh): strategy brains, belief map, firewall, turn engine, series
runner, simulator, CLI, quality-gate scripts.
