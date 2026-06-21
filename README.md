  ![FNP-QNN Logo](./assets/logo/template%203.png)

# FNP-QNN Local Research Simulator

<p align="center">
  <a href="https://e2b.dev/startups">
    <img alt="Sponsored by E2B for Startups" src="https://img.shields.io/badge/Sponsored%20by-E2B%20for%20Startups-FF8800?style=for-the-badge" />
  </a>
  <a href="https://www.datadoghq.com/partner/datadog-for-startups/">
    <img alt="Supported by Datadog for Startups" src="https://img.shields.io/badge/Supported%20by-Datadog%20for%20Startups-632CA6?style=for-the-badge&amp;logo=datadog&amp;logoColor=white" />
  </a>
</p>

<p align="center">
  <a href="https://orcid.org/0009-0007-2904-0443">
    <img alt="ORCID: 0009-0007-2904-0443" src="https://img.shields.io/badge/ORCID-0009--0007--2904--0443-A6CE39?style=flat-square&amp;logo=orcid&amp;logoColor=white" />
  </a>
  <img alt="Alpha-local research simulator" src="https://img.shields.io/badge/alpha--local-research%20simulator-1f6feb?style=flat-square" />
  <img alt="Non-clinical educational research" src="https://img.shields.io/badge/non--clinical-educational%2Fresearch-6e7781?style=flat-square" />
</p>

## Authorship and Research Boundary

Primary maintainer provenance: Jean-Sébastien Beaulieu  
ORCID: https://orcid.org/0009-0007-2904-0443

This project remains an alpha-local, non-clinical educational/research simulator.
It is not clinical, diagnostic, therapeutic, emergency, safety-critical, or
production-public software.

This repository is an alpha-local, non-clinical research simulator for:

- Cerebrum-shaped interval memory events;
- deterministic crossmodal pair construction;
- feature-vector encoding for QNN candidate lanes;
- a deterministic PyTorch surrogate fallback;
- deterministic NeuroBit gate profiles and trace previews;
- optional future Qiskit and legacy-export evidence lanes.

It is not a clinical, diagnostic, therapeutic, safety, emergency, or production-public system. Public claims must stay tied to local tests, demo output, or explicit reports in this repository.

## Current Status

Validated locally:

- `python -m unittest discover -s tests -p "test_*.py"`
- `python examples/cerebrum_qnn_demo.py`
- `python examples/cerebrum_runtime_demo.py`
- `python examples/cerebrum_runtime_legacy_demo.py`
- Torch surrogate fallback.
- NeuroBit gate and tunnel-noise demo.

Not validated by the default local runtime:

- Qiskit execution;
- TorchQuantum execution;
- quanvolution benchmarking;
- R or FFED-RNASeq tests;
- live historical Cerebrum database replay;
- any clinical, diagnostic, therapeutic, safety, or production-public behavior.

## Fractal Carrier Rules

The simulator accepts an optional deterministic fractal carrier:

```text
D_f_hat(x) = (D_f(x) - D_min) / (D_max - D_min)
```

