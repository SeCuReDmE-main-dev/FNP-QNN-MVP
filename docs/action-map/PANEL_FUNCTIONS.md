# FNP-QNN Panel Function Contract

This file defines the only panel functions allowed by the action map. It is a
mapping contract, not a UI implementation.

The panel must keep the simulator in alpha-local, non-clinical mode. It must
not expose arbitrary shell execution or any clinical, diagnostic, therapeutic,
emergency, safety, or production-public workflow.

## Function Set

| Panel function | Purpose | Allowed action shape | Default UI treatment |
| --- | --- | --- | --- |
| `status_check` | Read current state or metadata. | Safe GET endpoints, allowlisted status commands, local availability checks. | Visible as read-only status cards. |
| `run_demo` | Run deterministic local examples or fixture-backed demos. | README-listed demos or equivalent API demo routes. | Visible with clear alpha-local labels. |
| `run_validation` | Run tests or readiness gates. | Unit tests, alpha readiness script, focused test modules. | Visible as validation actions; output is pass/fail evidence. |
| `run_api_action` | Send typed payloads to simulator API actions. | Pydantic-backed endpoints and allowlisted command routes. | Visible only with schema-bound inputs and validation feedback. |
| `inspect_report` | Open evidence, status, or readiness artifacts. | Markdown, text, or HTML reports already present in the repo. | Visible as read-only document links. |
| `inspect_module` | Explain or inspect a code module without running it. | Core modules and API schemas. | Visible as read-only module cards. |
| `configure_local` | Prepare optional local data or integration state. | Bounded setup/export actions with explicit inputs and side effects. | Hidden behind an advanced/local configuration section. |
| `experimental_hidden` | Preserve but hide unstable local surfaces. | LVFM, registry, WebSocket, unvalidated demos, or local-only work in progress. | Hidden by default; no one-click execution in first panel. |
| `disabled_unsafe` | Record actions that must not be exposed as executable panel controls. | Registry boot setup, command window launchers, arbitrary shell, clinical claims. | Never executable; shown only in audit/exclusion views. |

## Mapping Rules

- Every action receives exactly one `panel_function`.
- If an action writes files, starts processes, touches HKCU registry, calls a live external service, or loops, it cannot be `status_check`, `run_demo`, or `run_api_action` unless it is explicitly sandboxed later.
- LVFM registry publication and Windows boot integration stay `experimental_hidden` or `disabled_unsafe`.
- `/execute-command` remains a compatibility shim only. It routes allowlisted simulator commands and must never become shell execution.
- The theoretical trace language must preserve `I -> I_system^S -> D_f -> dF -> i_fractal`.

## Risk Levels

| Risk | Meaning |
| --- | --- |
| `low` | Read-only or deterministic local computation with no durable writes. |
| `medium` | Local computation with test/cache writes, model execution, or optional dependency checks. |
| `high` | Writes local artifacts, touches optional live integrations, or requires advanced operator intent. |
| `critical` | Starts processes, writes OS registry/boot integration, enables shell execution, or risks false public/clinical claims. |

## MVP Relevance Labels

| Label | Meaning |
| --- | --- |
| `stable_contract` | Present in README/API/tests and suitable for future panel exposure. |
| `stable_contract_plus_experimental_lvfm` | Stable base path now includes local LVFM additions that still need careful exposure. |
| `compatibility` | Kept for internal or legacy compatibility, not primary UX. |
| `local_evidence` | Useful local evidence/report, not an executable simulator capability. |
| `optional_future` | Recognized future lane, not required for default local runtime. |
| `experimental_local` | Present in local checkout but not stable public contract. |
| `excluded` | Explicitly not part of the tool. |

