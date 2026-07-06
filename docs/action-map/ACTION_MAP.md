# FNP-QNN Action Map

This is the human-readable companion to `ACTION_MAP.json`. It maps the current
repo surfaces to future panel functions without building the panel yet.

Scope: local alpha, non-clinical research simulator. The mapping is neutral: it
records what exists, what is safe to expose later, and what must remain hidden
or disabled.

## Guardrails

- No arbitrary shell execution.
- No clinical, diagnostic, therapeutic, emergency, safety, or production-public action.
- Qiskit, TorchQuantum, R/FFED-RNASeq, live Cerebrum replay, and LVFM registry paths are optional or experimental unless separately validated.
- Preserve `I -> I_system^S -> D_f -> dF -> i_fractal`; do not collapse `dF` into generic `I`.

## Stable API Actions

| Action | Entrypoint | Panel function | Risk | Evidence |
| --- | --- | --- | --- | --- |
| API root metadata | `GET /` | `status_check` | low | `README.md`, `api/main.py` |
| API health check | `GET /health` | `status_check` | low | README public contract |
| Cerebrum adapter status | `GET /cerebrum/status` | `status_check` | low | README public contract |
| Encode observations | `POST /cerebrum/encode` | `run_api_action` | low | `api/schemas.py`, `tests/test_cerebrum_qnn.py` |
| Runtime bridge status | `GET /cerebrum/runtime/status` | `status_check` | low | runtime API tests |
| Runtime ingest | `POST /cerebrum/runtime/ingest` | `run_api_action` | low | runtime API tests |
| Runtime pairs | `POST /cerebrum/runtime/pairs` | `run_api_action` | low | `core/cerebrum_runtime_bridge.py` |
| Runtime run | `POST /cerebrum/runtime/run` | `run_api_action` | medium | runtime API tests |
| Legacy fixture demo | `GET /cerebrum/runtime/legacy-demo` | `run_demo` | low | README run section |
| QNN candidate matrix | `GET /qnn/candidates` | `status_check` | low | QNN tests |
| QNN smoke | `POST /qnn/smoke` | `run_api_action` | medium | QNN smoke tests |
| Novak-Anderson phi/pi status | `GET /fnp-qnn/novak-anderson/status` | `status_check` | low | `tests/test_api_novak_anderson_phi_pi.py` |
| Novak-Anderson convergence | `POST /fnp-qnn/novak-anderson/convergence` | `run_api_action` | low | `tests/test_api_novak_anderson_phi_pi.py` |
| Command route | `POST /commands/{command_name}` | `run_api_action` | medium | command route tests |
| Compatibility shim | `POST /execute-command` | `run_api_action` | medium | shell rejection test |

## Experimental API Actions

| Action | Entrypoint | Panel function | Risk | Why hidden |
| --- | --- | --- | --- | --- |
| LVFM gate trace | `POST /cerebrum/runtime/gate-run` | `experimental_hidden` | high | Appends JSONL and can publish registry state. |
| LVFM gate history | `GET /cerebrum/runtime/gate-history` | `experimental_hidden` | medium | Depends on local LVFM history files. |
| WebSocket command bridge | `WS /ws` | `experimental_hidden` | medium | Command bridge should not be first panel surface. |

## Allowlisted Commands

| Command | Panel function | Risk | Notes |
| --- | --- | --- | --- |
| `phi-status` | `status_check` | low | Generates in-memory synthetic particles. |
| `novak-anderson-phi-pi` | `status_check` | low | Runs source-backed classical phi/pi convergence checks. |
| `cerebrum-runtime-status` | `status_check` | low | Read-only runtime status. |
| `cerebrum-runtime-run` | `run_api_action` | medium | Runs local runtime and QNN path. |
| `cerebrum-runtime-gate-run` | `experimental_hidden` | high | Writes LVFM history and can publish registry state. |
| `cerebrum-runtime-legacy-demo` | `run_demo` | low | Fixture-backed replay. |
| `qnn-smoke` | `run_api_action` | medium | Runs torch surrogate or optional Qiskit lane. |

## Demos

| Demo | Entrypoint | Panel function | Risk |
| --- | --- | --- | --- |
| Adapter/QNN smoke demo | `python examples/cerebrum_qnn_demo.py` | `run_demo` | low |
| Runtime bridge smoke demo | `python examples/cerebrum_runtime_demo.py` | `run_demo` | low |
| Legacy fixture replay | `python examples/cerebrum_runtime_legacy_demo.py` | `run_demo` | low |
| Legacy unvalidated demo | `python examples/legacy_unvalidated_demo.py` | `experimental_hidden` | medium |