`D_f_hat` is a bounded local admissible carrier. It can be exposed as
`fractal_carrier.D_f_hat` and, when admissible, as `i_fractal_candidate`
metadata in NeuroBit, QNN smoke, and LVFM runtime snapshots. It does not
replace `indeterminacy`, and the project must preserve this hierarchy:

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```

Accepted inputs are optional `fractal_dimension`, `fractal_dimension_min`, and
`fractal_dimension_max`; public aliases `D_f`, `D_min`, and `D_max` are accepted
by the API. `D_f_hat` is calculated by the simulator and should not be supplied
as an asserted input value.

## CeLeBrUm CPAI/YOLO Bridge

CeLeBrUm can act as a local router between CodeProject.AI/YOLO and this
simulator's LVFM runtime API. The bridge sends sanitized `vision` observations
to `POST /cerebrum/runtime/run`; this repository still owns graph construction,
LVFM snapshots, plugin traces, and `T/I/dF/F` interpretation.

YOLO is a perception tool only. A detection can contribute local `T`,
`I_system_component`, `F`, and `dF` provenance, but it must not replace global
`I` or claim that ambiguity was solved.

Detailed operator notes live in
`FNP-QNN-MVP-organisation/05_status/CELEBRUM_CPAI_YOLO_LVFM_BRIDGE.md`.

## FFeD MVP5 Plugin Hook

The QNN can optionally call the local Codex pluginpack through
`core/ffed_plugin_bridge.py`. This is an application-level hook, not a Codex
manifest hook. It does not add `hooks` to `.codex-plugin/plugin.json`, and it
does not allow arbitrary plugin IDs. The hook is disabled by default and must
be requested with:

```json
{
  "plugin_hook_enabled": true,
  "plugin_set": "mvp5",
  "include_plugin_trace": true
}
```

The bridge acts as a small router in front of the QNN:

1. It receives the simulation observations or a supplied `plugin_context`.
2. It normalizes plugin parameters into the valid range accepted by each plugin.
3. It calls only the MVP5 allowlist.
4. It maps plugin outputs into local `D_f`, `D_min`, `D_max`, `D_f_hat`, `dF`,
   and `i_fractal_candidate` metadata.
5. It returns `impact_verification`, showing which plugin IDs ran and which
   effective parameters they received.

CPAI is the mesh base. The hook does not replace CPAI; it attaches plugin
signals to the CPAI mesh as local, measurable features. The expected mesh nodes
are:

- `cpai-mcp-server`;
- `cpai-celebrum`;
- `cpai-ffed`.

The expected Datadog metric family is:

- `cpai.mesh.local_response_time_ms`;
- `cpai.mesh.effective_response_time_ms`;
- `cpai.mesh.requests_processed_local`;
- `cpai.mesh.requests_forwarded`;
- `cpai.mesh.requests_received`;
- `cpai.mesh.nodes_visible`;
- `cpai.mesh.nodes_active`;
- service check `cpai.mesh.can_connect`.

The project-level Datadog references are dashboard `4i9-v3n-pe7` and notebook
`293549`. The simulator reports these IDs as non-secret mesh metadata only; it
does not silently edit Datadog assets.

The simulator also carries a native `CPAIMeshState` in `core/cpai_mesh.py`.
That state is intentionally small: route, visible nodes, active nodes, response
time, local load, forwarded load, connection state, and a local routing
decision. This prevents the plugin hook from depending on a live external MCP
mesh before the simulator can reason about routing.

The hook measures ambiguity/tension. It does not solve ambiguity, replace
indeterminacy, prove physical stress, make clinical claims, or make security
decisions.

MVP5 plugins:

- `p011_fractales_atomiques`: measures atom overload and recomposition. Example:
  if many event fragments arrive with weak recomposition, the bridge raises the
  local overload carrier because the simulated atom is harder to recompose.
- `p046_rossler_beaulieu_cubic_framework`: measures chaos, divergence, and
  anti-entropy balance. Example: if the time-series becomes more divergent, the
  chaos carrier makes roughness/frustration more visible to the QNN feature
  vector.
- `p097_fbm_tuner`: measures roughness, drift, and instability in a numeric
  series. Example: values `[0.1, 0.3, 0.2, 0.8, 0.4, 0.9]` produce a roughness
  signal that can mark unstable local motion.
- `p109_dual_triplex`: mandatory MVP plugin for dual-triplex fractal density.
  Example: the plugin supplies a native fractal-density carrier that replaces
  the older `p112` MVP slot without treating density as general `I`.
- `p114_ffed_neutrosophic_consensus`: produces the native local `T/I/F`
  consensus. Example: evidence items with high indeterminacy raise only the
  local `I_system_component`, never the full global `I`.

The global plugin carrier is:

```text
D_f_plugin = weighted_mean(p114=0.25, p046=0.25, p097=0.20, p011=0.15, p109=0.15)
D_f_hat_plugin = normalize_fractal_dimension(D_f_plugin, 0, 1)
```

Neutrosophic gate integration:

- `AND(p046, p097)` measures persistent instability: chaos plus roughness.
- `OR(p011, p109)` measures atom/fractal stress: overload or density.
- `IF_THEN(p114, p046)` measures ambiguity that makes chaos relevant.
- `AND(atom/fractal stress, ambiguity chaos)` becomes `plugin_tension_profile`.
- `NOT(stability)` is an explanatory contrast only.

For NeuroBit, plugins can request the local `W` gate when their
`I_system_component` crosses the local threshold. They do not rewrite the
profile's original `truth`, `indeterminacy`, or `falsity`.

Datadog, E2B, and Redis are observability/engine surfaces around the hook:

- Datadog Agent is optional and receives logs/metrics from the Docker stack.
- E2B auditor is optional and can run external sandbox audits.
- `plugin-engine-redis` is optional Docker infrastructure for future
  router/cache/trace distribution. The current Python path falls back to local
  in-process execution when Redis is absent.
- FFeD MCP can be used as an external runtime in Codex sessions that expose it.
  The checked-in simulator uses the local `ffed_runtime.run_plugin(...)` API so
  unit tests remain deterministic.
- Datadog MCP supervision is represented as expected configuration and
  runbook metadata unless Datadog MCP tools are actually available in the
  active session.

No Datadog API key, E2B key, plugin secret, PAT, or raw environment value is
printed in hook output. The status payload reports only booleans such as
`datadog_env_present`, `e2b_env_present`, and `redis_url_present`.

### Future Cerebrum YOLO Lane

The legacy Cerebrum source under
`C:\Users\jeans\Desktop\Case study\modele\cerebrum\Cerebrum` already contains
an OpenCV-based `vision` package and crossmodal mappings for hearing/vision and
vision/language. It does not currently expose YOLO or CPAI as native modules.

Planned integration path:

1. Keep YOLO out of the MVP5 fractal hook.
2. Add a separate Cerebrum image lane that emits bounded vision observations.
3. Route those observations through native `CPAIMeshState`.
4. Feed the resulting vision observations into the existing simulator bridge.
5. Keep YOLO optional because image inference adds heavier dependencies and
   runtime cost.

## Architecture

```text
api/
  main.py                      # typed FastAPI surface and command allowlist
  schemas.py                   # Pydantic request contracts and validation
