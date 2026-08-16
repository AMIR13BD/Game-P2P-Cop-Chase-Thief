# BrainBase

- **Source:** `src/thief_agent/strategy/base.py` L27
- **Layer:** `strategy`  ·  **Degree:** 64
- **Community:** Action

## Neighbours

- `imports` reference.py
- `inherits` ReferenceBrain
- `imports` simple.py
- `inherits` GreedyBrain
- `inherits` MobilityBrain
- `inherits` RandomWalkBrain
- `inherits` ShortestPathBrain
- `imports` trap.py
- `inherits` ChokeControllerBrain
- `inherits` DelayedCornerBrain
- `inherits` EdgeHerderBrain
- `inherits` SealAssistBrain
- `imports` tricky.py
- `inherits` BarrierHeavyBrain
- `inherits` CornerTrapBrain
- `inherits` DeceptiveBrain
- `imports` uoh.py
- `inherits` UohCopBrain
- `inherits` UohThiefBrain
- `imports` ai_brain.py
- `uses` AIPrimaryBrain
- `contains` [[nodes/src_thief_agent_strategy_base\|base.py]]
- `method` .decide()
- `method` .hint()
- `method` .__init__()
- `rationale_for` Base class for all brains. Subclasses override `decide`.
- `imports` [[nodes/src_thief_agent_strategy_meta\|meta.py]]
- `uses` [[nodes/src_thief_agent_strategy_meta_metacontroller\|MetaController]]
- `references` ._brain()
- `imports` police_barrier.py

[[index]] · [[hot]] · [[architecture]]
