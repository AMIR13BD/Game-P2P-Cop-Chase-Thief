# Self-play A/B method

`sim/selfplay.py` compares the **candidate** `MetaController` against a **faithful frozen
baseline** in ONE process — no strategy files are copied between repositories.

- `BaselineMeta(MetaController)` re-declares the frozen `_police_choice`/`_thief_choice`/
  `select` verbatim (commit 00de656 / ac8d585).
- **Faithfulness proof:** a git worktree checked out at the baseline commit runs
  baseline-vs-baseline; its per-seed (outcome, steps) is **byte-identical** to
  `BaselineMeta`-vs-`BaselineMeta` (police seeds 1–120, thief 1–100). `tests/unit/
  test_selfplay.py` locks the frozen selection rules and that the candidate differs and wins.
- Matchups: A base/base, B candidate-Police/base-Thief, C base-Police/candidate-Thief,
  D candidate/candidate. `run_matchup(cfg, police_cls, thief_cls, seeds, measure)`.
- Deterministic: identical seeds -> identical decisions/outcomes (timing excluded).
- Engine: `peer.turn_engine.run_sub_game` via `sim.evaluation.evaluate_matchup` (records
  capture/survival/technical, illegal, fallback, decision-time p50/p95/max).
