# Day-1 acceptance evidence (thief) — after Phase-2.1 compliance repair

Gate target: **G-MINPLAYABLE** (explicit TODO task T-0405).

| Item | Result |
|---|---|
| uv sync | clean (Python 3.14.4, pytest 9.1.1, ruff 0.16.1) |
| pytest | 89 passed, 0 failed, 0 skipped |
| ruff check / format --check | pass / pass |
| line-count gate (<=150 physical) | OK |
| secret scan (tree) | no secrets |
| py_compile (type/syntax) | OK (mypy not configured for Day-1) |
| Appendix F config (schema_version 1.2) | all mandatory fields validated; fail-closed on missing/unknown/fixed/min |
| config_sha256 golden | 1355b4c57daa1b5d83819b228c90e7ead09efb90fac16e0053f20a0d3c44813d (identical in both repos) |
| scent 5x5 kernel | exact PDF values; decay 0.90->0.81; cap 0.9; edge-clipped |
| Step-0 github_commit | real repository commit hash (audited for presence+format) |
| Step-0 dev signature | verified by audit; official signer BLOCKED-EXTERNAL |
| technical-loss path | invalid transition/crypto/config/audit -> outcome "technical", 0/0 |
| six-sub-game series | completes; role_sequence = thief,police,thief,police,thief,police |
| deterministic same-seed | identical trajectories/outcomes/scores |
| tamper + malformed-audit | detected; audit fails closed (no crash) |
| 10,000-turn simulation | 10,010 turns: 0 illegal, 0 diagonal, 0 timeouts, 0 exceptions |

Not in Day-1 scope: FastMCP/networking, Gmail, tunnels, GUI, Replay Viewer,
championship strategies, opponent profiling, tournaments.
