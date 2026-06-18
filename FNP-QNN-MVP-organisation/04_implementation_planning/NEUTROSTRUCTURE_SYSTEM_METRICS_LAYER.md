# NeutroStructure System Metrics Layer

Date: 2026-06-18

Source: Florentin Smarandache, *Structure, NeutroStructure, and AntiStructure in Science*.

URL: https://fs.unm.edu/NA/NeutroStructure.pdf

## Simulator Lacuna Fixed

The previous NeutroAlgebra layer inspected operations and sampled axioms, but
it did not yet convert those algebraic results into a system-level structural
readout. This layer fills that gap by computing `T_system`, `I_system`, and
`F_system` from relations and attributes, matching the source definition that a
structure is a non-empty space characterized by relations and attributes.

## Source Evidence

- Pages 1-2: the source defines the neutrosophic triplet `<A, neutA, antiA>`
  and states that `T/I/F` may apply to concepts beyond mathematics.
- Page 1 and page 3: operations/functions can be well-defined,
  indeterminate/undefined, or outer-defined.
- Page 4: a classical structure is a space with relations and attributes;
  relation and attribute each have classical, neutro, and anti forms.
- Page 5: a NeutroStructure has at least one NeutroRelation or
  NeutroAttribute and no AntiRelation nor AntiAttribute; an AntiStructure has
  at least one AntiRelation or AntiAttribute.
- Page 5 conclusion: real structures are often neither perfect nor uniform, and
  elements do not all share relations and attributes in the same degree.

## Exact Code Binding

- `core/neutro_structure.py`
  - `neutro_relation_profile(elements, relation_checks)`
  - `neutro_attribute_profile(elements, attribute_checks)`
  - `neutrostructure_profile(space, relations, attributes)`
  - `runtime_neutrostructure_profile(events, pairs, neutro_algebra_profile, plithogenic_topology_profile)`

- `core/cerebrum_runtime_bridge.py`
  - Reuses `neutro_algebra_enabled=true`.
  - Adds `structure_system_profile` under `runtime.neutro_algebra`.
  - Adds `lvfm.neutro_structure_profile`.
  - Appends compact bounded NeutroStructure features to QNN input only on the
    existing NeutroAlgebra opt-in path.

- `core/qnn_nucleus.py`
  - Adds `qnn_result.neutro_structure_profile` when the runtime provides it.

## Runtime Mapping

- Space: runtime events represented as modality-index nodes.
- Relations: crossmodal pair relation, algebraic operation relation, and
  plithogenic-topology decision relation.
- Attributes: modality coverage, value stability, source completeness,
  temporal overlap quality, and algebraic integrity.
- Output: `T_system`, `I_system`, `F_system`, `system_classification`,
  relation profile, attribute profile, witnesses, and bounded feature vector.

## Boundaries

- `T_system/I_system/F_system` is a structural health/readiness readout for the
  local simulator, not clinical truth or production reliability.
- It is not a proof engine and does not validate physical quantum behavior.
- It does not overwrite NeutroAlgebra, plithogenic, topology, plugin, QNN,
  NeuroBit, LVFM, `D_f`, `dF`, or `i_fractal` evidence.
- It preserves `I -> I_system^S -> D_f -> dF -> i_fractal`; structural
  `I_system` is not generic `I`.

## Tests

- `tests/test_neutro_structure.py`
- `tests/test_cerebrum_runtime_bridge.py`

Covered behavior:

- Classical structure returns `T_system=1`, `I_system=0`, `F_system=0`.
- NeutroStructure appears with neutro relation/attribute evidence.
- AntiStructure appears with anti relation/attribute evidence.
- Runtime system metrics stay bounded.
- Runtime, LVFM, QNN, and endpoint surfaces expose the structural profile only
  when `neutro_algebra_enabled=true`.
