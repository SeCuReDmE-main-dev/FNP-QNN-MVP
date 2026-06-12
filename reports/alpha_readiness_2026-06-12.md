# Alpha Readiness Report - 2026-06-12

Status: alpha-local candidate after P0 hardening.

## Evidence

- Unit/API tests are the required local gate.
- The runtime bridge, adapter, and Torch surrogate fallback are the validated default path.
- Qiskit, TorchQuantum, quanvolution, R, and live legacy database replay remain optional or unproven.

## Required Command Gate

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_alpha_readiness.py
```

## Public Claim Boundary

The project may be described as a local non-clinical research simulator. It must not be described as clinical, diagnostic, therapeutic, safety-validated, or production-public.
