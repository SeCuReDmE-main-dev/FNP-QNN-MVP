{{ attention mainteneur : le code est en phase de conception active. Les contributions doivent rester maintainer-guidees pendant que ce message reste present. Merci de discuter avant d'ouvrir de grands changements, issues, pull requests, pushes ou demandes de review. }}

# FNP-QNN Local Research Simulator

[![SPONSORED BY E2B FOR STARTUPS](https://img.shields.io/badge/SPONSORED%20BY-E2B%20FOR%20STARTUPS-ff8800?style=for-the-badge)](https://e2b.dev/startups)
[![SUPPORTED BY DATADOG FOR STARTUPS](https://img.shields.io/badge/SUPPORTED%20BY-DATADOG%20FOR%20STARTUPS-632CA6?style=for-the-badge&logo=datadog&logoColor=white)](https://www.datadoghq.com/partner/datadog-for-startups/)

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

## Evidence And Reports

- `docs/alpha-readiness.md`: alpha-local evidence matrix.
- `reports/alpha_readiness_2026-06-12.md`: current readiness report.
- `reports/qnn_lane_tdr.md`: QNN lane decision record.
- `reports/cerebrum_runtime_wiring_report.md`: runtime bridge wiring report.
- `reports/readme_evidence_audit_2026-06-11.md`: earlier README evidence audit.

## Observabilité et audit infrastructure (Datadog + E2B)

L’application intègre une **voie d’audit opérationnel optionnelle** dédiée à la vérification de l’environnement d’exécution:

- **E2B** démarre des sandboxes courtes pour des contrôles non-cliniques et non sensibles:
  - inventaire des paquets installés,
  - ouverture des ports,
  - processus actifs,
  - visibilité contrôlée des variables d’environnement,
  - permissions de fichiers sensibles.
- **Datadog** reçoit les résultats d’audit sous forme de logs structurés pour permettre un suivi centralisé sans affecter le cœur de calcul de l’app.

Dans le produit FNP-QNN, cette intégration est utilisée ainsi:

1. On lance un run d’audit via le script `scripts/e2b_datadog_audit/audit_e2b.py`.
2. Le script crée une sandbox E2B, exécute la vérification et nettoie la sandbox en fin de run.
3. Le résumé (JSON local) est produit et un log Datadog est envoyé si la clé `DATADOG_API_KEY` est présente.
4. Le monitoring peut déclencher des alertes sur `status:error service:e2b-vm-auditor`.

Chemins utiles:

- Script principal: `scripts/e2b_datadog_audit/audit_e2b.py`
- Dépendances optionnelles: `scripts/e2b_datadog_audit/requirements.txt`
- Documentation détaillée: `scripts/e2b_datadog_audit/README.md`

Métadonnées Datadog produites par exécution:

- `service`: `e2b-vm-auditor`
- `sandbox_id`: identifiant de la sandbox E2B (si disponible)
- `env`, `template_id`, `audit_status` (pass/fail)
- JSON local de synthèse (utile pour pipelines et logs internes)

Les secrets (`E2B_API_KEY`, `DATADOG_API_KEY`) sont nettoyés avant envoi au log.
Cette lane reste optionnelle, locale par défaut, et limitée aux usages de supervision interne.

## Educational Open Source Use

This project is suitable for supervised educational exploration of local
simulation pipelines, feature encoding, deterministic fallback behavior,
NeuroBit gate traces, and future visual network-design workflows.

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
