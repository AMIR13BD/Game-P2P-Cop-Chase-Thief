# Experiment log

Dev seeds (diagnosis/tuning): 1–300, 500–649. Corrected held-out **scenarios** (final):
600 @ seed 12345; opponent matrix 200 @ seed 777. Never tuned on.

## Accepted
- Police barrier-first `_police_choice` (paired +0.255 capture).
- Thief escape-default `_thief_choice` (paired +0.147 survival).

## Rejected
- V2 barrier-first + endgame capture-dash: worse than pure barrier-first.

## Evaluation correction (this task)
- Found: the fixed-config 500-seed benchmark repeated ONE scenario (deterministic agents)
  and overstated results. Replaced with scenario-diverse paired evaluation (grid/starts/
  distance/budget/limit varied; 568/600 unique trajectories).
- Found (genuine regression): Thief vs corner_trap 0.20->0.04, surfaced only by scenario
  diversity. Reported; strategy left unchanged per task instruction ("do not change yet").
