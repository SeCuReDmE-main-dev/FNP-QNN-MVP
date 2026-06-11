# README Evidence Audit

Date: 2026-06-11

Repository: `SeCuReDmE-main-dev/FNP-QNN-MVP-version-disease-simulator-`

Branch: `FNP_QNN`

Audited commit before README update: `3d84ee00fb1efad951e8b30a4797fb4a6e2c102c`

README audit update commit: the commit containing this report and README update.

## Objective

Audit the simulator repository after rapid development work, identify gaps
between the README and the actual code/history, document lack-of-evidence
items, and update the README so public claims stay aligned with evidence.

## Inputs inspected

- `README.md`
- `api/main.py`
- `core/cerebrum_runtime_bridge.py`
- `core/qnn_nucleus.py`
- `tests/test_cerebrum_runtime_bridge.py`
- `reports/cerebrum_runtime_wiring_report.md`
- `reports/qnn_lane_tdr.md`
- `requirements.txt`
- `git log --since="10 hours ago"`

## Git timeline summary

- `64da885` added an initial development notice.
- `29b5ba7` added the Cerebrum adapter, QNN nucleus, API expansion, demo,
  tests, requirements updates, and first status reports.
- `cd24ce7` clarified README and QNN nucleus behavior.
- `a0bdb58` improved smoke-run behavior, Qiskit integration handling, and QNN
  tests.
- `360ba2d` added compiled Python cache files for the QNN/demo state.
- `8736d64` updated the Cerebrum/QNN status report and added the QNN lane TDR.
- `783237b` implemented the runtime bridge, life-science port, runtime API,
  runtime demo, runtime report, and runtime tests.
- `3d5fa8d` hardened runtime label handling for benchmark stability.
- `e26d0f8` added the production/instability warning to the README.
- `373cd98` updated compiled Python cache files for core modules.
- `3d84ee0` merged local and remote `FNP_QNN` branch state.

## README gaps found

The README before this audit had the correct high-level direction but did not
fully explain:

- the repository status and contribution boundary created by the warning block;
- the full runtime bridge contract;
- the command-router surface;
- the last 10-hour Git history and why the project changed quickly;
- which claims are validated versus only scaffolded;
- the lack of Qiskit runtime evidence in the current environment;
- the blocked FFED/R evidence due to missing `Rscript`;
- optional legacy dependency status;
- tracked `__pycache__` files as repository hygiene debt.

## Validation evidence

Python test command:

```text
python -m unittest discover -s tests -p "test_*.py"
Ran 14 tests in 25.349s
OK
```

Runtime demo command:

```text
python examples/cerebrum_runtime_demo.py
events: 4
pairs: 6
feature_dimension: 31
qnn_backend: torch_surrogate
warnings: []
```

Qiskit and runtime status probe:

```text
qiskit_available: False
bridge: operational
supported_modalities: audio, video, text, stimuli
supported_pair_directions: H2V, V2H, H2L, L2H, V2L, L2V
optional_dependency_available: rethinkdb=True, pyaudio=False, cv2=False, hpelm=False
qnn_backend: torch
```

FFED/R check:

```text
Rscript tests/test_lvfm_core.R
Rscript is not recognized as a cmdlet, function, script file, or executable program.
```

## Lack of evidence

- Real Qiskit execution is not proven in the current local runtime.
- `TorchQuantum` and quanvolution are candidate lanes, not validated local
  execution lanes.
- FFED-RNASeq R tests are blocked in this shell because `Rscript` is missing.
- The life-science port is an observation adapter only, not validation of a
  biological or clinical result.
- The legacy Cerebrum runtime is intentionally not imported into FastAPI and is
  not proven to run inside the simulator process.
- Optional Cerebrum-era dependencies are only partially available.
- There is no clinical validation or safety validation.

## README update applied

The README was rewritten to:

- preserve the exact warning block at the top;
- add a clear repository status section;
- document current architecture and public API surfaces;
- summarize the last 10-hour Git history;
- include a validation matrix;
- explicitly list lack-of-evidence items;
- document known debt around tracked `__pycache__`;
- keep all clinical and public-contribution claims constrained.

## Recommended next steps

1. Keep the README warning block present until the project owner explicitly
   decides the repo is ready for broader public interaction.
2. Validate Qiskit in a controlled environment with `qiskit` and
   `qiskit-machine-learning` installed.
3. Validate FFED/R in an R-enabled environment.
4. Clean tracked `__pycache__` files in a separate maintenance commit if repo
   hygiene becomes the priority.
5. Continue updating reports and README together after major runtime changes.
