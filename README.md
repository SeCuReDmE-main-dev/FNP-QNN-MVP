{{ attention ne pas effacer : le code est en production et je suis loin dun alpha respecter ce message si encore present pas pret pour tout le monde tres instable je naccept aucun push pull issue durant que je concoit et craft le code sil vous plait respecter mon processus de creation merci de votre patience }}

<style>
.readme-background {
  background-image: url("https://kommodo.ai/i/rlzh6FPen2CoWAI2KKra");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  padding: 1.2rem;
  border-radius: 8px;
}

.readme-content-overlay {
  background: rgba(255, 255, 255, 0.82);
  padding: 0.75rem 1rem;
  border-radius: 4px;
}
</style>

<div class="readme-background">
<div class="readme-content-overlay">

# Cerebrum to QNN Research Prototype

This repository is a production-facing, unstable research prototype for a
Cerebrum-shaped runtime bridge, a crossmodal cognitive adapter, and a testable
quantum-neural-network nucleus.

It is not a clinical system. It does not claim therapeutic efficacy, diagnostic
performance, treatment performance, or life-saving capability.

## Repository status

- This code is in an active crafting phase and is not ready for broad public
  contribution.
- Do not open unsolicited issues, pull requests, pushes, or review requests
  while this notice remains present.
- The repository contains working local runtime surfaces, but several research
  lanes are intentionally scaffolded or dormant until stronger evidence exists.
- Public claims must stay tied to local tests, demo output, or explicit reports
  in this repository.

## What this project does

- Ingests heterogeneous observations such as `audio`, `video`, `text`, and
  `stimuli`.
- Ingests Cerebrum-style interval memories for hearing, vision, language, and
  stimuli without importing the legacy Python 2 Cerebrum runtime.
- Builds deterministic crossmodal overlap pairs such as `H2V`, `V2H`, `H2L`,
  `L2H`, `V2L`, and `L2V`.
- Normalizes events into ordered feature bundles with modality counts, means,
  standard deviations, transition structure, recency weighting, and temporal
  span.
- Sends the resulting vector into QNN candidate lanes or a deterministic PyTorch
  fallback.
- Exposes a dormant life-science observation port for future FFED/LVFM-shaped
  inputs without making FFED-RNASeq a runtime dependency.

## Current architecture

```text
core/
  cerebrum_adapter.py          # flat and interval event normalization
  cerebrum_runtime_bridge.py   # Cerebrum-shaped interval memory bridge
  life_science_port.py         # dormant FFED/LVFM StateField-shaped port
  qnn_nucleus.py               # QNN candidate matrix and torch fallback
  phi_framework.py             # legacy phi compatibility layer
api/
  main.py                      # FastAPI and command-handler surface
examples/
  cerebrum_qnn_demo.py         # adapter + QNN smoke path
  cerebrum_runtime_demo.py     # runtime bridge + QNN smoke path
tests/
  test_cerebrum_qnn.py
  test_cerebrum_runtime_bridge.py
reports/
  cerebrum_qnn_status.md
  cerebrum_runtime_wiring_report.md
  qnn_lane_tdr.md
```

## Public API contract

Core HTTP endpoints:

- `GET /health`
- `GET /cerebrum/status`
- `POST /cerebrum/encode`
- `GET /cerebrum/runtime/status`
- `POST /cerebrum/runtime/ingest`
- `POST /cerebrum/runtime/pairs`
- `POST /cerebrum/runtime/run`
- `GET /qnn/candidates`
- `POST /qnn/smoke`

Command-router prefixes:

- `phi-*`
- `cerebrum-*`
- `cerebrum-runtime-*`
- `qnn-*`
- `quantum-*`
- `neural-*`

The runtime API accepts `memories`, `events`, `observations`, grouped modality
collections, or an optional `statefield` payload. It returns normalized events,
crossmodal pairs, feature vectors, bundle summaries, warnings, QNN smoke output,
and benchmark entries where applicable.

## QNN lane decision

The current decision record is in `reports/qnn_lane_tdr.md`.

- Primary lane: `Qiskit Machine Learning`
- Hybrid lane: `Qiskit + TorchConnector`
- Secondary comparison lanes: `TorchQuantum` and quanvolution
- Verified local fallback: deterministic PyTorch surrogate