core/
  cerebrum_adapter.py          # flat and interval event normalization
  cerebrum_runtime_bridge.py   # Cerebrum-shaped runtime bridge and pair builder
  cpai_mesh.py                 # native local CPAI mesh state and routing profile
  life_science_port.py         # dormant StateField-shaped observation adapter
  neurobit_gates.py            # public NeuroBit gate primitive contract
  neurobit_gate_tunnel.py      # NeuroBit gate + tunnel-noise demo runtime
  experiment_seed.py           # deterministic experiment seed provenance
  ffed_plugin_bridge.py        # optional FFeD MVP5 plugin router and D_f mapper
  plithogenic_logic.py         # opt-in plithogenic runtime fusion profile
  plithogenic_probability_statistics.py # plithogenic statistics -> topology bridge
  revolutionary_topologies.py  # opt-in topology-style deformation profile
  quantum_feature_transforms.py # pure amplitude/phase feature transforms
  qnn_nucleus.py               # QNN candidate matrix and Torch fallback
  phi_framework.py             # synthetic phi-framework simulation primitives
examples/
  cerebrum_qnn_demo.py
  cerebrum_runtime_demo.py
  cerebrum_runtime_legacy_demo.py
  neurobit_gate_demo.py
  legacy_unvalidated_demo.py
tests/
  test_cerebrum_qnn.py
  test_cerebrum_runtime_bridge.py
docs/
  alpha-readiness.md
