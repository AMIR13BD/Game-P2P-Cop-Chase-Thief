# Day-1 acceptance evidence (thief)

Gate target: **G-MINPLAYABLE**. Evidence captured on the Day-1 checkpoint.

| Item | Result |
|---|---|
| `uv sync` | clean (police-agent + pytest 9.1.1 + ruff 0.16.1, Python 3.14.4) |
| pytest | 51 passed, 0 failed, 0 skipped |
| ruff check | All checks passed |
| ruff format --check | all files formatted |
| line-count gate (≤150 physical) | OK (max file = 130 lines (thief mirror)) |
| secret scan | no secrets detected |
| py_compile (type/syntax) | OK (mypy not configured for Day-1) |
| local six-sub-game series | completes; role_sequence = thief,police,thief,police,thief,police |
| per-sub-game mutual audit | all passed (commit-reveal verified) |
| 10,000-turn simulation | 10,010 turns: 0 illegal, 0 diagonal, 0 timeouts, 0 exceptions |
| deterministic replay (same seed x2) | identical trajectories/outcomes/scores |
| crypto tamper (payload/nonce/commit) | all rejected; audit reports failed step |
| diagonal moves | rejected (config + firewall); 0 in simulation |
| malformed move config | fails closed (no king fallback) |
| official Step-0 signer | BLOCKED-EXTERNAL (dev/test signer used) |

Not in Day-1 scope (later batches): FastMCP/networking, Gmail, tunnels, GUI,
Replay Viewer, championship strategies, opponent profiling, tournaments.
