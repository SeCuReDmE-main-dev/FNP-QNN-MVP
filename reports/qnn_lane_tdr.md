# QNN Lane Technical Decision Record

## Decision

- Primary lane: `Qiskit Machine Learning`
- Hybrid execution lane: `Qiskit + TorchConnector`
- Local fallback: deterministic PyTorch surrogate
- Secondary comparison lanes: `TorchQuantum` and quanvolution

## Why This Split

- `Qiskit Machine Learning` is the clearest path for an explicit, inspectable
  QNN with `EstimatorQNN` and a standard Torch bridge.
- `TorchConnector` gives a practical training path without hiding the quantum
  model behind custom glue.
- The surrogate keeps the repository runnable when the Qiskit stack is absent.
- `TorchQuantum` and quanvolution stay available as comparative baselines, not
  as core runtime dependencies.

## Acceptance Criteria

- The code imports without requiring Qiskit.
- The surrogate path runs locally and is deterministic enough for smoke tests.
- When Qiskit is present, the hybrid lane can train a small toy batch.
- The public API exposes the same contract regardless of backend availability.
- The README and report stay aligned with the actual execution path.

## Revisit Triggers

- Qiskit is installed but the hybrid lane fails to train or forward-pass on a
  small synthetic dataset.
- The Qiskit lane becomes materially slower or less stable than the surrogate
  on the same toy benchmark.
- A new optional backend proves more stable than Qiskit for this prototype and
  can still keep the explicit contract intact.
