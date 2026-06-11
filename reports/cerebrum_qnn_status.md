# Cerebrum as Cognitive Layer, QNN as Testable Core

## Objective
Turn crossmodal perception events into deterministic features, then evaluate a
QNN nucleus against a local surrogate while keeping the repository runnable in
its current environment.

## What Was Implemented

- `core/cerebrum_adapter.py`
  - Converts `audio`, `video`, `text`, and `stimuli` observations into ordered
    crossmodal events.
  - Builds a fixed feature bundle with modality counts, means, standard
    deviations, transition matrix, recency weighting, and temporal span.
  - Produces a fixed-length vector suitable for QNN or classical models.
- `core/qnn_nucleus.py`
  - Defines an explicit candidate matrix for:
    - Qiskit Estimator QNN
    - Qiskit + TorchConnector hybrid QNN
    - TorchQuantum
    - Quanvolution baseline
    - Torch surrogate fallback
  - Uses a deterministic PyTorch surrogate when Qiskit is not installed.
  - Exposes `benchmark()` and `fit_surrogate()` to smoke-test the pipeline.
- `api/main.py`
  - Adds `GET /cerebrum/status`
  - Adds `POST /cerebrum/encode`
  - Adds `GET /qnn/candidates`
  - Adds `POST /qnn/smoke`
  - Keeps the legacy `phi` and command routes for compatibility.
- `examples/cerebrum_qnn_demo.py`
  - Provides a direct local smoke run of the adapter and QNN nucleus.
- `tests/test_cerebrum_qnn.py`
  - Covers adapter vectorization, candidate matrix shape, surrogate smoke run,
    and benchmark enumeration.

## Current Validation

- Python compilation passed on the new modules.
- Unit tests passed: `4 tests`.
- The demo script executed successfully and produced:
  - a 31-dimensional Cerebrum feature vector
  - a candidate matrix with the explicit QNN shortlist
  - a local surrogate training result
- Local environment note:
  - `qiskit` and `qiskit-machine-learning` are not installed in this runtime.
  - The code therefore exercises the torch fallback locally.

## What This Means

- The repository now reflects the real task more honestly:
  - Cerebrum is treated as a cognitive adapter layer.
  - QNN is treated as the testable core.
  - `EbaAaZ` is not used as a runtime dependency.
- The system is now set up for a later swap to real Qiskit execution once the
  optional packages are installed.

## Remaining Gaps

- Real Qiskit execution path is not yet validated in this environment.
- `TorchQuantum` and quanvolution are represented as candidate lanes, but not
  yet executed locally.
- Any medical or life-saving interpretation must remain experimental and
  non-clinical.

## Recommended Next Step

- Install the optional Qiskit packages in the environment and rerun the same
  smoke harness so the fallback can be compared to a real QNN path.
