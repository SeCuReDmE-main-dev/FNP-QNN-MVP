{{ attention ne pas effacer : le code est en production et je suis loin dun alpha respecter ce message si encore present pas pret pour tout le monde tres instable je naccept aucun push pull issue durant que je concoit et craft le code sil vous plait respecter mon processus de creation merci de votre patience }}

# Cerebrum to QNN Research Prototype

This repository is a local research prototype for a Cerebrum-shaped runtime
bridge, a crossmodal cognitive adapter, and a testable quantum-neural-network
nucleus.

It is not a clinical system. It does not claim therapeutic efficacy.

## What this project does

- Ingests heterogeneous observations such as `audio`, `video`, `text`, and
  `stimuli`.
- Ingests Cerebrum-style interval memories for hearing, vision, language, and
  stimuli without importing the legacy Python 2 runtime.
- Builds deterministic crossmodal overlap pairs such as `H2V`, `V2H`, `H2L`,
  `L2H`, `V2L`, and `L2V`.
- Normalizes them into ordered crossmodal events.
- Builds a fixed feature bundle with modality counts, means, standard
  deviations, transition structure, recency weighting, and temporal span.
- Sends the resulting vector into one of several QNN lanes.
- Keeps a deterministic PyTorch fallback so the repo remains runnable when the
  optional Qiskit stack is not installed.

## Current architecture

```text
core/
  cerebrum_adapter.py   # crossmodal event normalization and feature bundle
  cerebrum_runtime_bridge.py # Cerebrum-shaped interval runtime bridge
  life_science_port.py  # dormant FFED/LVFM-shaped observation port
  qnn_nucleus.py        # QNN candidate matrix, qiskit lane, torch fallback
  phi_framework.py      # legacy compatibility layer
api/main.py             # FastAPI surface
examples/cerebrum_qnn_demo.py
examples/cerebrum_runtime_demo.py
tests/test_cerebrum_qnn.py
tests/test_cerebrum_runtime_bridge.py
reports/cerebrum_qnn_status.md
reports/cerebrum_runtime_wiring_report.md
```

## Public contract

- `GET /cerebrum/status`
- `POST /cerebrum/encode`
- `GET /cerebrum/runtime/status`
- `POST /cerebrum/runtime/ingest`
- `POST /cerebrum/runtime/pairs`
- `POST /cerebrum/runtime/run`
- `GET /qnn/candidates`
- `POST /qnn/smoke`
- `GET /health`

The API also keeps legacy `phi-` commands for compatibility, but the new work
is centered on the Cerebrum adapter and the QNN nucleus.

## QNN lanes

- Primary lane: `Qiskit Machine Learning`
- Hybrid lane: `Qiskit + TorchConnector`
- Comparison lanes: `TorchQuantum` and quanvolution
- Local fallback: deterministic PyTorch surrogate

## Install

```bash
pip install -r requirements.txt
```

Optional packages for the Qiskit lane:

```bash
pip install qiskit qiskit-machine-learning
```

## Run

Smoke demo:

```bash
python examples/cerebrum_qnn_demo.py
python examples/cerebrum_runtime_demo.py
```

Unit tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

API server:

```bash
uvicorn api.main:app --reload --port 8000
```

## Validation status

- Python compilation passes on the new modules.
- Unit tests pass locally.
- The adapter and runtime smoke demos run locally and exercise the torch
  fallback.
- The local environment currently does not have `qiskit` or
  `qiskit-machine-learning` installed, so the real Qiskit lane is scaffolded but
  not executed in this runtime yet.
- `Rscript` is not available in this shell, so FFED-RNASeq R tests must be run
  in an R-enabled environment.

## Notes

- `Cerebrum` is treated as the upstream cognitive contract. The simulator now
  wires its memory and crossmodal-pair shape through a pure Python 3 runtime
  bridge instead of importing the legacy runtime directly.
- The life-science port is intentionally dormant and opt-in; FFED-RNASeq is not
  a simulator runtime dependency.
- `EbaAaZ` is lineage only and is not part of the runtime contract.
- The report source for the current implementation lives in
  `reports/cerebrum_qnn_status.md`.
