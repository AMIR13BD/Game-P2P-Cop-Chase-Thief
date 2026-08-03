# Ablation (scenario-diverse)

| Feature | Metric | Baseline | +feature | Note |
|---|---|---|---|---|
| Police barrier-first | capture | 0.232 | 0.487 | improves all boards/opponents |
| Thief escape-default | survival | 0.768 | 0.915 | improves all boards |
| Thief +decorner (trap fix) | corner_trap survival | 0.040 (old cand) | **0.510** | primary 0.915->0.930, cvc 0.833->0.865 |

decorner ablation (vs the escape-only candidate), scenario-diverse:
- ON  : corner_trap 0.51, delayed_corner 0.38, primary 0.930, cvc 0.865, deceptive 0.835, random 0.925.
- OFF : corner_trap 0.04, delayed_corner 0.003, primary 0.915, cvc 0.833, deceptive 0.875, random 0.970.

The single decorner branch fixes both corner-herding opponents (corner_trap, delayed_corner)
and slightly improves primary/cvc, at a small cost vs the two randomised opponents. It fires
only in low-degree corners on barrier-free boards (a tiny fraction of primary/cvc turns).
