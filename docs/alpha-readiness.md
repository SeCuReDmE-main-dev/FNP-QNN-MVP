# Alpha Readiness Matrix

This repository is an alpha-local research simulator. It is not a clinical,
diagnostic, therapeutic, safety, or production-public system.

## Validated Locally

- `python -m unittest discover -s tests -p "test_*.py"`
- `python examples/cerebrum_qnn_demo.py`
- `python examples/cerebrum_runtime_demo.py`
- `python examples/cerebrum_runtime_legacy_demo.py`
- Torch surrogate fallback for local smoke paths.

## Scaffolded Or Optional

- Qiskit and Qiskit Machine Learning are optional extras.
- TorchQuantum and quanvolution lanes are candidates only.
- RethinkDB export support is an offline snapshot utility, not a live runtime dependency.
- Life-science StateField conversion is an observation adapter only.

## Not Claimed

- No clinical validation.
- No diagnostic validation.
- No therapeutic validation.
- No safety validation.
- No live legacy Cerebrum database replay has been proven by the default runtime.

## Alpha Exit Gate

- Shell execution is not available through public API endpoints.
- Public routes use Pydantic request contracts.
- Runtime payloads are size-limited and reject invalid non-finite numeric inputs.
- README and reports must stay tied to local tests, demo output, and explicit evidence.
