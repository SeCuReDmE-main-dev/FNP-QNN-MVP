# Quantum-Neutrosophic Source Ledger

This ledger maps Prof. Florentin Smarandache's quantum-neutrosophic sources to bounded simulator mechanisms. It is implementation guidance for an alpha-local educational research simulator.

Boundary: FNP-QNN does not claim to implement a physical neutrosophic quantum computer, clinical tool, security product, production system, or validated quantum physics engine. The code uses small, deterministic, source-attributed primitives as simulation grammar.

## Sources And Simulator Binding

| Source | Relevant concept | Simulator binding | Public-safe claim |
| --- | --- | --- | --- |
| [Neutrosophic Quantum Computer](https://fs.unm.edu/NeutrosophicQuantumComputer.pdf) | Theoretical neutrobit basis `0`, `1`, and `I`; refined indeterminacy; neutrosophic superposition; reversibility concerns. | `core/neutrosophic_quantum_primitives.py` models `NeutrobitState`; `neutrosophic_gate_algebra()` provides bounded `not`, `and`, `or`, and `if_then`; `core/neurobit_gate_tunnel.py` keeps `W` as the local `|I>` marker. | The simulator can demonstrate a deterministic neutrobit-style feature grammar and gate-algebra preview. |
| [Neutrosophic Logic Based Quantum Computing](https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf) | Coherent versus decoherent neutrosophic states; non-projective measurement returning a distribution over `|0>`, `|1>`, `|I>`; neutrosophic logic operators. | `CoherentNeutroState`, `DecoherentNeutroState`, `neutrosophic_measurement()`, and `neutrosophic_gate_algebra()` return triplet distributions instead of forcing binary collapse. | The simulator can expose T/I/F-style measurement and logic previews for educational inspection. |
| [Infinitesimally Punctured Wave program](https://fs.unm.edu/IPW/) and related short articles: [IPW](https://fs.unm.edu/NSS/39Infinitesimally.pdf), [comparison](https://fs.unm.edu/NSS/6InfinitesimallyPunctured.pdf) | Discrete-continuous bridge: a wave/surface/space can be represented as ordered punctures/sub-particles. | `punctured_wave_state()` creates a deterministic ordered puncture state; `punctured_surface_state()` extends this to finite 2D grids. | The simulator can show finite puncture-grid analogies for wave-like and surface-like states. |
| [From IPW to FPW](https://fs.unm.edu/IPW/IPW-to-FPW.pdf) | FPW replaces virtual infinitesimal spacing with practical finite `delta > 0`. | API fields accept optional `puncture_delta`; NeuroBit can emit finite wave and surface metadata; QNN feature expansion can append finite puncture metadata. | The simulator can use finite spacing as a reproducible local simulation parameter. |
| [Neutrosophic Quantum Theory: Partial Entanglement, Partial Effect of the Observer, and Teleportation](https://fs.unm.edu/NSS/1QuantumTheory.pdf) | T/I/F describes partial entanglement, separability/failure, decoherence/noise, and partial observer effect. | `partial_entanglement_profile()` maps correlation, separability, decoherence, and `dF`; `observer_effect_profile()` maps observer strength into bounded T/I/F metadata. | The simulator can inspect partial-correlation and partial-observer scenarios without binary overclaiming. |
| [Nidus Idearum. Scilogs, II: de rerum consectatione, 2nd ed.](https://fs.unm.edu/NidusIdearum2-ed2.pdf) | Dynamic T/I/F triplets; source importance; incomplete or indeterminate models; SuperHyperAlgebra; indeterminate sample size; partial membership means. | `core/nidus_idearum_math.py` adds `triplet_quality_profile()`, `source_weighted_triplet_fusion()`, and `partial_membership_mean()` behind opt-in `/fnp-qnn/nidus/*` endpoints. | The simulator can expose source-attributed local triplet quality, incomplete-model fusion, and partial-membership sample readouts for educational inspection. |
| [Introduction to Plithogenic Logic as generalization of MultiVariate Logic](https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf) | Plithogenic proposition `P(V1...Vn)`; truth-values by attribute/random variable; variable weights; indeterminate values; cumulative neutrosophic truth by `min(T), max(I), max(F)`; dependence degree for future aggregation. | `core/plithogenic_logic.py` adds opt-in runtime fusion profiles for attribute truth triplets, weights, pair dependence/contradiction, cumulative truth, and QNN feature additions when `plithogenic_enabled=true`. | The simulator can expose bounded local plithogenic runtime-fusion metadata for education without changing default runtime behavior. |
| Local source: `C:\Users\jeans\Desktop\Docs\pdf\livre\complain of quantum node #734\Complain-of-Quantum-Node-734{{ final }} .pdf` | Narrative source for the deterministic baton/FfeD framing and bounded local carrier interpretation. | Supports the wording that `D_f_hat` is a local admissible carrier and not a production, security, or clinical claim. | The simulator can describe the baton/FfeD framing as local educational theory context only. |
| Local source: `C:\Users\jeans\Desktop\livre pdf\Fractal_NeutroGeometry_Livre_V2_chapters_1_to_7.pdf` | Fractal dimension grammar around `D_f`, `D_min`, `D_max`, normalized `D_f_hat`, and specialized `I_fractal`/`i_fractal` interpretation. | `normalize_fractal_dimension()` computes bounded `D_f_hat`; `fractal_carrier_profile()` returns `D_f_hat`, `dF_carrier`, `i_fractal_candidate`, hierarchy, and research boundary. | The simulator can expose a tested normalized fractal carrier while preserving `I -> I_system^S -> D_f -> dF -> i_fractal`. |

## Accepted Implementation Claims

- `state_basis="binary"` preserves the existing QNN encoding path.
- `state_basis="neutrobit"` appends a compact neutrobit feature expansion before the QNN/Torch surrogate lane.
- `puncture_delta` is a finite positive simulation parameter for FPW-style local grids.
- `observer_strength` is an optional educational parameter for bounded partial-observer T/I/F profiling.
- `fractal_dimension`, `fractal_dimension_min`, and `fractal_dimension_max` are optional provided values for calculating `D_f_hat`.
- `D_f_hat` is a calculated output carrier, clamped to `[0, 1]`, and can be surfaced as `i_fractal_candidate` metadata when the context is admissible.
- NeuroBit gate output is deterministic and bounded when Qiskit is unavailable.
- NeuroBit `gate_semantics` and `reversibility_profile` are trace metadata only.
- Measurement output is a non-projective triplet distribution for local simulation.

## Forbidden Claims

- Do not claim physical construction of a neutrosophic quantum computer.
- Do not claim clinical, diagnostic, therapeutic, emergency, or safety-critical behavior.
- Do not claim encryption, secure transport, or production security from NeuroBit tunnel/noise demos.
- Do not imply that Qiskit, TorchQuantum, quanvolution, or physical quantum execution is validated by the default runtime.
- Do not collapse the hierarchy `I -> I_system^S -> D_f -> dF -> i_fractal`.
- Do not equate the full indeterminacy layer with the normalized fractal carrier.

## Current Code Targets

- `core/neutrosophic_quantum_primitives.py`: pure source-backed math primitives, `D_f_hat` carrier normalization, gate algebra, puncture grids, and observer profiling.
- `core/neurobit_gate_tunnel.py`: deterministic NeuroBit gate/run output enriched with triplet measurement, semantics, reversibility, observer, puncture, and optional fractal-carrier metadata.
- `core/qnn_nucleus.py`: optional neutrobit, observer, and fractal-carrier feature expansion for QNN/Torch surrogate paths.
- `core/plithogenic_logic.py`: opt-in runtime attribute profiles, dependence/contradiction metadata, cumulative plithogenic truth, and bounded feature vectors.
- `api/schemas.py`: backward-compatible optional fields `state_basis`, `puncture_delta`, `observer_strength`, and fractal carrier inputs; NeuroBit-only surface dimensions.
- Tests: primitives, NeuroBit regression, QNN opt-in feature expansion, and API compatibility.
