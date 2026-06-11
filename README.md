{{ attention ne pas effacer : le code est en production et je suis loin dun alpha respecter ce message si encore present pas pret pour tout le monde tres instable je naccept aucun push pull issue durant que je concoit et craft le code sil vous plait respecter mon processus de creation merci de votre patience }}

# Cerebrum to QNN Research Prototype

This repository is a local research prototype for a crossmodal cognitive
adapter and a testable quantum-neural-network nucleus.

It is not a clinical system. It does not claim therapeutic efficacy.

## What this project does

- Ingests heterogeneous observations such as `audio`, `video`, `text`, and
  `stimuli`.
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
  qnn_nucleus.py        # QNN candidate matrix, qiskit lane, torch fallback
  phi_framework.py      # legacy compatibility layer
api/main.py             # FastAPI surface
examples/cerebrum_qnn_demo.py
tests/test_cerebrum_qnn.py
reports/cerebrum_qnn_status.md
```

## Public contract

- `GET /cerebrum/status`
- `POST /cerebrum/encode`
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
- The smoke demo runs locally and exercises the torch fallback.
- The local environment currently does not have `qiskit` or
  `qiskit-machine-learning` installed, so the real Qiskit lane is scaffolded but
  not executed in this runtime yet.

## Notes

- `Cerebrum` is treated as the cognitive-architecture reference, not as a
  runtime dependency.
- `EbaAaZ` is lineage only and is not part of the runtime contract.
- The report source for the current implementation lives in
  `reports/cerebrum_qnn_status.md`.