The repository imports and runs without Qiskit. If Qiskit is unavailable, the
runtime uses the PyTorch fallback and reports that status explicitly.

## Last 10-hour Git history summary

Recent work transformed the project from a broad prototype into a more explicit
runtime surface:

- `64da885` added the initial development notice.
- `29b5ba7` added the Cerebrum adapter, QNN nucleus, API expansion, demo,
  tests, requirements updates, and the first Cerebrum/QNN status reports.
- `cd24ce7` clarified the README and QNN nucleus.
- `a0bdb58` improved `smoke_run`, Qiskit integration handling, and tests.
- `360ba2d` added compiled Python cache files for the first QNN/demo state.
- `8736d64` added Qiskit lane details and `reports/qnn_lane_tdr.md`.
- `783237b` added the runtime bridge, life-science port, runtime API, runtime
  demo, runtime report, and runtime tests.
- `3d5fa8d` hardened runtime label handling for benchmark stability.
- `e26d0f8` added the production/instability warning at the top of the README.
- `373cd98` updated compiled Python cache files for core modules.
- `3d84ee0` merged the local and remote `FNP_QNN` branch state.

## Validation matrix

Verified in the current local environment:

| Check | Result | Evidence |
| --- | --- | --- |
| Python unit/API tests | Pass | `python -m unittest discover -s tests -p "test_*.py"` ran 14 tests and returned OK |
| Runtime bridge demo | Pass | `python examples/cerebrum_runtime_demo.py` returned 4 events, 6 pairs, a 31D vector, `torch_surrogate`, and no warnings |
| Qiskit lane availability | Not available locally | `QISKIT_AVAILABLE` returned `False` |
| Runtime bridge status | Operational | status reports modalities `audio`, `video`, `text`, `stimuli`; pair directions `H2V`, `V2H`, `H2L`, `L2H`, `V2L`, `L2V`; backend `torch` |
| Legacy optional dependencies | Partial | `rethinkdb=True`, `pyaudio=False`, `cv2=False`, `hpelm=False` |
| FFED-RNASeq R test | Blocked locally | `Rscript` is not recognized in this shell |

## Lack of evidence

These points are not proven by the current repo evidence and should not be
claimed as complete:

- Real Qiskit execution has not been validated in this local runtime.
- `TorchQuantum` and quanvolution are listed as candidate/comparison lanes, but
  are not locally benchmarked here.
- FFED-RNASeq R tests were not run because `Rscript` is unavailable in this
  shell.
- The life-science port only converts `StateField`-shaped payloads into
  simulator observations; it is not a scientific validation layer.
- The legacy Cerebrum runtime is not imported directly and is not proven to run
  inside this simulator process.
- There is no clinical, diagnostic, therapeutic, or safety validation.
- Optional Cerebrum-era dependencies are only partially available locally.

## Known debt

- Recent Git history contains tracked compiled Python cache files under
  `__pycache__`. They are not runtime source. Clean them in a separate
  maintenance commit if/when repository hygiene becomes the priority.
- The Qiskit path is scaffolded and guarded, but needs a dedicated environment
  with `qiskit` and `qiskit-machine-learning` installed for real execution
  evidence.
- The FFED/R lane needs an R-enabled environment before its tests can be used as
  supporting evidence.
- README and reports should remain synchronized after each major runtime
  change.

## Install

```bash
pip install -r requirements.txt
```

Optional packages for the Qiskit lane:

```bash
pip install qiskit qiskit-machine-learning
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

Unit and API tests:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

API server:

```bash
uvicorn api.main:app --reload --port 8000
```

## Reports

- `reports/cerebrum_qnn_status.md`: adapter/QNN status and local validation.
- `reports/qnn_lane_tdr.md`: QNN lane decision record.
- `reports/cerebrum_runtime_wiring_report.md`: runtime bridge wiring report.
- `reports/readme_evidence_audit_2026-06-11.md`: README and evidence audit.

## Notes

- `Cerebrum` is treated as the upstream cognitive contract. The simulator wires
  its memory and crossmodal-pair shape through a pure Python 3 runtime bridge
  instead of importing the legacy runtime directly.
- The life-science port is intentionally dormant and opt-in; FFED-RNASeq is not
  a simulator runtime dependency.
- `EbaAaZ` is lineage only and is not part of the runtime contract.

</div>
</div>
