{{ attention mainteneur : le code est en phase de conception active. Les contributions doivent rester maintainer-guidees pendant que ce message reste present. Merci de discuter avant d'ouvrir de grands changements, issues, pull requests, pushes ou demandes de review. }}

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

## Architecture

```text
api/
  main.py                      # typed FastAPI surface and command allowlist
  schemas.py                   # Pydantic request contracts and validation
core/
  cerebrum_adapter.py          # flat and interval event normalization
  cerebrum_runtime_bridge.py   # Cerebrum-shaped runtime bridge and pair builder
  life_science_port.py         # dormant StateField-shaped observation adapter
  neurobit_gates.py            # public NeuroBit gate primitive contract
  neurobit_gate_tunnel.py      # NeuroBit gate + tunnel-noise demo runtime
  experiment_seed.py           # deterministic experiment seed provenance
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
- `POST /commands/{command_name}`

Compatibility endpoint:

- `POST /execute-command`

`/execute-command` is an internal compatibility shim. It does not execute shell commands. It only routes allowed simulator commands such as `phi-status`, `cerebrum-runtime-status`, `cerebrum-runtime-run`, `cerebrum-runtime-legacy-demo`, and `qnn-smoke`.

## Install

Base runtime:

```bash
pip install -r requirements.txt
```

Optional Qiskit lane:

```bash
pip install ".[qiskit]"
```

Optional legacy export utility:

```bash
pip install ".[legacy-export]"
```

## Run

Adapter/QNN smoke demo:

```bash
python examples/cerebrum_qnn_demo.py
```

Runtime bridge smoke demo:

```bash
python examples/cerebrum_runtime_demo.py
```

Legacy fixture replay:

```bash
python examples/cerebrum_runtime_legacy_demo.py
```

NeuroBit gate demo:

```bash
python examples/neurobit_gate_demo.py --truth 0.55 --indeterminacy 0.30 --falsity 0.15
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
  entanglement profiles, and optional neutrobit feature expansion.
- `core/neurobit_gate_tunnel.py` now reports the `W` gate as the local `|I>`
  basis marker, includes triplet measurement metadata, exposes a bounded
  partial-entanglement T/I/F profile, and can include finite
  `puncture_delta` metadata when requested.
- `core/qnn_nucleus.py` keeps the default `state_basis="binary"` path intact
  and adds opt-in `state_basis="neutrobit"` feature expansion before the
  QNN/Torch surrogate lane.
- `api/schemas.py` and `api/main.py` expose the compatible optional fields
  `state_basis` and `puncture_delta` for QNN smoke, runtime runs, and
  NeuroBit gate demos.
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
- partial entanglement represented as bounded T/I/F metadata.

These additions are local educational simulation primitives only. They do not
claim a physical neutrosophic quantum computer, clinical system, security
system, production system, quantum advantage, or validated physics engine.

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
