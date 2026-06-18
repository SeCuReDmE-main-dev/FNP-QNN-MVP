# Math Function Source Guardrail

This document is the code-facing registry for mathematical functions currently available in the FNP-QNN simulator. It mirrors the organization baseline:

`FNP-QNN-MVP-organisation/04_implementation_planning/MATH_SOURCE_FUNCTION_GUARDRAIL_BASELINE_2026-06-18.md`

After 2026-06-18, add only new source/function rows instead of repeating the whole baseline.

## Current Function Registry

| Function or class | File | Source relation | URL or source reference |
| --- | --- | --- | --- |
| `NeutrobitState` | `core/neutrosophic_quantum_primitives.py` | Local `|0>`, `|1>`, `|I>` simulation basis | https://fs.unm.edu/NeutrosophicQuantumComputer.pdf |
| `CoherentNeutroState`, `DecoherentNeutroState` | `core/neutrosophic_quantum_primitives.py` | Coherent/decoherent neutrosophic state wrappers | https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf |
| `neutrosophic_measurement()` | `core/neutrosophic_quantum_primitives.py` | Non-projective T/I/F-style measurement | https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf |
| `neutrosophic_gate_algebra()` | `core/neutrosophic_quantum_primitives.py` | Bounded neutrosophic `not`, `and`, `or`, `if_then` previews | https://fs.unm.edu/NeutrosophicQuantumComputer.pdf |
| `punctured_wave_state()` | `core/neutrosophic_quantum_primitives.py` | Finite puncture sequence for wave-like simulation | https://fs.unm.edu/IPW/ |
| `punctured_surface_state()` | `core/neutrosophic_quantum_primitives.py` | Finite puncture grid for surface-like simulation | https://fs.unm.edu/IPW/IPW-to-FPW.pdf |
| `partial_entanglement_profile()` | `core/neutrosophic_quantum_primitives.py` | Partial entanglement/separability/decoherence T/I/F metadata | https://fs.unm.edu/NSS/1QuantumTheory.pdf |
| `observer_effect_profile()` | `core/neutrosophic_quantum_primitives.py` | Partial observer effect T/I/F metadata | https://fs.unm.edu/NSS/1QuantumTheory.pdf |
| `normalize_fractal_dimension()` | `core/neutrosophic_quantum_primitives.py` | `D_f_hat = (D_f - D_min) / (D_max - D_min)` | Local Fractal NeutroGeometry manuscript source |
| `fractal_carrier_profile()` | `core/neutrosophic_quantum_primitives.py` | Local admissible `D_f_hat`, `dF`, `i_fractal_candidate` carrier | Local Fractal NeutroGeometry manuscript source |
| `neutrobit_features_from_vector()` | `core/neutrosophic_quantum_primitives.py` | Optional QNN feature expansion using neutrobit/puncture/observer/fractal metadata | Source-backed composite |
| `build_neurobit_gate_sequence()` | `core/neurobit_gate_tunnel.py` | Deterministic NeuroBit gate schedule with `W` as local `|I>` marker | https://fs.unm.edu/NeutrosophicQuantumComputer.pdf |
| `run_neurobit_gates()` | `core/neurobit_gate_tunnel.py` | NeuroBit gate trace, measurement, entanglement, observer, puncture, and carrier payload | Source-backed composite |
| `run_neurobit_tunnel_demo()` | `core/neurobit_gate_tunnel.py` | Deterministic tunnel-noise demo | Local simulator only; not encryption |
| `to_torchquantum_ops()` | `core/neurobit_gates.py` | Backend-neutral operation descriptors | Local MVP transfer contract |
| `apply_gate_sequence_qiskit()` | `core/neurobit_gates.py` | Optional Qiskit-compatible trace path | Local MVP transfer contract |
| `complex_wavefunction_to_amplitude_phase_features()` | `core/quantum_feature_transforms.py` | Amplitude/phase feature encoding | Local MVP transfer contract |
| `structure_vector_to_phi_scaled_state()` | `core/quantum_feature_transforms.py` | Phi-scaled complex state encoding | Local MVP transfer contract |
| `triplet_quality_profile()` | `core/nidus_idearum_math.py` | Dynamic T/I/F quality metadata | https://fs.unm.edu/NidusIdearum2-ed2.pdf |
| `source_weighted_triplet_fusion()` | `core/nidus_idearum_math.py` | Source-weighted fusion preserving incomplete/intersection uncertainty | https://fs.unm.edu/NidusIdearum2-ed2.pdf |
| `partial_membership_mean()` | `core/nidus_idearum_math.py` | Partial membership mean with under/equal/over membership | https://fs.unm.edu/NidusIdearum2-ed2.pdf |
| `plithogenic_attribute_profile()` | `core/plithogenic_logic.py` | Runtime `P(V1, V2, ..., Vn)` attribute profile | https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf |
| `plithogenic_contradiction_degree()` | `core/plithogenic_logic.py` | Bounded local dependence/contradiction metric | https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf |
| `plithogenic_neutrosophic_conjunction()` | `core/plithogenic_logic.py` | Cumulative truth by `min(T), max(I), max(F)` | https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf |
| `plithogenic_weighted_cumulative_truth()` | `core/plithogenic_logic.py` | Weight-sensitive cumulative truth readout | https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf |
| `plithogenic_runtime_fusion_profile()` | `core/plithogenic_logic.py` | Opt-in runtime event fusion profile before LVFM/QNN features | https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf |
| `FfeDPluginBridge.run_mvp5()` | `core/ffed_plugin_bridge.py` | Optional allowlisted plugin feature bridge into `D_f/D_f_hat/dF/i_fractal_candidate` | Local pluginpack path when available |
| `CerebrumRuntimeBridge.build_state()` | `core/cerebrum_runtime_bridge.py` | Runtime event, pair, LVFM, QNN, plugin, and plithogenic integration point | Local clean-room runtime contract |

## Guardrail

- New source-backed math must add a new row here.
- New public endpoints must reference the row that justifies them.
- Source claims must stay educational and bounded.
- `D_f_hat` and `dF` must not be collapsed into generic `I`.
- The README may point here instead of duplicating this full table.
