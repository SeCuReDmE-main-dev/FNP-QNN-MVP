# Quantum-Neutrosophic Source Ledger

This ledger maps Prof. Florentin Smarandache's quantum-neutrosophic sources to bounded simulator mechanisms. It is implementation guidance for an alpha-local educational research simulator.

Boundary: FNP-QNN does not claim to implement a physical neutrosophic quantum computer, clinical tool, security product, production system, or validated quantum physics engine. The code uses small, deterministic, source-attributed primitives as simulation grammar.

## Sources And Simulator Binding

| Source | Relevant concept | Simulator binding | Public-safe claim |
| --- | --- | --- | --- |
| [Neutrosophic Quantum Computer](https://fs.unm.edu/NeutrosophicQuantumComputer.pdf) | Theoretical neutrobit basis `0`, `1`, and `I`; refined indeterminacy; neutrosophic superposition; reversibility concerns. | `core/neutrosophic_quantum_primitives.py` models `NeutrobitState`; `core/neurobit_gate_tunnel.py` keeps `W` as the local `|I>` marker. | The simulator can demonstrate a deterministic neutrobit-style feature grammar. |
| [Neutrosophic Logic Based Quantum Computing](https://fs.unm.edu/neut/NeutrosophicLogicBasedQuantum.pdf) | Coherent versus decoherent neutrosophic states; non-projective measurement returning a distribution over `|0>`, `|1>`, `|I>`. | `CoherentNeutroState`, `DecoherentNeutroState`, and `neutrosophic_measurement()` return a triplet distribution instead of forcing binary collapse. | The simulator can expose a T/I/F-style measurement preview for educational inspection. |
| [Infinitesimally Punctured Wave program](https://fs.unm.edu/IPW/) and related short articles: [IPW](https://fs.unm.edu/NSS/39Infinitesimally.pdf), [comparison](https://fs.unm.edu/NSS/6InfinitesimallyPunctured.pdf) | Discrete-continuous bridge: a wave/surface/space can be represented as ordered punctures/sub-particles. | `punctured_wave_state()` creates a deterministic ordered puncture state for simulation and feature expansion. | The simulator can show a finite puncture-grid analogy for wave-like states. |
| [From IPW to FPW](https://fs.unm.edu/IPW/IPW-to-FPW.pdf) | FPW replaces virtual infinitesimal spacing with practical finite `delta > 0`. | API fields accept optional `puncture_delta`; QNN feature expansion can append finite puncture metadata. | The simulator can use finite spacing as a reproducible local simulation parameter. |
| [Neutrosophic Quantum Theory: Partial Entanglement, Partial Effect of the Observer, and Teleportation](https://fs.unm.edu/NSS/1QuantumTheory.pdf) | T/I/F describes partial entanglement, separability/failure, and decoherence/noise. | `partial_entanglement_profile()` maps correlation, separability, decoherence, and `dF` into a bounded T/I/F profile. | The simulator can inspect partial-correlation scenarios without binary overclaiming. |

## Accepted Implementation Claims

- `state_basis="binary"` preserves the existing QNN encoding path.
- `state_basis="neutrobit"` appends a compact neutrobit feature expansion before the QNN/Torch surrogate lane.
- `puncture_delta` is a finite positive simulation parameter for FPW-style local grids.
- NeuroBit gate output is deterministic and bounded when Qiskit is unavailable.
- Measurement output is a non-projective triplet distribution for local simulation.

## Forbidden Claims

- Do not claim physical construction of a neutrosophic quantum computer.
- Do not claim clinical, diagnostic, therapeutic, emergency, or safety-critical behavior.
- Do not claim encryption, secure transport, or production security from NeuroBit tunnel/noise demos.
- Do not imply that Qiskit, TorchQuantum, quanvolution, or physical quantum execution is validated by the default runtime.
- Do not collapse the hierarchy `I -> I_system^S -> D_f -> dF -> i_fractal`.

## Current Code Targets

- `core/neutrosophic_quantum_primitives.py`: pure source-backed math primitives.
- `core/neurobit_gate_tunnel.py`: deterministic NeuroBit gate/run output enriched with triplet measurement metadata.
- `core/qnn_nucleus.py`: optional neutrobit feature expansion for QNN/Torch surrogate paths.
- `api/schemas.py`: backward-compatible optional fields `state_basis` and `puncture_delta`.
- Tests: primitives, NeuroBit regression, QNN opt-in feature expansion, and API compatibility.
