# Math Source Function Guardrail Baseline

Date: 2026-06-18

Purpose: establish the complete baseline of mathematical sources currently implanted in the FNP-QNN simulator. After this document, future updates should not repeat the whole history. They should only append newly added sources, functions, endpoints, and tests.

Boundary: alpha-local educational research simulator. Not clinical, diagnostic, therapeutic, emergency, safety-critical, security, production-public, or validated physical quantum behavior.

## Coordination Context

The latest professor-facing thread reviewed on 2026-06-18 confirms the project transition: book/manuscript support is being closed down, and the active work moves to the simulator, the mathematical engine, runtime evidence, interface, tests, and funding preparation.

This guardrail is the reference point for declaring that another project uses these mathematical sources heavily. It lists the currently implemented simulator math and the source relationship for each function.

## Guardrail Rule From This Baseline Forward

- This document is the full baseline.
- Future source work must be append-only in a dated section or a new companion report.
- Future summaries should list only new functions and new source URLs after 2026-06-18.
- Do not re-claim earlier sources as newly implemented.
- Do not collapse `I -> I_system^S -> D_f -> dF -> i_fractal`.
- Do not promote local simulation metadata into clinical, security, production, or physical validation claims.

## Source-To-Function Baseline

| Source | URL or local reference | Implemented simulator functions | Public-safe simulator meaning |
| --- | --- | --- | --- |
| Neutrosophic Quantum Computer | https://fs.unm.edu/NeutrosophicQuantumComputer.pdf | `NeutrobitState`, `NeutrobitState.from_tif()`, `neutrosophic_measurement()`, `neutrosophic_gate_algebra()`, NeuroBit `W` gate marker | Deterministic neutrobit-style grammar over `|0>`, `|1>`, and local `|I>` for education. |
| Neutrosophic Logic Based Quantum Computing | https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf | `CoherentNeutroState`, `DecoherentNeutroState`, `neutrosophic_measurement()`, `neutrosophic_gate_algebra()` | Triplet measurement and logic previews without binary collapse. |
| Infinitesimally Punctured Wave articles | https://fs.unm.edu/IPW/ and https://fs.unm.edu/NSS/39Infinitesimally.pdf and https://fs.unm.edu/NSS/6InfinitesimallyPunctured.pdf | `punctured_wave_state()`, `punctured_surface_state()` | Finite local puncture-grid analogies for wave and surface simulation. |
| From IPW to FPW | https://fs.unm.edu/IPW/IPW-to-FPW.pdf | API `puncture_delta`, `punctured_wave_state()`, `punctured_surface_state()`, QNN optional feature expansion | Finite positive `delta` as a reproducible local simulation parameter. |
| Neutrosophic Quantum Theory: Partial Entanglement, Partial Effect of the Observer, and Teleportation | https://fs.unm.edu/NSS/1QuantumTheory.pdf | `partial_entanglement_profile()`, `observer_effect_profile()` | Bounded T/I/F metadata for partial correlation, separability, decoherence, and observer strength. |
| Local Fractal NeutroGeometry source | `C:\Users\jeans\Desktop\livre pdf\Fractal_NeutroGeometry_Livre_V2_chapters_1_to_7.pdf` | `normalize_fractal_dimension()`, `fractal_carrier_profile()`, API aliases `D_f`, `D_min`, `D_max` | `D_f_hat = (D_f - D_min) / (D_max - D_min)` as a bounded local carrier; not identical to global `I`. |
| Local Complain of Quantum Node #734 source | `C:\Users\jeans\Desktop\Docs\pdf\livre\complain of quantum node #734\Complain-of-Quantum-Node-734{{ final }} .pdf` | `fractal_carrier_profile()` wording and local baton/FfeD interpretation | Public-safe local carrier framing only. |
| Nidus Idearum II | https://fs.unm.edu/NidusIdearum2-ed2.pdf | `triplet_quality_profile()`, `source_weighted_triplet_fusion()`, `partial_membership_mean()` | Dynamic T/I/F quality, source-weighted incomplete-model fusion, and partial membership means. |
| Introduction to Plithogenic Logic as generalization of MultiVariate Logic | https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf | `plithogenic_attribute_profile()`, `plithogenic_contradiction_degree()`, `plithogenic_neutrosophic_conjunction()`, `plithogenic_weighted_cumulative_truth()`, `plithogenic_runtime_fusion_profile()` | Runtime multi-attribute event truth, weights, dependence/contradiction metadata, and cumulative truth. |
| Local FFeD MVP5 plugin bridge | Local pluginpack path, when available: `C:\Users\jeans\Desktop\pluginpack` | `FfeDPluginBridge.run_mvp5()`, `build_plugin_payload_from_results()`, `numeric_series_from_events()`, `consensus_items_from_events()` | Optional allowlisted local plugin signals mapped into `D_f`, `D_f_hat`, `dF`, `i_fractal_candidate`, and gate metadata. |
| Cerebrum runtime bridge | Local runtime clean-room contract in `core/cerebrum_runtime_bridge.py` | `CerebrumRuntimeBridge.ingest()`, `build_pairs()`, `build_state()`, LVFM snapshot construction | Converts interval memory events into observations, pairs, LVFM state, and QNN-ready features. |
| Amplitude/phase feature transforms | Local MVP transfer source in repository transfer plan | `complex_wavefunction_to_amplitude_phase_features()`, `structure_vector_to_phi_scaled_state()` | Pure deterministic feature transforms for the local QNN candidate lane. |

