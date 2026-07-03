# Graph Theory Phase Log

## Scope
- Root: C:\Users\jeans\Desktop\Case study\modele\fnp-qnn\FNP-QNN-MVP-version-disease-simulator-\
- Requested focus: graph representation & T/I/dF trace behavior across repositories.

## Phase 1 — Repository Sweep
- Enumerated candidate projects: fnp-qnn, NeuUuR-o, simulateur de bacterie, ReaAaS-n, FFED-RNAeq.
- Searched for AGENTS.md under these paths; none found.
- Searched for graph/T/F/dF markers; found active graph implementations in:
  - fnp-qnn: `core/lvfm_runtime_graph.py`
  - simulateur de bacterie: `core/lvfm_runtime_graph.py`
  - NeuUuR-o: `src/research/field_representation.py`
  - ReaAaS-n: `tfd-logic.md` (design language), plus pipeline docs in `docs/`

## Phase 2 — Graph Modules Actually Used
- `fnp-qnn` and `simulateur de bacterie` share the same logical graph type:
  - `LVFMRuntimeGraph` with `register_node`, `add_edge`, `adjacency_matrix`, `compact_snapshot`, `weighted_trace`, `evaluate_gate`, `to_snapshot`.
  - `evaluate_gate` emits line with `T=...|I=...|dF=...|F=...|nodes=...|edges=...|verdict=...`.
- `NeuUuR-o` focuses on geometric/raster/point-cloud/graph output, not LVFM gate scoring:
  - `GraphField`, `build_graph_from_point_cloud` in `src/research/field_representation.py`.

## Phase 3 — T/I/dF Semantics Observed
- `fnp-qnn` and `simulateur de bacterie` currently map `RegisterBit.i_mass` directly from `d_f` (alias), i.e., `I` field is used as `dF` in outputs.
- `fnp-qnn` snapshot currently includes richer fields (`compact`, `exact_bits`, `register_keys`) than `simulateur` variant.
- ReaAaS-n documents a stricter conceptual model (`T + dF <= 1`) and routing/memory logic around dF as friction.

## Phase 4 — Action Recommendation
1) Keep graph engine aligned on all LVFM paths first (snapshot keys/shape parity).
2) Add a focused graph-theory evidence file in `docs/` for each active repo before changing runtime semantics.
3) Run tests for all discovered graph modules in one sweep before any launch-script changes.

## Test Plan (Next)
- `pytest tests/test_lvfm_runtime_graph.py` in both LVFM repos.
- `pytest tests/test_field_validation_steps_25_31.py` and graph-related docs checks in NeuUuR-o.
- Capture output logs with explicit labels and save in output folder for audit trace.