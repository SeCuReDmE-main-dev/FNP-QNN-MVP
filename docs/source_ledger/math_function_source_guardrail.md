# Math Function Source Guardrail

This is the code-facing registry for mathematical functions currently available in the FNP-QNN simulator.

Canonical organization baseline:

`FNP-QNN-MVP-organisation/04_implementation_planning/MATH_SOURCE_FUNCTION_GUARDRAIL_BASELINE_2026-06-18.md`

Rule: after 2026-06-18, append only new source/function rows. Do not repeat the whole historical baseline in every future update.

Boundary: alpha-local educational research simulator only. No clinical, diagnostic, therapeutic, emergency, safety-critical, security, production, encryption, or validated physical quantum claim.

## Source URL Registry

| Source id | Source URL or local path | Evidence class |
| --- | --- | --- |
| `NQC` | `https://fs.unm.edu/NeutrosophicQuantumComputer.pdf` | Prof-thread primary source |
| `NLQC` | `https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf` | Prof-thread primary source |
| `IPW` | `https://fs.unm.edu/IPW/` | Prof-thread primary source |
| `IPW_39` | `https://fs.unm.edu/NSS/39Infinitesimally.pdf` | Prof-thread primary source |
| `IPW_6` | `https://fs.unm.edu/NSS/6InfinitesimallyPunctured.pdf` | Prof-thread primary source |
| `FPW` | `https://fs.unm.edu/IPW/IPW-to-FPW.pdf` | Prof-thread primary source |
| `NQT_2025` | `https://fs.unm.edu/NSS/1QuantumTheory.pdf` | Prof-thread primary source |
| `NIDUS_II` | `https://fs.unm.edu/NidusIdearum2-ed2.pdf` | Later FS PDF primary source |
| `PLITHOGENIC_2021` | `https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf` | Later FS PDF primary source |
| `REVOLUTIONARY_TOPOLOGIES` | `https://fs.unm.edu/TT/RevolutionaryTopologies.pdf` | Later FS PDF primary source |
| `PLITHOGENIC_PROB_STATS_2021` | `C:\Users\jeans\Desktop\livre pdf\PlithogenicProbabilityStatistics20.pdf` | Local FS PDF primary source |
| `NEUTROALGEBRA` | `https://fs.unm.edu/NA/NeutroAlgebra.pdf` | Later FS PDF primary source |
| `NEUTROSTRUCTURE` | `https://fs.unm.edu/NA/NeutroStructure.pdf` | Later FS PDF primary source |
| `FRACTAL_LOCAL` | `C:\Users\jeans\Desktop\livre pdf\Fractal_NeutroGeometry_Livre_V2_chapters_1_to_7.pdf` | Local manuscript source |
| `NODE734_LOCAL` | `C:\Users\jeans\Desktop\Docs\pdf\livre\complain of quantum node #734\Complain-of-Quantum-Node-734{{ final }} .pdf` | Local manuscript source |
| `LOCAL_RUNTIME` | Repository runtime contract | Local clean-room implementation source |

## Function Registry