## Current API Surfaces

- `POST /qnn/smoke`
- `POST /cerebrum/runtime/run`
- `POST /cerebrum/runtime/ingest`
- `POST /cerebrum/runtime/pairs`
- `POST /fnp-qnn/neurobit/gates/run`
- `POST /fnp-qnn/neurobit/tunnel/demo`
- `GET /fnp-qnn/nidus/status`
- `POST /fnp-qnn/nidus/triplet/profile`
- `POST /fnp-qnn/nidus/fusion/profile`
- `POST /fnp-qnn/nidus/partial-membership/mean`
- `POST /fnp-qnn/plithogenic/runtime/profile`

## Function Families

### Neutrobit And Neutrosophic Logic

- File: `core/neutrosophic_quantum_primitives.py`
- Core functions: `NeutrobitState`, `CoherentNeutroState`, `DecoherentNeutroState`, `neutrosophic_measurement()`, `neutrosophic_gate_algebra()`, `neutrobit_features_from_vector()`.
- Guardrail: these are deterministic simulation grammar, not physical quantum execution.

### NeuroBit Gate Runtime

- Files: `core/neurobit_gates.py`, `core/neurobit_gate_tunnel.py`
- Core functions: `build_neurobit_gate_sequence()`, `build_gate_parameters()`, `gate_matrix()`, `to_torchquantum_ops()`, `apply_gate_sequence_qiskit()`, `run_neurobit_gates()`, `run_neurobit_tunnel_demo()`.
- Guardrail: Qiskit and TorchQuantum remain optional/gated; tunnel demo is not encryption.

### Fractal Carrier

- File: `core/neutrosophic_quantum_primitives.py`
- Core functions: `normalize_fractal_dimension()`, `fractal_carrier_profile()`.
- Guardrail: `D_f_hat` is a local admissible carrier and can be `i_fractal_candidate`; it is not full indeterminacy.

### FPW/IPW Puncture Simulation

- File: `core/neutrosophic_quantum_primitives.py`
- Core functions: `punctured_wave_state()`, `punctured_surface_state()`.
- Guardrail: finite positive `delta` only; no infinitesimal or physical proof claim.

### Partial Entanglement And Observer Effect

- File: `core/neutrosophic_quantum_primitives.py`
- Core functions: `partial_entanglement_profile()`, `observer_effect_profile()`.
- Guardrail: bounded local T/I/F metadata only.

### Nidus Idearum II Layer

- File: `core/nidus_idearum_math.py`
- Core functions: `triplet_quality_profile()`, `source_weighted_triplet_fusion()`, `partial_membership_mean()`.
- Guardrail: Nidus endpoints are opt-in and do not change default QNN, NeuroBit, or runtime behavior.

### Plithogenic Runtime Fusion

- File: `core/plithogenic_logic.py`
- Core functions: `plithogenic_attribute_profile()`, `plithogenic_contradiction_degree()`, `plithogenic_neutrosophic_conjunction()`, `plithogenic_weighted_cumulative_truth()`, `plithogenic_runtime_fusion_profile()`.
- Guardrail: opt-in with `plithogenic_enabled=true`; default runtime remains unchanged.

### FFeD MVP5 Plugin Hook

- File: `core/ffed_plugin_bridge.py`
- Core functions: `FfeDPluginBridge.run_mvp5()`, `build_plugin_payload_from_results()`.
- Guardrail: optional local allowlist only; no arbitrary plugin execution, no secret exposure, no runtime dependency when absent.

## Validation Baseline

Latest validation after Plithogenic implantation:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Result: 117 tests passed.

```powershell
.\.venv\Scripts\python.exe scripts\validate_alpha_readiness.py
```

Result: alpha-local readiness gate passed.

## Nota Bene

The current README is intentionally acting as a maintainer trace marker during pre-alpha. It is not yet the final public-facing README. Before soft launch / alpha, the README should be reduced and reorganized into a cleaner user-facing document, while this guardrail remains the source-to-function registry.
