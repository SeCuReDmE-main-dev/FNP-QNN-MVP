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

## Accepted Implementation Claims

- `state_basis="binary"` preserves the existing QNN encoding path.
- `state_basis="neutrobit"` appends a compact neutrobit feature expansion before the QNN/Torch surrogate lane.
- `puncture_delta` is a finite positive simulation parameter for FPW-style local grids.
- `observer_strength` is an optional educational parameter for bounded partial-observer T/I/F profiling.
- NeuroBit gate output is deterministic and bounded when Qiskit is unavailable.
- NeuroBit `gate_semantics` and `reversibility_profile` are trace metadata only.
- Measurement output is a non-projective triplet distribution for local simulation.

## Forbidden Claims

- Do not claim physical construction of a neutrosophic quantum computer.
- Do not claim clinical, diagnostic, therapeutic, emergency, or safety-critical behavior.
- Do not claim encryption, secure transport, or production security from NeuroBit tunnel/noise demos.
- Do not imply that Qiskit, TorchQuantum, quanvolution, or physical quantum execution is validated by the default runtime.
- Do not collapse the hierarchy `I -> I_system^S -> D_f -> dF -> i_fractal`.

## Current Code Targets

- `core/neutrosophic_quantum_primitives.py`: pure source-backed math primitives, gate algebra, puncture grids, and observer profiling.
- `core/neurobit_gate_tunnel.py`: deterministic NeuroBit gate/run output enriched with triplet measurement, semantics, reversibility, observer, and puncture metadata.
- `core/qnn_nucleus.py`: optional neutrobit and observer feature expansion for QNN/Torch surrogate paths.
- `api/schemas.py`: backward-compatible optional fields `state_basis`, `puncture_delta`, and `observer_strength`; NeuroBit-only surface dimensions.
- Tests: primitives, NeuroBit regression, QNN opt-in feature expansion, and API compatibility.
