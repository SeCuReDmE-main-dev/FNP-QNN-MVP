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
- Novak-Anderson phi/pi theorem convergence checks;
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

If the packet includes `chapter4_profile`, the gate can preserve only the
Synthia lexical guard:

- `admitted_chapter4_guard`;
- `allowed_payload`;
- `excluded_payload_summary`.

This supports partitioned language: a recoverable metaphor can remain in
`excluded_payload_summary` while only the admitted public-safe payload continues
toward later simulation work.

If the packet includes `chapter5_intake_profile`, the admission gate can also
preserve `admitted_chapter5_intake`. A separate chapter-5 command can then
normalize a supplied public-safe carrier request into `D_f_hat`:

Use:

```bash
python -m fnp_qnn_cli --json neutrino guardrail-check --input tests/fixtures/neutrino_valid_admission.json
```

Chapter-5 carrier example:

```bash
python -m fnp_qnn_cli --json neutrino chapter5-carrier --input tests/fixtures/neutrino_chapter5_valid_admission.json
```

The chapter-5 carrier command does not compute `dF`, `i_fractal`, or
`i_fractal_candidate`; those remain outside this public-safe step.

If the packet includes `chapter6_vector_profile`, the admission gate can also
preserve `admitted_chapter6_vector` and `chapter6_guardrail_check` without
computing friction. The required vector is `I_neutrino_vec`, with ten carriers:
`I_source`, `I_flavor`, `I_mass`, `I_mix`, `I_phase`, `I_medium`,
`I_interaction`, `I_secondary`, `I_detector`, and `I_uncertainty`.
`I_neutrino_vec` is not `dL_lex`, not `dF`, not a detector signature, and not
proof of detection.

If the packet includes `chapter7_transition_profile`, the admission gate can
also preserve `admitted_chapter7_transition`. The separate chapter-7 readout
command may then compute the public-safe simulation readout after Synthia has
approved the transition:

```bash
python -m fnp_qnn_cli --json neutrino chapter7-readout --input tests/fixtures/neutrino_chapter7_valid_admission.json
```

This readout may return `D_f`, `D_f_hat`, `dF`, and
`i_fractal_candidate`, but only as a conditional educational simulation
candidate. It is not detector evidence and it is not physical proof.

If the packet includes `chapter8_run_profile`, the admission gate can preserve
`admitted_chapter8_run`. The separate chapter-8 command validates whether the
first run may continue:

```bash
python -m fnp_qnn_cli --json neutrino chapter8-run --input tests/fixtures/neutrino_chapter8_valid_admission.json
```

This command returns permission status only. It does not compute `D_f`,
`D_f_hat`, `dF`, `i_fractal`, or `i_fractal_candidate`. The allowed status
`admissible_under_guardrails` means the run may continue inside the educational
simulation boundary; it is not detection and not proof.

If the packet includes `chapter9_source_choice_profile`, the admission gate can
preserve `admitted_chapter9_source_choice`. The separate chapter-9 command
validates the public source registry and the central T2K-like simulation choice:

```bash
python -m fnp_qnn_cli --json neutrino chapter9-choice --input tests/fixtures/neutrino_chapter9_valid_admission.json
```

This command can only prepare the next educational container. It is not T2K
reproduction, not a CP measurement, not detector evidence, not physical proof,
and not a downstream fractal calculation.

If the packet includes `chapter10_chamber_profile`, the admission gate can
preserve `admitted_chapter10_chamber`. The separate chapter-10 command validates
the declared chamber, container, simulated event, and run contract for the next
controlled passage:

```bash
python -m fnp_qnn_cli --json neutrino chapter10-contract --input tests/fixtures/neutrino_chapter10_valid_admission.json
```

This command can only prepare a chapter-11 run contract. It does not execute the
run, does not reproduce T2K, does not measure CP violation, does not treat a
container as physical proof, and does not compute `D_f`, `D_f_hat`, `dF`,
`i_fractal`, or `i_fractal_candidate`.

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

## Novak-Anderson Phi/Pi Lab

The Novak-Anderson layer lets students inspect how odd-sided polygon Golden
Numbers connect the golden ratio to the pseudopi chain, and how the pseudopi
function approaches pi as polygon order increases.

Good lab checks include:

- verify `golden_number(2, 2) = phi`;
- verify `pseudopi(2) = 5 / phi`;
- compare Fibonacci-vector component ratios with polygon Golden Numbers;
- inspect convergence error as `n` increases.

This lab proves only the implemented formulas and numerical convergence checks.
It does not prove a physical quantum effect, cosmology, cryptographic security,
clinical behavior, or consciousness.

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
