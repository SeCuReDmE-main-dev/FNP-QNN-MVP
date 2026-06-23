# Axiomatic-Chamber Gravity Null-Test Status - 2026-06-23

Branch: `experiment/axiomatic-chamber-gravity-null-test`

## Implemented

- Core chamber primitives in `core/axiomatic_chamber.py`.
- Gravity null-test simulator in `core/gravity_null_test.py`.
- Bell-state vs graviton-node chamber taxonomy through:
  - `bell_state_reference_profile()`
  - `bell_vs_gravity_chamber_taxonomy()`
- API endpoints:
  - `GET /fnp-qnn/gravity-null-test/status`
  - `POST /fnp-qnn/gravity-null-test/run`
- QNN smoke opt-in flag: `gravity_null_test_enabled`.
- Optional SeQUeNCe event-spec export.
- Optional Qiskit preview.
- Optional E2B micro-VM and Datadog telemetry review contract.
- Network Designer preset: `gravity_null_test`.
- Source ledger and experiment documentation.
- README expansion preserving the educational sections and adding the Vedral source lane, E2B/Datadog review lane, Penrose/Hameroff relation, and Bell-vs-chamber distinction.

## Bell State Vs Chamber Result

The implementation treats these as separate objects:

- Bell state: `A-B` state/correlation reference only.
- Gravity/null-test chamber: axiomatic room that wraps the Bell input with uncorrelated `C`, chamber bounds, no-signalling residual, frustration index, `Adm`, telemetry, and graviton-constraint placeholder.

No Bell-state output is allowed to imply graviton mass, faster-than-light signalling, or physical quantum-gravity proof.

## Validation

Passed locally with the repo `.venv`:

```powershell
python -m unittest tests.test_gravity_null_test
python -m unittest tests.test_api_qnn_smoke
python -m unittest tests.test_network_designer_executor
python -m unittest tests.test_network_designer_serialization
python -m unittest discover -s tests -p "test_*.py"
```

Full discovery result:

```text
Ran 192 tests in 55.429s
OK
```

Observed warning:

```text
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
```

The warning is pre-existing dependency drift and did not fail the suite.

## Public Boundary

This branch proves a simulator principle only: source isolation, residual classification, admissibility discipline, and telemetry review. It does not prove quantum gravity, exact graviton mass, biological microtubule validation, consciousness, clinical behavior, security behavior, or production readiness.
