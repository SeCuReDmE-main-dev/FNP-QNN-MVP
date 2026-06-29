# Cerebrum Runtime Wiring Report

Date: 2026-06-11

## Objective

Wire the simulator to a real Cerebrum-shaped runtime contract without importing
the legacy Cerebrum runtime directly. The simulator is now the runnable layer:
it accepts interval memories, builds deterministic crossmodal pairs, converts
those pairs into the existing feature bundle, and sends the result through the
QNN nucleus or torch fallback.

## What Changed

- Added `core/cerebrum_runtime_bridge.py`.
  - Defines `CerebrumMemoryEvent`, `CrossModalPair`,
    `CerebrumRuntimeState`, and `CerebrumRuntimeBridge`.
  - Accepts `hearing`, `vision`, `language`, `audio`, `video`, `text`, and
    `stimuli` records.
  - Normalizes interval times to a local zero-based runtime window.
  - Generates overlap-derived pairs equivalent to the useful Cerebrum mapper
    directions: `H2V`, `V2H`, `H2L`, `L2H`, `V2L`, `L2V`.
  - Keeps legacy Cerebrum optional dependencies isolated and reported by
    status instead of required at import time.

- Updated `core/cerebrum_adapter.py`.
  - Existing flat observation input still works.
  - Interval-shaped records with `starting_time`, `ending_time`,
    `payload_ref`, and provenance-compatible fields now coerce into
    `CrossModalEvent`.

- Added `core/life_science_port.py`.
  - Provides an opt-in `LifeScienceObservationPort`.
  - Converts FFED/LVFM `StateField`-shaped payloads into simulator
    observations without requiring R, FFED-RNASeq, or any plugin runtime.
  - This is dormant by default.

- Updated `api/main.py`.
  - Added `GET /cerebrum/runtime/status`.
  - Added `POST /cerebrum/runtime/ingest`.
  - Added `POST /cerebrum/runtime/pairs`.
  - Added `POST /cerebrum/runtime/run`.
  - Added command-handler support for:
    - `cerebrum-runtime-status`
    - `cerebrum-runtime-ingest`
    - `cerebrum-runtime-pairs`
    - `cerebrum-runtime-run`

- Added `examples/cerebrum_runtime_demo.py`.
  - Runs the full bridge without starting FastAPI.
  - Demonstrates hearing, vision, language, and stimuli interval memories.

- Added `examples/cerebrum_runtime_legacy_demo.py` and the versioned
  `examples/legacy_cerebrum_snapshot.json` fixture.
  - Exercises the legacy Cerebrum-compatible path without a live RethinkDB
    export.
  - Shows that the simulator can replay a snapshot-shaped legacy payload
    through the bridge and QNN path.

- Added `tests/test_cerebrum_runtime_bridge.py`.
  - Covers interval normalization, invalid modality fallback, H/V/L pair
    generation, empty runtime state safety, full QNN runtime execution,
    dormant life-science conversion, runtime API endpoints, the legacy demo
    endpoint, and the versioned legacy fixture.

## Current Runtime Contract

Input can be provided as:

- `memories`: a list of interval records.
- `events` or `observations`: compatible aliases.
- grouped collections such as `hearing_memory`, `vision_memory`,
  `language_memory`, `audio`, `video`, `text`, or `stimuli`.
- `statefield`: an optional FFED/LVFM-shaped payload with `mu`, `nu`, and `pi`.

Each normalized runtime event contains:

- `modality`
- `starting_time`
- `ending_time`
- `duration`
- `value`
- `source`
- `label`
- `payload_ref`
- `provenance`

Each crossmodal pair contains:

- `timestamp1`
- `timestamp2`
- `direction`
- `source_modality`
- `target_modality`
- `overlap_score`

The full runtime run returns:

- normalized events
- crossmodal pairs
- QNN-ready observations
- feature bundle summary
- feature vector
- QNN result
- benchmark matrix
- warnings

## Design Decisions

- The old Cerebrum code is not imported into FastAPI. This avoids requiring
  Python 2, RethinkDB, PyAudio, OpenCV GUI windows, or HPELM for the simulator
  to boot.
- The bridge copies the deterministic crossmodal idea that matters for this
  pass: overlap between memory intervals.
- The simulator remains runnable when Qiskit is unavailable by using the
  existing torch surrogate path.
- FFED-RNASeq remains outside the simulator runtime. Its future integration
  point is the `StateField`-shaped life-science port.
- Public wording stays research-oriented and makes no clinical claim.

## Validation

Commands run from:

`[local maintainer path redacted]`

Python unit/API tests:

```text
python -m unittest discover -s tests -p "test_*.py"
Ran 20 tests in 7.951s
OK
```

Runtime demo:

```text
python examples/cerebrum_runtime_demo.py
events: 4
pairs: 6
feature_dimension: 31
qnn_backend: torch_surrogate
warnings: []
```

Legacy runtime demo:

```text
python examples/cerebrum_runtime_legacy_demo.py
events: 3
pairs: 6
feature_dimension: 31
qnn_backend: torch_surrogate
warnings: []
```

Known validation note:

- `Rscript` is not available in this shell, so FFED-RNASeq R tests were not
  rerun here.
- Qiskit packages are not active in this runtime; the verified path is the
  torch surrogate fallback.
- The legacy Cerebrum bridge is proven against a versioned snapshot fixture in
  `examples/`, not against a live historical Cerebrum database export.

## Result

The simulator is no longer only referencing Cerebrum conceptually. It now has a
real runtime wiring layer for Cerebrum-shaped memories and crossmodal mappings,
with API, tests, command handling, and a local demo.
