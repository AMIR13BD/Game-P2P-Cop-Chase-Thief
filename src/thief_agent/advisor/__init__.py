"""OpenAI tactical-advisor layer.

The advisor is a tactical *selector* on top of the deterministic engine: it may only
choose among pre-validated legal candidate actions, and any failure/timeout/budget
issue falls back to the deterministic choice. It never generates actions, never sees
hidden opponent truth, and never touches protocol or the frozen capture-claim."""