```

## Public API Contract

Core HTTP endpoints:

- `GET /health`
- `GET /cerebrum/status`
- `POST /cerebrum/encode`
- `GET /cerebrum/runtime/status`
- `POST /cerebrum/runtime/ingest`
- `POST /cerebrum/runtime/pairs`
- `POST /cerebrum/runtime/run`
- `GET /cerebrum/runtime/legacy-demo`
- `GET /qnn/candidates`
- `POST /qnn/smoke`
- `GET /fnp-qnn/neurobit/status`
- `POST /fnp-qnn/neurobit/gates/run`
- `POST /fnp-qnn/neurobit/tunnel/demo`
- `GET /fnp-qnn/nidus/status`
- `POST /fnp-qnn/nidus/triplet/profile`
- `POST /fnp-qnn/nidus/fusion/profile`
- `POST /fnp-qnn/nidus/partial-membership/mean`
- `POST /fnp-qnn/plithogenic/runtime/profile`
- `POST /fnp-qnn/revolutionary-topology/runtime/profile`
- `POST /fnp-qnn/plithogenic-topology/runtime/profile`
- `POST /commands/{command_name}`

Compatibility endpoint:

- `POST /execute-command`

`/execute-command` is an internal compatibility shim. It does not execute shell commands. It only routes allowed simulator commands such as `phi-status`, `cerebrum-runtime-status`, `cerebrum-runtime-run`, `cerebrum-runtime-legacy-demo`, and `qnn-smoke`.

## Install

Use the repository-local `.venv`. Do not install this project into your global
Python environment.

Windows PowerShell setup:

```powershell
py -3.10 --version
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

The expected Python version is `3.10.11`. If `py -3.10 --version` does not show
Python 3.10.11, fix Python first before installing dependencies.

One-command local setup:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\Install-FNPQNNVenv.ps1
```

Optional Qiskit plus visualization lane:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\Install-FNPQNNVenv.ps1 -WithQiskit
```

Optional local cloud/operator kit:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\Install-FNPQNNVenv.ps1 -WithCloudKit
```

Full local research kit:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\Install-FNPQNNVenv.ps1 -WithQiskit -WithCloudKit
```

## Optional Kits

The base simulator should stay lightweight. Optional kits are installed only
when a user wants the extra lane they enable.

### Qiskit Kit

The Qiskit kit is for the educational quantum lane. It installs Qiskit,
Qiskit Machine Learning, Aer, Algorithms, IBM Runtime helpers, and Qiskit
visualization support inside `.venv`.

Use it when you want to:

- show a visible quantum/QNN backend lane in the Network Designer;
- run Qiskit availability checks instead of the default gated placeholder;
- experiment with `EstimatorQNN` / `TorchConnector` paths;
- generate educational circuit diagrams and visual traces;
- compare the Qiskit lane against the deterministic Torch surrogate.

The Qiskit kit does not make the simulator clinical, production-ready, or
scientifically validated. It is an optional teaching and backend-experiment
surface.

### CloudKit

The CloudKit is for local operator integrations around the simulator. It keeps
cloud and service clients in `.venv` so experiments do not pollute global
Python.

It is intended to support:

- E2B SDK usage for sandbox smoke tests and future cloud execution checks;
- E2B infrastructure planning with `e2b-dev/infra` as the open-source reference;
- Datadog metrics/tracing clients for metadata-only observability;
- Redis client experiments for local queue/cache/router patterns;
- Docker Python client checks for local engine/container status;
- Supabase client experiments for future public-safe data surfaces.

CodeProject.AI / CPAI is currently reached by HTTP on the local mesh, so no
special Python wheel is required for CPAI in this kit. Vercel is primarily an
npm CLI, so it is documented as an external toolchain dependency rather than a
Python package.

CloudKit must not upload secrets, private documents, raw images, clinical data,
or private CeLeBrUm material. It is for controlled smoke tests, public-safe
metadata, and future reproducibility work.