## Validation Actions

| Validation | Entrypoint | Panel function | Risk |
| --- | --- | --- | --- |
| Full unit/API tests | `python -m unittest discover -s tests -p "test_*.py"` | `run_validation` | medium |
| Alpha readiness gate | `python scripts/validate_alpha_readiness.py` | `run_validation` | medium |
| Cerebrum/QNN tests | `python -m unittest tests.test_cerebrum_qnn` | `run_validation` | medium |
| Runtime bridge/API tests | `python -m unittest tests.test_cerebrum_runtime_bridge` | `run_validation` | medium |
| LVFM registry anchor tests | `python -m unittest tests.test_lvfm_registry_anchor` | `experimental_hidden` | medium |

## Scripts And Local Configuration

| Script | Panel function | Risk | Mapping decision |
| --- | --- | --- | --- |
| `scripts/export_cerebrum_legacy_snapshot.py` | `configure_local` | high | Optional live RethinkDB export; not default panel action. |
| `scripts/lvfm_windows_bootstrap.py` | `experimental_hidden` | high | Local API loop and optional registry publish. |
| `scripts/lvfm_bit_cost_audit.ps1` | `experimental_hidden` | high | PowerShell/local registry/history readback. |
| `scripts/read-lvfm-registry-window.ps1` | `experimental_hidden` | high | Registry readback. |
| `scripts/setup-lvfm-registry-boot.ps1` | `disabled_unsafe` | critical | Registry/startup integration setup. |
| `scripts/lvfm_bootstrap_window.cmd` | `disabled_unsafe` | critical | Starts command window/process. |

## Core Modules

| Module | Panel function | Risk | Role |
| --- | --- | --- | --- |
| `api/schemas.py` | `inspect_module` | low | Pydantic contracts. |
| `core/cerebrum_adapter.py` | `inspect_module` | low | Crossmodal feature encoding. |
| `core/cerebrum_runtime_bridge.py` | `inspect_module` | medium | Runtime state, pairs, legacy fixture loading, LVFM snapshot path. |
| `core/qnn_nucleus.py` | `inspect_module` | medium | Candidate matrix and torch/Qiskit smoke paths. |
| `core/phi_framework.py` | `inspect_module` | medium | Synthetic phi research primitives. |
| `core/life_science_port.py` | `inspect_module` | medium | Dormant opt-in StateField adapter. |
| `core/lvfm_runtime_graph.py` | `experimental_hidden` | medium | Local LVFM graph trace. |
| `core/lvfm_gate_ledger.py` | `experimental_hidden` | high | Writes gate JSONL history. |
| `core/lvfm_registry_anchor.py` | `disabled_unsafe` | critical | Can write HKCU registry state. |

## Reports And Evidence

| Artifact | Panel function | Risk |
| --- | --- | --- |
| `docs/alpha-readiness.md` | `inspect_report` | low |
| `reports/alpha_readiness_2026-06-12.md` | `inspect_report` | low |
| `reports/qnn_lane_tdr.md` | `inspect_report` | low |
| `reports/cerebrum_runtime_wiring_report.md` | `inspect_report` | low |
| `reports/readme_evidence_audit_2026-06-11.md` | `inspect_report` | low |
| `reports/cerebrum_qnn_status.md` | `inspect_report` | low |
| `GRAPH_THEORY_PHASE_LOG_2026-06-12.md` | `experimental_hidden` | medium |

## Explicit Exclusions

| Exclusion | Panel function | Reason |
| --- | --- | --- |
| Clinical/diagnostic/therapeutic/safety/emergency/production-public workflows | `disabled_unsafe` | README and readiness gate forbid these claims. |
| Arbitrary shell commands | `disabled_unsafe` | The API must stay allowlist-only and shell-free. |
| One-click Windows registry boot setup | `disabled_unsafe` | System integration and process launch risk. |

## Coverage Check

- Endpoints: mapped.
- Allowlisted commands: mapped.
- Demos: mapped.
- Tests and validation gates: mapped.
- Local scripts: mapped.
- Core modules: mapped.
- Reports/docs: mapped.
- Experimental LVFM surfaces: preserved but hidden or disabled.

