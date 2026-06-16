# Educational Use

FNP-QNN is an alpha-local, non-clinical educational research simulator.

It is intended for learning and supervised experimentation around:

- structured memory-event payloads;
- feature-vector encoding;
- deterministic neural fallback execution;
- optional QNN candidate lanes;
- NeuroBit gate profiles and traces;
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
- discuss why optional Qiskit execution must be reported separately from a fallback;
- design a small future Network Designer preset on paper before implementing it.

## Reproducibility

Use these commands as the baseline local check:

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_alpha_readiness.py
python examples/neurobit_gate_demo.py
```
