# Architecture from the graph (Game-P2P-Cop-Chase-Thief)

## Nodes per layer

| Layer | Nodes |
| --- | ---: |
| `tests` | 1110 |
| `strategy` | 362 |
| `docs` | 358 |
| `interop` | 239 |
| `schemas` | 180 |
| `sim` | 170 |
| `gui` | 162 |
| `other` | 117 |
| `peer` | 91 |
| `infra` | 84 |
| `domain` | 69 |
| `(package root)` | 64 |
| `report` | 55 |
| `shared` | 45 |
| `scripts` | 43 |
| `advisor` | 30 |
| `security` | 28 |
| `sdk` | 24 |

## Cross-layer dependencies (edges)

| From | To | Edges |
| --- | --- | ---: |
| `tests` | `strategy` | 325 |
| `tests` | `interop` | 305 |
| `sim` | `strategy` | 229 |
| `strategy` | `domain` | 160 |
| `tests` | `domain` | 144 |
| `tests` | `shared` | 108 |
| `tests` | `peer` | 98 |
| `tests` | `(package root)` | 89 |
| `tests` | `security` | 81 |
| `tests` | `report` | 78 |
| `tests` | `gui` | 67 |
| `sim` | `domain` | 58 |
| `tests` | `sim` | 54 |
| `peer` | `domain` | 50 |
| `tests` | `infra` | 43 |
| `peer` | `(package root)` | 32 |
| `interop` | `domain` | 24 |
| `advisor` | `strategy` | 22 |
| `peer` | `strategy` | 21 |
| `(package root)` | `shared` | 20 |
| `tests` | `sdk` | 20 |
| `(package root)` | `infra` | 17 |
| `tests` | `advisor` | 17 |
| `scripts` | `sim` | 16 |
| `(package root)` | `gui` | 16 |