All validation commands in this README assume `.venv`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\.venv\Scripts\python.exe scripts\validate_alpha_readiness.py
```

## Run

Adapter/QNN smoke demo:

```powershell
.\.venv\Scripts\python.exe examples\cerebrum_qnn_demo.py
```

Runtime bridge smoke demo:

```powershell
.\.venv\Scripts\python.exe examples\cerebrum_runtime_demo.py
```

Legacy fixture replay:

```powershell
.\.venv\Scripts\python.exe examples\cerebrum_runtime_legacy_demo.py
```

NeuroBit gate demo:

```powershell
.\.venv\Scripts\python.exe examples\neurobit_gate_demo.py --truth 0.55 --indeterminacy 0.30 --falsity 0.15
```

Unit/API tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Alpha readiness gate:

```bash
python scripts/validate_alpha_readiness.py
```

API server:

```bash
uvicorn api.main:app --reload --port 8000
```

HoloViz Panel dashboard:

```bash
panel serve panel_app.py --show --port 5006
```

The Panel dashboard is the primary local operator panel. It runs the same
runtime, encoding, QNN smoke, benchmark, and legacy fixture paths as the API
without adding a Node/React build chain.

## Docker stack

The repository now includes a Docker Compose stack for:

- `simulator-api`: FastAPI runtime
- `simulator-panel`: HoloViz Panel control room
- `vllm`: optional `vLLM` OpenAI-compatible server
- `etcd`: optional single-node local state service
- `plugin-engine-redis`: optional Redis router/cache/trace block for the plugin engine
- `datadog-agent`: optional Datadog Agent scraping the `vLLM` metrics endpoint
- `e2b-auditor`: optional E2B sandbox auditor emitting Datadog logs tied to the same stack

Prepare environment values:

```bash
copy .env.docker.example .env
```

Base stack:

```bash
docker compose up --build simulator-api simulator-panel
```

Add the `vLLM` lane:

```bash
docker compose --profile llm up --build vllm
```

Add the `etcd` lane:

```bash
docker compose --profile state up --build etcd
```

Add the optional Redis plugin engine lane:

```bash
docker compose --profile plugin-engine up --build plugin-engine-redis
```

Add Datadog Agent + E2B audit services:

```bash
docker compose --profile llm --profile state --profile observability --profile audit up --build
```

Datadog Agent uses:

- `observability/datadog/agent-conf.d/vllm.d/conf.yaml`
- `observability/datadog/agent-conf.d/etcd.d/conf.yaml`
- `http://vllm:8000/metrics` inside the Compose network
- `http://etcd:2379/metrics` inside the Compose network

For `etcd`, the Datadog check is configured as a containerized integration with:

- integration name: `etcd`
- instance config: `{"prometheus_url": "http://etcd:2379/metrics"}`
- log source/service tags attached on the container through Docker labels

The `e2b-auditor` service reuses `scripts/e2b_datadog_audit/audit_e2b.py` and
adds stack-level tags/metadata so E2B audit logs can be correlated with the
same Docker `vLLM` lane in Datadog.

## Evidence And Reports

- `docs/alpha-readiness.md`: alpha-local evidence matrix.
- `reports/alpha_readiness_2026-06-12.md`: current readiness report.
- `reports/qnn_lane_tdr.md`: QNN lane decision record.
- `reports/cerebrum_runtime_wiring_report.md`: runtime bridge wiring report.
- `reports/readme_evidence_audit_2026-06-11.md`: earlier README evidence audit.

## Datadog and E2B usage in this application

The simulator uses a local, offline-first posture, with **optional external audit tooling**:
This is separate from the core API/Panel runtime and is intended for optional VM/autobuild security checks only.

### 1) Datadog

- **Role**: receives structured audit logs from optional VM security audits.
- **Service tag**: `e2b-vm-auditor`.
- **Mandatory tags**: `env`, `sandbox_id`, `template_id`, `audit_status`.
- **Where it is wired**:
  - `scripts/e2b_datadog_audit/audit_e2b.py`
  - optional workflow orchestration around autobuild and release validation.
- **Local impact**: no Datadog calls are required for the main app runtime.

### 2) E2B

- **Role**: launches temporary audit sandboxes for command checks on generated VM images.
- **Checks executed** in sandbox:
  - package inventory (`dpkg -l` fallback to `pip list`),
  - open ports (`ss -tlnp`),
  - active processes (`ps aux`),
  - environment variables (`env`) with redaction,
  - sensitive path permission checks.
- **Lifetime**: sandbox is destroyed in script cleanup even when a check fails.
- **Where it is used**:
  - `scripts/e2b_datadog_audit/audit_e2b.py`.

### 3) Workflow expectation

Datadog logs from each audit can be used by a monitor, for example:

- `status:error service:e2b-vm-auditor`

