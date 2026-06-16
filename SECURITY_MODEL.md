# Security Model

## Project Boundary

FNP-QNN is an alpha-local, non-clinical research simulator. It is not a
production security product and does not provide medical, diagnostic,
therapeutic, emergency, or safety-critical guarantees.

## Trust Boundaries

Public-safe layer:

- repository source code;
- tests and fixture demos;
- Panel dashboard screenshots that expose no secrets;
- public documentation.

Private/local layer:

- `.env` values;
- CeLeBrUm local memory/evidence corpus;
- unpublished white paper or book material;
- operator tokens;
- private Datadog/E2B configuration;
- local machine paths that reveal sensitive context.

## Runtime Assumptions

- The default runtime is local.
- Qiskit, TorchQuantum, Datadog, E2B, and legacy database paths are optional.
- Missing optional services must not break the base runtime.
- The NeuroBit tunnel demo is deterministic signal/noise metadata only. It is
  not encryption and not a security guarantee.

## Data Handling

- Do not commit secrets, API keys, tokens, credentials, or private corpus text.
- Use synthetic or fixture-backed data for public examples.
- Do not expose clinical, patient, or personal data.
- Keep CeLeBrUm material private unless explicitly sanitized and approved.

## Validation Baseline

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_alpha_readiness.py
```

## Deployment Status

No public production deployment is guaranteed by this repository. Any Vercel,
Datadog, E2B, or institutional hosting path must be documented and validated
separately before being described as operational.
