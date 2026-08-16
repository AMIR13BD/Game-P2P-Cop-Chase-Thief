# Reverse engineering the codebase from the Graphify knowledge graph

Every claim below is read out of [`graph/graph.json`](graph/graph.json) — 3,231 nodes and
7,385 edges extracted from the committed tree at `efde472`. Figures are reproducible with
the commands in [`README.md`](README.md); nothing here is asserted from prior knowledge of
the code. Start at [[index]], then [[architecture]] and [[hot]].

---

## 1. What the graph is

Graphify parsed the committed tree with tree-sitter (AST extraction, no LLM); 334 files
contributed nodes. The result is a directed graph of classes, functions, modules and documents, clustered into **177
communities**. Nodes carry their source file and line; edges carry a relation (`calls`,
`imports`, `defines`, …) and a confidence.

## 2. Main modules and their weight

Node counts per layer, straight from the graph:

| Layer | Nodes | What the graph says it is |
|---|---:|---|
| `tests` | 1110 | The largest single layer — roughly a third of all nodes |
| `strategy` | 362 | Largest production layer: the brains and their support |
| `docs` | 358 | Documentation is a first-class part of the corpus |
| `interop` | 239 | The official league wire path |
| `sim` | 170 | Offline evaluation harness |
| `gui` | 162 | Live GUI + replay viewer |
| `peer` | 91 | Turn engine, sealing, deadlines, reconnect |
| `infra` | 84 | MCP server/client, tunnel, Gmail |
| `domain` | 69 | Board, rules, capture, scoring, crypto, scent |
| `report` | 55 | Artifacts and verification |
| `shared` | 45 | Config, gatekeeper, version |
| `advisor` | 30 | Optional LLM advisor |
| `security` | 28 | Signing and auth |
| `sdk` | 24 | Public facade |

The first observation is a *ratio*: `tests` (1110) outnumbers the entire production
surface of `strategy` + `interop` + `peer` + `domain` (761). Test density is not a claim in
the README here — it is visible in the graph's shape.

The second is that `domain` is **small** (69 nodes) relative to `strategy` (362). The rules
of the game are a compact, stable core; almost all the volume is in deciding what to do
within them.

## 3. High-connectivity nodes (the hubs)

| Rank | Node | Degree | Layer |
|---:|---|---:|---|
| 1 | `Board` | 216 | `domain` |
| 2 | `Observation` | 163 | `strategy` |
| 3 | `Action` | 117 | `strategy` |
| 4 | `BeliefMap` | 79 | `strategy` |
| 5 | `board.py` | 74 | `domain` |
| 6 | `make_rng()` | 69 | `strategy` |
| 7 | `BrainBase` | 64 | `strategy` |
| 8 | `base.py` | 62 | `strategy` |
| 9 | `DevTestSigner` | 60 | `security` |

The top four are all **data types, not behaviour**: a board, an observation, an action, a
belief. The graph is telling us the system is organised around a small vocabulary of shared
structures that everything else agrees on — which is why `strategy` can hold twenty-odd
interchangeable brains without them knowing about each other.

`make_rng()` at rank 6 is worth noting: a seeded RNG factory is reachable from most of the
codebase, which is the structural reason determinism holds end-to-end.

`DevTestSigner` at rank 9 is a *test* signer with production-level connectivity — expected
for a commit-reveal system where nearly every path needs to seal something, but it is the
one hub whose prominence is an artefact of testing rather than of runtime.

## 4. Layer separation — the dependency directions

This is where the graph is most informative, because direction is checkable.

| From → To | Edges | Reading |
|---|---:|---|
| `strategy` → `domain` | 160 | Brains consume the rules |
| `peer` → `domain` | 50 | Turn engine consumes the rules |
| `interop` → `domain` | 24 | Wire layer consumes the rules |
| `peer` → `strategy` | 21 | Engine invokes brains |
| `gui` → `domain` | 15 | Presentation reads the model |
| `gui` → `strategy` | 9 | Presentation reads belief types |
| `advisor` → `strategy` | 22 | Optional advisor plugs into strategy |
| `sim` → `strategy` | 229 | Evaluation harness is the heaviest consumer |
| **`domain` → anything** | **13, all to package root** | — |