This keeps the app evidence loop separated from runtime execution while still surfacing
operator signals for follow-up remediation.

### Optional local scan utility

You can still use `python scripts/glymphatic_scan.py` as a local-only inventory tool:
- read-only, no process termination,
- no automatic file deletion,
- no network action.

## Educational Open Source Use

This project is suitable for supervised educational exploration of local
simulation pipelines, feature encoding, deterministic fallback behavior,
NeuroBit gate traces, and future visual network-design workflows.

Recent quantum-neutrosophic learning additions:

- `core/neutrosophic_quantum_primitives.py` adds a small, pure simulation
  grammar for `NeutrobitState`, coherent/decoherent neutrosophic states,
  non-projective T/I/F measurement, finite punctured-wave states, partial
  entanglement profiles, bounded neutrosophic gate algebra, finite
  punctured-surface grids, partial-observer profiles, and optional neutrobit
  feature expansion.
- `core/neurobit_gate_tunnel.py` now reports the `W` gate as the local `|I>`
  basis marker, includes triplet measurement metadata, exposes a bounded
  partial-entanglement T/I/F profile, reports gate semantics and reversibility
  risk metadata, and can include finite `puncture_delta`, surface, and
  observer metadata when requested.
- `core/qnn_nucleus.py` keeps the default `state_basis="binary"` path intact
  and adds opt-in `state_basis="neutrobit"` and `observer_strength` feature
  expansion before the QNN/Torch surrogate lane.
- `api/schemas.py` and `api/main.py` expose the compatible optional fields
  `state_basis`, `puncture_delta`, and `observer_strength` for QNN smoke,
  runtime runs, and NeuroBit gate demos, plus NeuroBit-only surface dimensions.
- `core/plithogenic_logic.py` adds opt-in runtime fusion metadata for
  multi-attribute plithogenic truth variables, weights, dependence/contradiction,
  and cumulative truth before LVFM/QNN feature encoding.
- `docs/source_ledger/quantum_neutrosophic_sources.md` maps each source PDF
  to the exact simulator mechanism, accepted educational claim, and forbidden
  public claim.
- `tests/test_neutrosophic_quantum_primitives.py` and the updated NeuroBit,
  QNN, and API tests cover normalization, measurement output, finite
  puncture-grid behavior, opt-in feature expansion, and backward-compatible
  API behavior.

Source-backed topics now available for education and code reading:

- neutrobit basis `|0>`, `|1>`, and `|I>`;
- coherent versus decoherent neutrosophic state handling;
- non-projective measurement as a T/I/F distribution;
- finite punctured-wave simulation through `puncture_delta`;
- finite punctured-surface simulation for IPW/FPW-style grids;
- neutrosophic `not`, `and`, `or`, and `if_then` gate algebra;
- partial entanglement and partial observer effect represented as bounded
  T/I/F metadata.
- plithogenic runtime fusion for weighted multi-attribute event truth,
  dependence/contradiction metadata, and cumulative neutrosophic truth.

Current Mechanism Layer v2 validation:

- `neutrosophic_gate_algebra()` provides deterministic educational logic
  previews for `not`, `and`, `or`, and `if_then`;
- `punctured_surface_state()` extends finite puncture modeling from 1D waves
  to 2D surface grids;
- `observer_effect_profile()` adds an optional partial-observer T/I/F profile;
- NeuroBit gate runs now include optional gate semantics, reversibility-risk
  metadata, surface puncture metadata, and observer-effect metadata;
- the full local test suite currently passes with 117 tests, and the
  alpha-local readiness validator passes.

These additions are local educational simulation primitives only. They do not
claim a physical neutrosophic quantum computer, clinical system, security
system, production system, quantum advantage, or validated physics engine.

### Nidus Idearum II math layer

`core/nidus_idearum_math.py` adds an opt-in educational layer based on
*Nidus Idearum. Scilogs, II: de rerum consectatione*, 2nd edition. It keeps
`T/I/F` as a dynamic triplet, preserves incomplete/intersection uncertainty as
local `I_system_component`, and supports partial-membership sample means where
membership can be below, equal to, or above 1.

