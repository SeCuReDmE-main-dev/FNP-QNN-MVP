# Cerebrum -> QNN Research Prototype

This repository is a serious experimental workspace for a crossmodal cognitive
adapter and a testable QNN nucleus. The goal is to turn heterogeneous perception
events into deterministic features, then compare quantum and quantum-inspired
models on the same compact input representation.

It is not a clinical system.

## Current state

- `Cerebrum` is used as the architecture reference for event memory, temporal
  relations, and multimodal sequencing.
- `Qiskit Machine Learning` is the preferred QNN target when available.
- A deterministic PyTorch surrogate keeps the project runnable when the Qiskit
  stack is not installed locally.
- The API exposes crossmodal encoding and QNN smoke endpoints.
- The repo still keeps the legacy `phi` framework for compatibility, but the
  new work is centered on `cerebrum` and `qnn`.

## Project layout

```text
core/
  cerebrum_adapter.py   # crossmodal event -> feature bundle
  qnn_nucleus.py        # QNN candidate matrix + surrogate benchmark
  phi_framework.py      # legacy mathematical core kept for compatibility
api/main.py             # FastAPI surface
examples/cerebrum_qnn_demo.py
tests/test_cerebrum_qnn.py
```

## How the pipeline works

1. ingest `audio / video / text / stimuli` observations
2. normalize them into ordered crossmodal events
3. derive a fixed feature bundle with sequence and transition information
4. feed that vector into a QNN candidate or the local PyTorch surrogate
5. compare candidate readiness with the same smoke harness

## Installation

```bash
pip install -r requirements.txt
```

Optional for the real Qiskit path:

```bash
pip install qiskit qiskit-machine-learning
```

## Quick start

Run the smoke demo:

```bash
python examples/cerebrum_qnn_demo.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

Run the API:

```bash
uvicorn api.main:app --reload --port 8000
```

## API highlights

- `GET /cerebrum/status`
- `POST /cerebrum/encode`
- `GET /qnn/candidates`
- `POST /qnn/smoke`
- `GET /health`

## Notes

- The project deliberately avoids clinical claims.
- `EbaAaZ` is treated as lineage only, not as a runtime dependency.
- The Qiskit candidate matrix is explicit, but the local runtime falls back to
  the PyTorch surrogate unless the optional packages are installed.