**`domain` has no upward dependencies.** Its only 13 outbound edges go to the package root
(`exceptions.py`, `constants.py`). It does not import `strategy`, `peer`, `interop` or
`gui`. That is a clean layered architecture confirmed from the artefact rather than from
intent: the rules of the game do not know who is playing.

## 5. SDK / domain / infrastructure separation

- **`sdk` (24 nodes)** is the smallest production layer and spans outward to `peer` (13),
  `report` (7), `strategy` (6) and `sim` (5). A thin object touching many layers is exactly
  the shape of a facade — it holds no logic of its own.
- **`infra` (84 nodes)** reaches `peer` (13), `report` (10), `shared` (10), `security` (10)
  and only `domain` (3). Infrastructure is wired to transport and reporting concerns, and
  is almost disconnected from game rules — the separation the guidelines ask for.
- **`shared`** hosts the cross-cutting utilities (config validation, gatekeeper, version)
  and is consumed by `peer`, `interop` and `infra` rather than consuming them.

## 6. Strategy modules

`strategy` is the largest production layer (362 nodes) and is organised around
`BrainBase` (degree 64) with `Observation`/`Action` as the interface contract. The
consumers are `sim` (229 edges), `peer` (21), `gui` (9), `sdk` (6), `interop` (3) — i.e.
the brains are called by the engine and measured by the harness, and nothing in `domain`
reaches back into them.

`advisor` (30 nodes) depends on `strategy` (22) and `domain` (12) but **nothing depends on
`advisor`** in the reverse direction from the core layers. Structurally it is an optional
plug-in, which matches its runtime behaviour: absent an API key it never activates.

## 7. MCP / interop path

`interop` (239 nodes) is the second-largest production layer and depends on `domain` (24),
package root (15), `shared` (6), `security` (6), `infra` (3) and `strategy` (3). The small
`strategy` coupling is the interesting part: the official wire path is almost entirely
independent of *which brain* is playing — it moves sealed moves and audits, not decisions.
`security` appearing here is the signing/auth path used for the commit-reveal exchange.

## 8. GUI and replay components

`gui` (162 nodes) depends outward on `domain` (15), `strategy` (9), `report` (6) and
`shared` (3).

**Nothing depends on `gui`** except the package root (16 edges — the CLI wiring). It is a
pure leaf in the dependency graph. This independently confirms, from the artefact rather
than from the commit message, the claim made when the GUI was added: it is a presentation
layer over existing state, and removing it could not affect gameplay. The graph also shows
`gui` reaching `report` (6) — the replay viewer reading recorded artifacts — while never
touching `peer` or `interop`, so it cannot participate in a live match.

## 9. What the graph does *not* show

Honest limits of this analysis:

- Extraction is **AST-only** (no LLM semantic pass), so edges are syntactic — imports,
  calls, definitions. Runtime-dynamic wiring (registry lookups by string, lazy imports) is
  under-represented. The lazy `AgentSDK` export in `__init__.py` is one such edge the graph
  cannot see.
- Degree measures *connectivity*, not importance or quality. `DevTestSigner`'s rank-9
  position is testing gravity, not architectural centrality.
- `docs` nodes (358) are part of the corpus, so document-to-document links inflate some
  community counts relative to a pure code graph.
- The graph is a snapshot of commit `efde472`; re-run `graphify update .` after any change.

## 10. Conclusion

The graph independently corroborates the architecture the written documentation claims:
a small dependency-free `domain` core, a large `strategy` layer built on a four-type shared
vocabulary, a thin `sdk` facade, an `interop` path decoupled from strategy choice, an
optional `advisor` plug-in, and a `gui` that is a strict leaf. The one structure the graph
reveals that the prose does not emphasise is how completely the codebase is organised
around `Board`, `Observation`, `Action` and `BeliefMap` — four types that between them
account for 575 of the 7,161 edges.