The layer is available through:

- `GET /fnp-qnn/nidus/status`
- `POST /fnp-qnn/nidus/triplet/profile`
- `POST /fnp-qnn/nidus/fusion/profile`
- `POST /fnp-qnn/nidus/partial-membership/mean`

The implementation report lives at
`FNP-QNN-MVP-organisation/04_implementation_planning/NIDUS_IDEARUM_II_MATH_IMPLANTATION.md`.
These endpoints are opt-in and do not change default QNN, NeuroBit, runtime,
or Panel behavior.

### Plithogenic runtime fusion layer

`core/plithogenic_logic.py` adds an opt-in runtime fusion layer based on
*Introduction to Plithogenic Logic as generalization of MultiVariate Logic*.
The simulator now has a concrete place to use plithogenic logic: Cerebrum
runtime event fusion before LVFM/QNN feature encoding.

Enable it on runtime runs with:

```json
{
  "plithogenic_enabled": true
}
```

The layer maps events to `P(V1, V2, ..., Vn)` attribute truth variables,
preserves bounded `T/I/F` triplets, applies event/source weights, surfaces
pair dependence and contradiction load, and reports cumulative neutrosophic
truth using `min(T), max(I), max(F)`. The same profile is available through:

- `POST /fnp-qnn/plithogenic/runtime/profile`

The implementation report lives at
`FNP-QNN-MVP-organisation/04_implementation_planning/PLITHOGENIC_LOGIC_RUNTIME_FUSION.md`.
This layer is disabled by default and does not change QNN, NeuroBit, Nidus,
runtime, or Panel behavior unless requested.

### Revolutionary topologies runtime layer

`core/revolutionary_topologies.py` adds an opt-in topology-style runtime layer
based on *Foundation of Revolutionary Topologies*. The simulator uses this as
the safe topological entry point: before LVFM/QNN treats runtime states as
different, it can inspect whether selected structure invariants survive local
deformation.

Enable it on runtime runs with:

```json
{
  "revolutionary_topology_enabled": true
}
```

The layer reports CT/NCT/ACT-style axiom closure, refined `T/I/F` topology
components, nested event/modality/pair metadata, NonStandard binad
neighborhood tolerance, and bounded Over/Under/Off plus multiset recurrence
signals. The same profile is available through:

- `POST /fnp-qnn/revolutionary-topology/runtime/profile`

The implementation report lives at
`FNP-QNN-MVP-organisation/04_implementation_planning/REVOLUTIONARY_TOPOLOGIES_RUNTIME_LAYER.md`.
This layer is disabled by default and does not change QNN, NeuroBit, Nidus,
Plithogenic, runtime, or Panel behavior unless requested.

### Plithogenic probability/statistics to topology wiring

`core/plithogenic_probability_statistics.py` adds a deterministic bridge based
on local source
`C:\Users\jeans\Desktop\livre pdf\PlithogenicProbabilityStatistics20.pdf`.
It qualifies plithogenic/topology runtime metadata as empirical sample,
probability family, refined `T/I/F` statistics, multi-variable to uni-variable
decision, and topology variable completion.

The bridge is automatic only when both runtime flags are enabled:

```json
{
  "plithogenic_enabled": true,
  "revolutionary_topology_enabled": true
}
```

The same combined profile is available through:

- `POST /fnp-qnn/plithogenic-topology/runtime/profile`

Plugin stabilization can be layered on top with the existing MVP5 plugin hook:

```json
{
  "plithogenic_enabled": true,
  "revolutionary_topology_enabled": true,
  "plugin_hook_enabled": true,
  "plugin_set": "mvp5"
}
```

In that mode the five selected plugins provide bounded stabilization metadata
for derived confidence/load fields only. Raw plithogenic probabilities,
topology axioms, `D_f`, `dF`, and `i_fractal` are not overwritten. CPAI
`forward_candidate` is recorded as metadata only; no Datadog write, Redis,
Docker, remote offload, or pluginpack dependency is required for defaults.

