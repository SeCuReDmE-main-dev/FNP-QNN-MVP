# Educational Use

FNP-QNN is an alpha-local, non-clinical educational research simulator.

It is intended for learning and supervised experimentation around:

- structured memory-event payloads;
- feature-vector encoding;
- deterministic neural fallback execution;
- optional QNN candidate lanes;
- NeuroBit gate profiles and traces;
- Penrose/Hameroff study metadata;
- Hydra-EM-GPCN hypothesis profiles using `GPCN-Set_phi`;
- five bounded Quantum Paradoxes multiverse experiment profiles;
- six bounded time-physics experiment profiles;
- local evidence dashboards;
- future visual network-design workflows.
- public-safe neutrino admission checks using a Synthia lexical gate packet.

## Neutrino Admission Gate

The neutrino admission gate validates whether a Synthia `LexPacket_neutrino`
allows downstream FNP-QNN simulation work. It does not compute `D_f`, `dF`, or
`i_fractal`; it only decides whether the simulator may proceed after lexical
admission.

If the Synthia packet includes `chapter3_profile`, the gate can preserve the
admitted carriers for later simulation work:

- `I_flavor`;
- `I_mass`;
- `I_phase`;
- `I_interaction`;
- `I_secondary`;
- `I_detector`.

Use:

```bash
python -m fnp_qnn_cli --json neutrino guardrail-check --input tests/fixtures/neutrino_valid_admission.json
```

The maintained boundary is:

- educational simulation;
- simulation is not detection;
- flavor state is not mass propagation state;
- weak interaction primary guardrail;
- secondary detector response is not a primary strong-force interaction;
- Synthia classifies before FNP-QNN computes;
- `dL_lex != dF`;
- `I_lexicon != i_fractal`;
- candidate is not proof.

## Not For Clinical Use

This project is not clinical, diagnostic, therapeutic, emergency,
safety-critical, or production-public software.

Do not use it to make medical, treatment, safety, or patient-care decisions.

## Suggested Course / Lab Use

Good classroom or lab exercises include:

- inspect a fixture-backed memory payload;
- encode observations into a feature vector;
- compare deterministic Torch fallback output with unavailable optional lanes;
- run the NeuroBit gate demo and inspect its trace;
- run the age-14+ learning pack: `python examples/learning_experiment_lab.py --age 15`;
- inspect a Penrose/Hameroff objective-reduction timing profile;
- run a Hydra-EM-GPCN Orch OR-style proxy profile and compare the bounded
  verdicts `communicates`, `decoheres`, `suspended`, and `rejected`;
- run the five Quantum Paradoxes multiverse experiment lanes and compare
  simulator evidence against forbidden ontology/signalling claims;
- run the six time-physics experiment lanes and compare manifest time,
  relativity, entropy, decoherence, cosmology, and time-travel paradox metadata
  against forbidden ontology, quantum-gravity, and operational time-travel
  claims;
- run a computational anesthesia damping sweep and discuss why it is not
  clinical anesthesia guidance;
- discuss why optional Qiskit execution must be reported separately from a fallback;
- design a small future Network Designer preset on paper before implementing it.

## Reproducibility

Use these commands as the baseline local check:

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_alpha_readiness.py
python examples/neurobit_gate_demo.py
```

## Current Advanced Study Layers

The Penrose/Hameroff, Hydra-EM-GPCN, Quantum Paradoxes multiverse, and
time-physics layers are optional educational study surfaces. They are useful for
reading code, comparing bounded feature vectors, and discussing how speculative
theory can be represented without overclaiming.

They do not validate biological microtubule communication, anesthesia effects,
consciousness, quantum gravity, many-worlds ontology, eternalism, time travel,
clinical decisions, or physical quantum execution. The time-physics source IDs
are kept separate from the prior Dr. Maria Violaris/Royal Institution source IDs
in the source ledger.
