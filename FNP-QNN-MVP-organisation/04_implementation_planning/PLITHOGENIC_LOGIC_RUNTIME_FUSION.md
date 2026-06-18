# Plithogenic Logic Runtime Fusion Implantation

Source: Florentin Smarandache, *Introduction to Plithogenic Logic as generalization of MultiVariate Logic*, Neutrosophic Sets and Systems, Vol. 45, 2021. URL: https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf

Boundary: this is an alpha-local educational simulation layer. It is not clinical, diagnostic, therapeutic, security, production-public, or validated physical behavior.

## Simulator Lacuna Fixed

The correct entry point is the Cerebrum runtime bridge, not a standalone theory endpoint. Before this layer, `CerebrumRuntimeBridge` could normalize interval events, create crossmodal overlap pairs, produce LVFM snapshots, and feed QNN features. The missing part was explicit handling of attribute-value contradiction and dependence before LVFM/QNN feature encoding.

The plithogenic layer fixes that gap by computing an opt-in runtime profile from the same events and pairs that already drive the simulator. Default behavior remains unchanged unless `plithogenic_enabled=true`.

## Five Mathematical Concepts Extracted

1. Multi-attribute proposition `P(V1, V2, ..., Vn)`
   - PDF evidence: page 1 defines a plithogenic proposition as characterized by many truth-values with respect to many attribute-values or random variables, denoted `P(V1, V2, ..., Vn)`.
   - Simulator mapping: runtime events become attribute-value observations `V1...Vn`.

2. Attribute truth degrees
   - PDF evidence: page 1 defines `P(Vj)=tj`; page 2 extends this to fuzzy, intuitionistic fuzzy, indeterminate, and neutrosophic forms.
   - Simulator mapping: each event receives bounded `T`, local `I_system_component`, and `F` while preserving `I -> I_system^S -> D_f -> dF -> i_fractal`.

3. Weights of truth variables
   - PDF evidence: page 3 states that some truth variables may weigh more than others.
   - Simulator mapping: event duration and existing event weights become normalized source/attribute weights for weighted cumulative truth.

4. Dependence and contradiction between variables
   - PDF evidence: page 1 says independence/dependence degrees determine the conjunctive operator; page 5 identifies future aggregation with dependence degree `dij in [0,1]`.
   - Simulator mapping: pair overlap is treated as local dependence, and divergent attribute truth-values create a bounded contradiction load. This is a simulator metric, not a claimed universal plithogenic operator.

5. Cumulative plithogenic truth
   - PDF evidence: page 1 says cumulative truth is computed; page 5 gives the neutrosophic conjunction as `min(T), max(I), max(F)`.
   - Simulator mapping: the runtime profile reports both source-direct neutrosophic cumulative truth and weighted cumulative truth.

## Exact Runtime Mapping

- `core/plithogenic_logic.py`
  - `plithogenic_attribute_profile(events)` maps events into `P(V1...Vn)` attributes.
  - `plithogenic_contradiction_degree(left, right, overlap_score)` computes local dependence/contradiction metadata.
  - `plithogenic_neutrosophic_conjunction(profiles)` computes `min(T), max(I), max(F)`.
  - `plithogenic_weighted_cumulative_truth(profiles)` computes a weight-sensitive readout.
  - `plithogenic_runtime_fusion_profile(events, pairs)` returns the runtime fusion profile and bounded feature vector.

- `core/cerebrum_runtime_bridge.py`
  - `build_state(..., plithogenic_enabled=False)` preserves the old path by default.
  - When enabled, it appends the plithogenic feature vector to the runtime feature vector, attaches `plithogenic` to the state payload, and stores a compact trace under `lvfm.plithogenic_fusion_profile`.

- API
  - `RuntimeRunRequest.plithogenic_enabled` enables the runtime integration.
  - `POST /fnp-qnn/plithogenic/runtime/profile` returns the same profile without running the full QNN path.

## Forbidden Claims

- Do not claim this implements the full plithogenic aggregation theory.
- Do not claim physical, clinical, diagnostic, therapeutic, emergency, safety-critical, production, or security behavior.
- Do not claim contradiction/dependence is solved; the simulator only surfaces a bounded local metric.
- Do not collapse `dF` into generic `I`.
- Do not replace existing QNN, NeuroBit, Nidus, or LVFM semantics by default.

## Validation

Required validation commands:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\.venv\Scripts\python.exe scripts\validate_alpha_readiness.py
```