The implementation report lives at
`FNP-QNN-MVP-organisation/04_implementation_planning/PLITHOGENIC_PROBABILITY_STATISTICS_TO_TOPOLOGY_WIRING.md`.
This bridge is disabled by default and does not change QNN, NeuroBit, Nidus,
standalone Plithogenic, standalone Revolutionary Topology, runtime, or Panel
behavior unless both source layers are active.

### NeutroAlgebra runtime integrity layer

`core/neutro_algebra.py` adds an opt-in algebraic-integrity layer based on
*NeutroAlgebra is a Generalization of Partial Algebra*. This is the simulator
door for checking whether runtime transformations, plugin outputs, topology
operations, and compact QNN feature operations are inner-defined,
indeterminate, outer-defined, or axiom-breaking.

Enable it on runtime runs with:

```json
{
  "neutro_algebra_enabled": true
}
```

When enabled, runtime can include `neutro_algebra`, LVFM can include
`neutro_algebra_profile`, and QNN results can include the same bounded
integrity metadata. The profile uses A/neutroA/antiA tri-sectioning,
NeutroFunction, NeutroOperation, NeutroAxiom, and structure classification
including Partial Algebra as a NeutroAlgebra generalization.

The same flag also activates the NeutroStructure system metrics layer based on
*Structure, NeutroStructure, and AntiStructure in Science*. It adds
`structure_system_profile` under `neutro_algebra`, plus LVFM/QNN
`neutro_structure_profile` metadata with bounded `T_system`, `I_system`, and
`F_system` computed from runtime relations and attributes.

The same profile is available through:

- `POST /fnp-qnn/neutro-algebra/profile`

The implementation report lives at
`FNP-QNN-MVP-organisation/04_implementation_planning/NEUTROALGEBRA_RUNTIME_INTEGRITY_LAYER.md`.
The NeutroStructure system metrics report lives at
`FNP-QNN-MVP-organisation/04_implementation_planning/NEUTROSTRUCTURE_SYSTEM_METRICS_LAYER.md`.
This layer is disabled by default and does not overwrite plithogenic,
topology, plugin, QNN, NeuroBit, LVFM, `D_f`, `dF`, or `i_fractal` evidence.

### Math source guardrail baseline

The current source-to-function baseline and professor-thread source-of-truth
record is stored in:

- `docs/source_ledger/math_function_source_guardrail.md`
- `FNP-QNN-MVP-organisation/04_implementation_planning/MATH_SOURCE_FUNCTION_GUARDRAIL_BASELINE_2026-06-18.md`

The organization report records the correct Gmail thread context, the selected
source URLs/tomes, the exact code bindings, endpoints, tests, and Git/GitHub
commit evidence. From this baseline forward, source updates should be
append-only: add only new mathematical sources, new functions, new endpoints,
and new tests instead of repeating the complete history each time.

Nota bene: this README is intentionally serving as a maintainer trace marker
during pre-alpha. It is larger than the final public README should be. Before
soft launch / alpha, it should be condensed into a cleaner user-facing README,
while the detailed source/function registry remains in the ledger and
organization documents.

Start with:

- `EDUCATION.md`
- `ROADMAP.md`
- `DESIGN.md`
- `AGENTS.md`
- `FNP_QNN_INSTITUTIONAL_BRIEF.md`
- `SECURITY_MODEL.md`

## Known Boundaries

- Qiskit packages are optional and not required for the default runtime.
- TensorFlow is not a base runtime dependency.
- The legacy Cerebrum runtime is not imported directly.
- Legacy replay is fixture-backed unless an explicit snapshot export is provided.
- The life-science port only converts StateField-shaped payloads into simulator observations.
- Runtime inputs are size-limited and API payloads are validated through Pydantic schemas.
- The NeuroBit tunnel-noise demo is not encryption and not a security guarantee.
- CeLeBrUm/private evidence material is not part of the public demo layer.

  {{ pre-alpha educational research simulator: contributions are open through a maintainer-reviewed education pilot. Please read CONTRIBUTING.md before opening issues or pull requests. Unscoped or incomplete proposals may be closed. Student school-project proposals must use the 12-section issue format and pass safety, eligibility, and scope review before any guided implementation session. }}
