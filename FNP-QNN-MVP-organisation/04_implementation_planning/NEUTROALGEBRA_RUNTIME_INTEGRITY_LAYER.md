# NeutroAlgebra Runtime Integrity Layer

Date: 2026-06-18

Source: Florentin Smarandache, *NeutroAlgebra is a Generalization of Partial Algebra*.

URL: https://fs.unm.edu/NA/NeutroAlgebra.pdf

## Simulator Lacuna Fixed

The simulator already has runtime fusion, plithogenic probability/statistics,
topology profiles, plugin stabilization, LVFM snapshots, and QNN feature
construction. The missing layer was algebraic integrity: before a runtime
transformation, plugin output, topology merge, or QNN feature operation is
trusted as an ordinary operation, the simulator should know whether the
operation is inner-defined, undefined/indeterminate, outer-defined, or
axiom-breaking.

This source is therefore not another probability layer. It is an opt-in
integrity annotation layer.

## Five Source-Backed Concepts

1. Tri-sectioned space: the PDF defines the space split into `A`, `neutroA`,
   and `antiA` regions. The simulator maps observed elements into those three
   regions and returns bounded `T/I/F`.

2. NeutroFunction: the PDF distinguishes inner-defined, outer-defined,
   undefined/indeterminate, total function, partial function, neutrofunction,
   and antifunction cases. The simulator uses this to inspect feature
   transforms and plugin/runtime adapters.

3. NeutroOperation: the PDF applies the same true/indeterminate/false split to
   operations. The simulator inspects binary operation tables over runtime
   carriers and marks inner-defined, undefined, indeterminate, or outer-defined
   outputs.

4. NeutroAxiom: the PDF defines axioms that can be true for some elements,
   indeterminate for others, and false for others. The simulator samples
   closure, commutativity, associativity, idempotence, and identity-style laws
   and returns witness examples.

5. NeutroAlgebra structure: the PDF classifies algebra, neutroalgebra,
   antialgebra, and states that partial algebra is generalized by
   NeutroAlgebra. The simulator aggregates operation and axiom profiles into
   `classical_algebra`, `partial_algebra`, `neutroalgebra`,
   `hybrid_neutroalgebra`, or `antialgebra`.

## PDF Evidence Map

- Pages/topics around the opening definition: tri-sectioning into `<A>`,
  `<neutroA>`, and `<antiA>` with true, indeterminate, and false regions.
- Function section: inner-defined, outer-defined, and
  indeterminate/undefined mapping cases; NeutroFunction and AntiFunction.
- Operation section: NeutroOperation and AntiOperation definitions, including
  operation outputs that may be inside, outside, or indeterminate.
- Axiom section: Axiom, NeutroAxiom, and AntiAxiom classification.
- Algebra section: Algebra, NeutroAlgebra, AntiAlgebra, and the theorem that
  NeutroAlgebra generalizes Partial Algebra.
- Example section: division and Cayley-table examples showing partial,
  outer-defined, indeterminate, and NeutroAssociative behavior.

## Exact Code Binding

- `core/neutro_algebra.py`
  - `tri_section_space_profile(elements, classifier)`
  - `neutro_function_profile(domain, codomain, universe, mapping)`
  - `neutro_operation_table_profile(carrier, universe, operation_table)`
  - `neutro_axiom_profile(carrier, operation, axiom_name)`
  - `neutroalgebra_structure_profile(carrier, operations, axioms)`
  - `neutroalgebra_runtime_profile(events, pairs, plithogenic_topology_profile)`

- `core/cerebrum_runtime_bridge.py`
  - Adds `neutro_algebra_enabled: bool = False`.
  - Computes `neutro_algebra` after plithogenic/topology wiring when enabled.
  - Adds bounded NeutroAlgebra features to QNN input only when enabled.
  - Adds `lvfm.neutro_algebra_profile` only when enabled.

- `core/qnn_nucleus.py`
  - Accepts optional NeutroAlgebra features and attaches
    `neutro_algebra_profile` to the QNN result only when provided.

- `api/schemas.py`
  - Adds `RuntimeRunRequest.neutro_algebra_enabled`.

- `api/main.py`
  - Adds `POST /fnp-qnn/neutro-algebra/profile`.
  - Runtime `/cerebrum/runtime/run` can surface `runtime.neutro_algebra` when
    `neutro_algebra_enabled=true`.

## Runtime Mapping

- Carrier: observed runtime event modalities.
- Universe: carrier plus a bounded `outer_runtime_state` marker.
- Operation: observed crossmodal transition/fusion table from runtime pairs.
- Axioms: closure, commutativity, and associativity sampled over the carrier.
- Plithogenic-topology interaction: when the plithogenic-topology profile is
  present, it is passed as annotation context, but raw plithogenic and topology
  results are not overwritten.

## Tests

- `tests/test_neutro_algebra.py`
- `tests/test_cerebrum_runtime_bridge.py`

Covered behavior:

- Tri-section profile is exhaustive and bounded.
- NeutroFunction distinguishes total, partial, outer, and indeterminate cases.
- NeutroOperation detects inner, undefined, outer, and indeterminate outputs.
- NeutroAxiom can show true, false, and indeterminate associativity samples.
- Structure profile treats partial algebra as a NeutroAlgebra generalization.
- Runtime output remains unchanged unless `neutro_algebra_enabled=true`.
- Enabled runtime adds NeutroAlgebra metadata to runtime, LVFM, and QNN.
- Endpoint returns the same bounded profile shape.

## Forbidden Claims

- This is not a formal proof engine.
- This does not validate physical quantum execution.
- This does not prove clinical, diagnostic, therapeutic, security, safety, or
  production behavior.
- This does not overwrite plithogenic, topology, plugin, QNN, NeuroBit, or LVFM
  evidence.
- This does not collapse `I -> I_system^S -> D_f -> dF -> i_fractal`.

## Boundary

Alpha-local educational simulator metadata only. The layer is designed to make
runtime math provenance clearer and to prevent invalid transformations from
being silently normalized into binary valid/invalid outcomes.
