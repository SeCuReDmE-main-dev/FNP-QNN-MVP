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
- local evidence dashboards;
- future visual network-design workflows.

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
- inspect a Penrose/Hameroff objective-reduction timing profile;
- run a Hydra-EM-GPCN Orch OR-style proxy profile and compare the bounded
  verdicts `communicates`, `decoheres`, `suspended`, and `rejected`;
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

The Penrose/Hameroff and Hydra-EM-GPCN layers are optional educational study
surfaces. They are useful for reading code, comparing bounded feature vectors,
and discussing how speculative theory can be represented without overclaiming.

They do not validate biological microtubule communication, anesthesia effects,
consciousness, quantum gravity, clinical decisions, or physical quantum
execution.
