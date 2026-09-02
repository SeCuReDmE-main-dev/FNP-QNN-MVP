# FNP-QNN to QCG Companion adapter

Status: experimental, local, read-only adapter proof
Schema: `securedme.fnp-qnn.qcg-companion-adapter.v1`

This adapter projects a compact FNP-QNN runtime summary into the existing
`qcg-console-snapshot.v2` contract. QCG keeps its name, its separate browser
extension, and its authority model. FNP-QNN remains an alpha-local,
non-clinical educational/research simulator.

## Boundary

The adapter accepts only these six fields:

- `run_id`
- `status`
- `events_count`
- `pairs_count`
- `feature_dimension`
- `evidence_count`

Unknown fields fail closed. Raw observations, source code, files, paths, URLs,
credentials, provider data and environment values are outside the contract.
The resulting QCG snapshot is memory-only, declares no available commands,
registers no tools, submits no QPU work, and sets `authority_state` to
`unavailable`. It cannot create consent or make a human decision.

## Local navigation

`FnpQnnQcgCompanionAdapter.navigate()` resolves only the current FNP-QNN Panel
destinations: Control Room, Events, Pairs, QNN benchmark, NeuroBit, Raw JSON,
Network Designer, Network Designer Canvas and Chamber Lab. A caller may pass
the existing Panel tab-selection callback. Unknown targets fail before the
callback runs.

This navigation contract does not add a remote route, provider or autonomous
control surface. It is a small host-application adapter for the separately
installed QCG Companion.

## Minimal use

```python
from uuid import uuid4

from core.qcg_companion_adapter import FnpQnnQcgCompanionAdapter

adapter = FnpQnnQcgCompanionAdapter(str(uuid4()))
snapshot = adapter.get_snapshot(
    {
        "run_id": "fnp-qnn-run-7",
        "status": "completed",
        "events_count": 4,
        "pairs_count": 6,
        "feature_dimension": 31,
        "evidence_count": 1,
    }
)
navigation = adapter.navigate("events")
```

## Validation receipt — Action 242

Date: 2026-09-02
Scope: FNP-QNN repository only; the WebMCP-QCG hackathon repository was used
read-only as the contract source of truth.

Validated from the existing SecuredMe Education Python 3.10 environment; no
package was installed and no environment file was read.

| Check | Result |
| --- | --- |
| `python -m unittest tests.test_qcg_companion_adapter -v` | PASS — 9 tests |
| `python -m unittest discover -s tests -p "test_*.py"` | PASS — 461 tests, 2 expected skips |
| `python -m ruff check core/qcg_companion_adapter.py tests/test_qcg_companion_adapter.py` | PASS |
| `python -m mypy --follow-imports=skip core/qcg_companion_adapter.py` | PASS — no issues |
| QCG `snapshotSanitizer.js` contract probe | PASS — v2 snapshot accepted |
| `python scripts/validate_alpha_readiness.py` | PASS — alpha-local gate |

The proof does not change QCG claims, FNP-QNN clinical boundaries, browser
permissions, provider support or the hackathon submission path. A repository-
wide mypy run still reports existing type debt in unrelated imported modules;
the isolated adapter check passes.