| Function or class | File | Source ids | Endpoint/runtime surface | Test coverage |
| --- | --- | --- | --- | --- |
| `NeutrobitState` | `core/neutrosophic_quantum_primitives.py` | `NQC`, `NLQC` | `state_basis="neutrobit"` in `/qnn/smoke`, `/fnp-qnn/neurobit/gates/run` | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_cerebrum_qnn.py`, `tests/test_api_qnn_smoke.py` |
| `CoherentNeutroState`, `DecoherentNeutroState` | `core/neutrosophic_quantum_primitives.py` | `NLQC` | Non-projective measurement payloads | `tests/test_neutrosophic_quantum_primitives.py` |
| `neutrosophic_measurement()` | `core/neutrosophic_quantum_primitives.py` | `NQC`, `NLQC` | NeuroBit/QNN triplet metadata | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py` |
| `neutrosophic_gate_algebra()` | `core/neutrosophic_quantum_primitives.py` | `NQC`, `NLQC` | Pure bounded primitive for `not`, `and`, `or`, `if_then` | `tests/test_neutrosophic_quantum_primitives.py` |
| `punctured_wave_state()` | `core/neutrosophic_quantum_primitives.py` | `IPW`, `IPW_39`, `FPW` | Optional `puncture_delta` metadata | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py` |
| `punctured_surface_state()` | `core/neutrosophic_quantum_primitives.py` | `IPW`, `IPW_6`, `FPW` | NeuroBit surface metadata and QNN expansion support | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| `partial_entanglement_profile()` | `core/neutrosophic_quantum_primitives.py` | `NQT_2025` | NeuroBit/QNN local T/I/F metadata | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py` |
| `observer_effect_profile()` | `core/neutrosophic_quantum_primitives.py` | `NQT_2025` | Optional `observer_strength` in QNN/NeuroBit/runtime schemas | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_cerebrum_qnn.py` |
| `normalize_fractal_dimension()` | `core/neutrosophic_quantum_primitives.py` | `FRACTAL_LOCAL` | API aliases `D_f`, `D_min`, `D_max`; local `D_f_hat` carrier | `tests/test_neutrosophic_quantum_primitives.py` |
| `fractal_carrier_profile()` | `core/neutrosophic_quantum_primitives.py` | `FRACTAL_LOCAL`, `NODE734_LOCAL` | QNN, NeuroBit, LVFM, and plugin metadata: `D_f_hat`, `dF_carrier`, `i_fractal_candidate` | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| `neutrobit_features_from_vector()` | `core/neutrosophic_quantum_primitives.py` | Composite: `NQC`, `NLQC`, `FPW`, `NQT_2025`, `FRACTAL_LOCAL` | Optional QNN feature expansion | `tests/test_neutrosophic_quantum_primitives.py`, `tests/test_cerebrum_qnn.py` |
| `build_neurobit_gate_sequence()` | `core/neurobit_gate_tunnel.py` | `NQC` | `/fnp-qnn/neurobit/gates/run` | `tests/test_neurobit_gate_tunnel.py` |
| `gate_semantics()`, `reversibility_profile()` | `core/neurobit_gate_tunnel.py` | `NQC`, `NLQC` | NeuroBit gate trace metadata | `tests/test_neurobit_gate_tunnel.py` |
| `run_neurobit_gates()` | `core/neurobit_gate_tunnel.py` | Composite source-backed runtime | `/fnp-qnn/neurobit/gates/run`, `/commands/neurobit-gates` | `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| `run_neurobit_tunnel_demo()` | `core/neurobit_gate_tunnel.py` | Local simulator only | `/fnp-qnn/neurobit/tunnel/demo`, `/commands/neurobit-tunnel-demo` | `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| `build_neutrosophic_gate_sequence()` | `core/neurobit_gates.py` | `NQC` | Public NeuroBit gate primitive contract | `tests/test_neurobit_gates.py` |
| `to_torchquantum_ops()` | `core/neurobit_gates.py` | `LOCAL_RUNTIME` | Backend-neutral op descriptors | `tests/test_neurobit_gates.py` |
| `apply_gate_sequence_qiskit()` | `core/neurobit_gates.py` | `LOCAL_RUNTIME` | Optional Qiskit-compatible trace path | `tests/test_neurobit_gates.py` |
| `complex_wavefunction_to_amplitude_phase_features()` | `core/quantum_feature_transforms.py` | `LOCAL_RUNTIME` | Pure feature transform | `tests/test_quantum_feature_transforms.py` |
| `structure_vector_to_phi_scaled_state()` | `core/quantum_feature_transforms.py` | `LOCAL_RUNTIME` | Phi-scaled local feature transform | `tests/test_quantum_feature_transforms.py` |
| `triplet_quality_profile()` | `core/nidus_idearum_math.py` | `NIDUS_II` | `/fnp-qnn/nidus/triplet/profile` | `tests/test_nidus_idearum_math.py`, `tests/test_api_qnn_smoke.py` |
| `source_weighted_triplet_fusion()` | `core/nidus_idearum_math.py` | `NIDUS_II` | `/fnp-qnn/nidus/fusion/profile` | `tests/test_nidus_idearum_math.py`, `tests/test_api_qnn_smoke.py` |
| `partial_membership_mean()` | `core/nidus_idearum_math.py` | `NIDUS_II` | `/fnp-qnn/nidus/partial-membership/mean` | `tests/test_nidus_idearum_math.py`, `tests/test_api_qnn_smoke.py` |
| `plithogenic_attribute_profile()` | `core/plithogenic_logic.py` | `PLITHOGENIC_2021` | Runtime attribute profile under `plithogenic_enabled=true` | `tests/test_plithogenic_logic.py`, `tests/test_cerebrum_runtime_bridge.py` |
| `plithogenic_contradiction_degree()` | `core/plithogenic_logic.py` | `PLITHOGENIC_2021` | Pair dependence/contradiction metadata | `tests/test_plithogenic_logic.py` |
| `plithogenic_neutrosophic_conjunction()` | `core/plithogenic_logic.py` | `PLITHOGENIC_2021` | Cumulative truth: `min(T), max(I), max(F)` | `tests/test_plithogenic_logic.py` |
| `plithogenic_weighted_cumulative_truth()` | `core/plithogenic_logic.py` | `PLITHOGENIC_2021` | Weighted cumulative runtime readout | `tests/test_plithogenic_logic.py` |
| `plithogenic_runtime_fusion_profile()` | `core/plithogenic_logic.py` | `PLITHOGENIC_2021` | `POST /fnp-qnn/plithogenic/runtime/profile`, `RuntimeRunRequest.plithogenic_enabled`, LVFM/QNN opt-in metadata | `tests/test_plithogenic_logic.py`, `tests/test_cerebrum_runtime_bridge.py` |
| `topological_axiom_profile()` | `core/revolutionary_topologies.py` | `REVOLUTIONARY_TOPOLOGIES` | CT/NCT/ACT-style closure profile for topology-like runtime sets | `tests/test_revolutionary_topologies.py` |
| `deformation_invariant_signature()` | `core/revolutionary_topologies.py` | `REVOLUTIONARY_TOPOLOGIES` | Graph invariant metadata for selected structure under deformation | `tests/test_revolutionary_topologies.py` |
| `nonstandard_neighborhood_profile()` | `core/revolutionary_topologies.py` | `REVOLUTIONARY_TOPOLOGIES` | Left/right/binad local neighborhood tolerance | `tests/test_revolutionary_topologies.py` |
| `refined_topology_components()` | `core/revolutionary_topologies.py` | `REVOLUTIONARY_TOPOLOGIES` | Refined `T/I/F` topology components preserving `I -> I_system^S -> D_f -> dF -> i_fractal` | `tests/test_revolutionary_topologies.py` |
| `revolutionary_topology_runtime_profile()` | `core/revolutionary_topologies.py` | `REVOLUTIONARY_TOPOLOGIES` | `POST /fnp-qnn/revolutionary-topology/runtime/profile`, `RuntimeRunRequest.revolutionary_topology_enabled`, LVFM/QNN opt-in metadata | `tests/test_revolutionary_topologies.py`, `tests/test_cerebrum_runtime_bridge.py` |
| `plithogenic_variate_sample_profile()`, `plithogenic_probability_family_profile()`, `refined_plithogenic_statistical_components()`, `plithogenic_multi_to_uni_decision()` | `core/plithogenic_probability_statistics.py` | `PLITHOGENIC_PROB_STATS_2021`, `PLITHOGENIC_2021`, `REVOLUTIONARY_TOPOLOGIES` | Pure empirical probability/statistics primitives for plithogenic-to-topology wiring | `tests/test_plithogenic_probability_statistics.py` |
| `plithogenic_topology_wiring_profile()` | `core/plithogenic_probability_statistics.py` | `PLITHOGENIC_PROB_STATS_2021`, `PLITHOGENIC_2021`, `REVOLUTIONARY_TOPOLOGIES` | `POST /fnp-qnn/plithogenic-topology/runtime/profile`; automatic LVFM/QNN opt-in metadata when `plithogenic_enabled=true` and `revolutionary_topology_enabled=true` | `tests/test_plithogenic_probability_statistics.py`, `tests/test_cerebrum_runtime_bridge.py` |
| `plithogenic_topology_load_profile()`, `plugin_stabilization_profile()` | `core/plithogenic_probability_statistics.py` | `PLITHOGENIC_PROB_STATS_2021`, `LOCAL_RUNTIME`, `NODE734_LOCAL`, `FRACTAL_LOCAL` | Optional plugin-stabilized derived metadata when `plithogenic_enabled=true`, `revolutionary_topology_enabled=true`, and `plugin_hook_enabled=true`; no offload or raw evidence overwrite | `tests/test_plithogenic_probability_statistics.py`, `tests/test_cerebrum_runtime_bridge.py` |
| `tri_section_space_profile()`, `neutro_function_profile()`, `neutro_operation_table_profile()`, `neutro_axiom_profile()`, `neutroalgebra_structure_profile()` | `core/neutro_algebra.py` | `NEUTROALGEBRA` | Pure algebraic-integrity primitives for A/neutroA/antiA regions, function validity, operation validity, sampled axioms, and structure classification | `tests/test_neutro_algebra.py` |
| `neutro_relation_profile()`, `neutro_attribute_profile()`, `neutrostructure_profile()`, `runtime_neutrostructure_profile()` | `core/neutro_structure.py` | `NEUTROSTRUCTURE`, `NEUTROALGEBRA`, `LOCAL_RUNTIME` | System structural metrics `T_system/I_system/F_system` from relations and attributes; attached under `structure_system_profile` when `neutro_algebra_enabled=true` | `tests/test_neutro_structure.py`, `tests/test_cerebrum_runtime_bridge.py` |
| `neutroalgebra_runtime_profile()` | `core/neutro_algebra.py` | `NEUTROALGEBRA`, `NEUTROSTRUCTURE`, `LOCAL_RUNTIME`, `PLITHOGENIC_2021`, `REVOLUTIONARY_TOPOLOGIES` | `POST /fnp-qnn/neutro-algebra/profile`; optional runtime/LVFM/QNN metadata when `neutro_algebra_enabled=true`; annotates plithogenic-topology runtime integrity and structural system metrics without overwriting raw evidence | `tests/test_neutro_algebra.py`, `tests/test_neutro_structure.py`, `tests/test_cerebrum_runtime_bridge.py` |
| `CerebrumRuntimeBridge.ingest()` | `core/cerebrum_runtime_bridge.py` | `LOCAL_RUNTIME` | `/cerebrum/runtime/ingest`, `/cerebrum/runtime/pairs` | `tests/test_cerebrum_runtime_bridge.py` |
| `CerebrumRuntimeBridge.build_state()` | `core/cerebrum_runtime_bridge.py` | `LOCAL_RUNTIME`, `FRACTAL_LOCAL`, `PLITHOGENIC_2021`, `REVOLUTIONARY_TOPOLOGIES`, `NEUTROALGEBRA`, `NEUTROSTRUCTURE` | Runtime event, pair, LVFM, QNN, plugin, plithogenic, topology, plithogenic-topology, NeutroAlgebra, and NeutroStructure integration point | `tests/test_cerebrum_runtime_bridge.py` |
| `LVFMRuntimeGraph` | `core/lvfm_runtime_graph.py` | `LOCAL_RUNTIME` | Runtime LVFM snapshot with T/dF/F register bits | `tests/test_lvfm_runtime_graph.py` |
| `FfeDPluginBridge.run_mvp5()` | `core/ffed_plugin_bridge.py` | `NODE734_LOCAL`, `FRACTAL_LOCAL`, local pluginpack when available | Optional `plugin_hook_enabled`; maps plugin signals into local carrier metadata | `tests/test_ffed_plugin_bridge.py`, `tests/test_neurobit_gate_tunnel.py`, `tests/test_api_qnn_smoke.py` |
| `build_plugin_payload_from_results()` | `core/ffed_plugin_bridge.py` | `NODE734_LOCAL`, `FRACTAL_LOCAL` | Plugin trace payload and impact verification | `tests/test_ffed_plugin_bridge.py` |
| `CPAIMeshState`, `cpai_mesh_profile()` | `core/cpai_mesh.py` | `LOCAL_RUNTIME` | Optional `cpai_context`, routing decision, Datadog metric contract | `tests/test_cpai_mesh.py`, `tests/test_ffed_plugin_bridge.py`, `tests/test_api_qnn_smoke.py` |

## Guardrail

- New source-backed math must add a new row here.
- New public endpoints must reference the row that justifies them.
- New tests must be listed next to the function or endpoint they protect.
- Source claims must stay educational and bounded.
- `D_f_hat`, `dF`, and `i_fractal_candidate` must not be collapsed into generic `I`.
- Preserve `I -> I_system^S -> D_f -> dF -> i_fractal`.
- The README may point here instead of duplicating this full table.
