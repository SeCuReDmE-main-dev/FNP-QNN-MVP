# AGENTS.md

## Purpose

This file gives coding agents the working rules for the FNP-QNN repository.

Repository:

```text
SeCuReDmE-main-dev/FNP-QNN-MVP-version-disease-simulator-
```

Default branch:

```text
FNP_QNN
```

Project type:

```text
alpha-local, non-clinical, educational/research open source simulator
```

Agents must read this file before modifying code, documentation, assets, README language, reports, UI files, funding materials, or source-to-MVP transfer work.

Detailed design rules:

```text
DESIGN.md
```

Detailed institutional funding, hosting, and source-to-MVP transfer plan:

```text
docs/institutional-funding-and-hosting-plan.md
```

---

## Highest-Priority Rule

Work as a careful maintainer-safe coding agent.

Do not make broad rewrites. Do not introduce large dependencies casually. Do not copy external code or assets unless exact file license and attribution requirements are verified.

Preferred workflow:

```text
1. Inspect actual files.
2. Understand the current architecture.
3. Make the smallest coherent change.
4. Add or update tests.
5. Run or document validation.
6. Record what changed and what remains risky.
```

---

## Project Boundary

FNP-QNN is not clinical, diagnostic, therapeutic, emergency, safety-critical, or production-public software.

Allowed language:

```text
local research simulator
alpha-local
non-clinical
educational open source project
feature-vector encoding
candidate QNN lane
deterministic PyTorch fallback
local evidence dashboard
fixture-backed replay
optional backend lane
```

Forbidden or unsafe language:

```text
clinical AI
medical diagnosis
disease prediction product
treatment recommendation
safety-critical system
production healthcare platform
emergency system
medical-grade AI
clinically validated
```

Recommended boundary copy:

```text
Alpha-local research simulator. Not clinical, diagnostic, therapeutic, emergency, safety-critical, or production-public software. Results are local simulation evidence only.
```

---

## Core Agent Rules

1. Inspect actual repository files before making claims.
2. Keep changes small, reviewable, and testable.
3. Do not rewrite unrelated files.
4. Protect existing maintainer/user changes.
5. Do not use destructive Git commands unless explicitly requested.
6. Do not copy KNIME or third-party code/assets unless exact file license and attribution requirements are verified.
7. Keep public language sober, bounded, and evidence-based.
8. Preserve the non-clinical boundary in README, docs, UI, reports, examples, screenshots, and funding materials.
9. Prefer deterministic local behavior over heavyweight optional dependencies.
10. Add tests for new behavior whenever possible.
11. Run or document validation commands after changes.
12. Separate private research framing from public project claims.
13. Do not add TensorFlow, Java, Eclipse, KNIME runtime, Node/React build chains, or heavyweight UI dependencies unless explicitly approved and documented.
14. If validation cannot be run, document the exact command, exact error, environment limitation, and next validation step.
15. Never expose private CeLeBrUm corpus content, `.env` values, secrets, white paper material, or private research text in public docs or screenshots.

---

## Repository Snapshot

Expected high-level layout:

```text
api/
core/
examples/
tests/
docs/
reports/
panel_app.py
requirements.txt
pyproject.toml
README.md
DESIGN.md
AGENTS.md
```

Important current facts:

```text
- Panel is the local operator dashboard.
- Runtime bridge, adapter, and Torch surrogate fallback are the validated default path.
- Qiskit, TorchQuantum, quanvolution, R, and live legacy database replay are optional or not yet validated by the default runtime.
- Qiskit must remain optional.
- TensorFlow is not a base runtime dependency.
- Public wording must stay tied to tests, demos, reports, and explicit evidence.
```

---

## Required Validation Commands

When dependencies are available, run:

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_alpha_readiness.py
```

For demos:

```bash
python examples/cerebrum_qnn_demo.py
python examples/cerebrum_runtime_demo.py
python examples/cerebrum_runtime_legacy_demo.py
```

For the Panel:

```bash
panel serve panel_app.py --show --port 5006
```

For the API server:

```bash
uvicorn api.main:app --reload --port 8000
```

If a command cannot run, report:

```text
- exact command
- exact error
- environment-related or code-related
- next validation step
```

---

## Dependency Policy

Keep the base runtime lightweight.

Strict Python environment rule:

```text
Use the repository-local `.venv` for all installs, tests, demos, API runs, and
Panel runs. Do not install packages into the user/global Python site-packages
for this repository unless the maintainer explicitly asks for a global install.
```

Required local setup pattern:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Optional backend installs must also stay inside `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[qiskit]"
```

If a dependency was accidentally installed into global Python, stop and report
the exact package/version impact before doing more installs.

Base runtime should remain close to:

```text
numpy
torch
scikit-learn
fastapi
uvicorn
python-multipart
panel
httpx for tests
```

Optional dependencies belong in `pyproject.toml` optional groups.

Expected optional groups:

```text
qiskit
legacy-export
analysis
observability
dev
```

Do not add heavy infrastructure unless it is clearly scoped and documented.

---

## External Code / KNIME Policy

The project may implement a clean-room interface inspired by general workflow concepts:

```text
Palette
Canvas
Node
Port
Edge
Inspector
Preset
Validation
Execution
Export JSON
```

The project must not copy:

```text
KNIME source files
KNIME icons
KNIME logo
KNIME CSS
KNIME Java/Eclipse implementation
KNIME node names as branding
KNIME trademarked visual presentation
```

Use original names:

```text
FNP-QNN Network Designer
Network Designer
Spiderweb Network
Cerebrum Crossmodal Network
Torch Surrogate Network
QNN Candidate Network
```

Avoid public names:

```text
KNIME clone
KNIME workflow editor
KNIME node repository
```

---

# FNP-QNN Source-to-MVP Transfer Rules

Agents must use the detailed transfer map in:

```text
docs/institutional-funding-and-hosting-plan.md
```

The full/private `FNP-QNN` repository contains broad research material. The MVP must not import the whole project. Transfer only small, public-safe, testable primitives that make the MVP valid and distinctive.

Migration rule:

```text
copy concept → rewrite minimal primitive → add tests → document boundary → expose only if deterministic and public-safe
```

## P0 mandatory transfers

These are the high-priority items required for a valid FNP-QNN MVP.

### 1. Neurobit / neutrosophic gate profile

Source concept:

```text
FNP-QNN/neural_network/quantum_gates_neutrosophic.py
```

Target:

```text
core/neurobit_gates.py
tests/test_neurobit_gates.py
examples/neurobit_gate_demo.py
```

Include:

```text
NeutrosophicGateProfile
normalized profile metadata
H/X/Y/Z/W gate matrices
gate_matrix()
build_neutrosophic_gate_sequence()
build_gate_parameters()
counts_to_expectation_vector()
```

### 2. Optional Qiskit trace adapter

Include `apply_gate_sequence_qiskit()` behavior only behind Qiskit availability.

Rule:

```text
Qiskit visible but gated.
No base runtime dependency on Qiskit.
Missing Qiskit must return a clear unavailable message.
```

### 3. Backend-neutral operation descriptors

Include `to_torchquantum_ops()` as plain operation descriptors.

Rule:

```text
No torchquantum import required.
Use descriptors for education, JSON traces, and future backend mapping.
```

### 4. Experiment seed manager subset

Target:

```text
core/experiment_seed.py
tests/test_experiment_seed.py
```

Include only:

```text
base_seed/current_seed
set_seed()
get_seed()
golden-ratio get_next_seed()
register_experiment()
get_experiment_seed()
get_state_summary()
```

Do not add secure-random claims or file state writes unless explicitly requested.

### 5. Amplitude/phase feature encoder

Source concept:

```text
FNP-QNN/neural_network/quantum_neural_bridge.py
```

Target:

```text
core/quantum_feature_transforms.py
tests/test_quantum_feature_transforms.py
```

Include only pure transforms:

```text
complex wavefunction → amplitude/phase features
structure vector → phi-scaled complex state
```

Do not port AccessDatabaseManager, `.accdb` paths, SQL operations, or live brain-structure updates.

## P1 optional transfers

Only after P0 is stable:

```text
FractalGeometry.fractal_dimension()
FibonacciDynamics.next_value()
NeutrosophicLogic.apply()
EigenvalueAnalysis.compute_eigenvalues()
EigenvalueAnalysis.is_stable()
Neurobit signal signature as educational metadata, not secure tunnel
```

## Explicit non-transfers for MVP

Do not migrate these into the MVP now:

```text
Full FFeD framework execution
full quanvolutional neural network execution
TorchQuantum runtime dependency
FossaDataManager / PostgreSQL sync
MindsDB/PostgreSQL integration
IIS / Apache Ignite / Mahout / Iceberg / Avalanche scripts
Access database bridge
quantum-circuit-designer submodule
smolagents / swarm manager placeholders
PQC / Kyber / Dilithium claims
secure quantum tunnel claims
```

Reason:

```text
too dependency-heavy, not public-safe enough, not validated enough, or too risky for educational MVP claims
```

## Valid MVP definition after transfer

The MVP can be described as valid when it has:

```text
[ ] local runtime bridge
[ ] feature-vector encoding
[ ] deterministic Torch surrogate fallback
[ ] QNN candidate matrix
[ ] Neurobit/neutrosophic gate profile and deterministic gate sequence
[ ] optional Qiskit trace, gated by availability
[ ] experiment seed manager / run provenance
[ ] amplitude-phase feature transform
[ ] Panel dashboard showing runtime evidence and Neurobit preview
[ ] tests for every transferred primitive
[ ] examples/neurobit_gate_demo.py
[ ] no clinical/security/encryption claims
[ ] no heavy full-project dependency creep
```

---

# Panel Repair Rules

Agents working on `panel_app.py`, `assets/`, `assets/generated/`, or future UI files must read `DESIGN.md` first.

Target feeling:

```text
FNP-QNN Research Control Room
```

Panel hierarchy must prioritize:

```text
1. Runtime status
2. Payload controls
3. Action workflow
4. Latest run summary
5. Evidence tabs
6. Network Designer
7. Optional brand/gallery section
```

Recommended main order:

```python
main=[
    _compact_hero_status(),
    _operator_action_grid(),
    _latest_run_overview(),
    _evidence_tabs(),
    _collapsed_brand_assets(),
]
```

Recommended sidebar order:

```python
sidebar=[
    status_pane,
    controls,
    pn.Card(command_output, title="Command output"),
    pn.Card(_small_visual_guide(), title="Visual guide", collapsed=True),
]
```

Required action tiles:

```text
1. Encode Features
2. Run Simulation
3. QNN Benchmark
4. Legacy Fixture
5. Network Designer
6. Export Evidence
```

Recommended evidence tabs:

```text
Events
Pairs
QNN Benchmark
Network Designer
Raw JSON
```

---

# Asset Cropping, Framing, and Panel Transfer Rules

Panel code should prefer prepared `*-panel.png` assets over raw source images.

Official asset pipeline:

```text
source asset
→ cut asset
→ framed asset
→ panel-ready asset
```

Three-layer asset model:

```text
Layer 1: visible subject cut
Layer 2: visible or subtle frame/backplate
Layer 3: invisible transparent safety cut layer
```

Transparent margin rules:

```text
small tile icons: 8% to 12%
medium UI assets: 10% to 14%
large hero assets: 12% to 18%
brand gallery assets: 10% to 16%
```

Hard rule:

```text
No visible subject should touch the final PNG boundary.
```

If an asset fails the checklist in `DESIGN.md`, do not use it in `panel_app.py` yet.

---

# FNP-QNN Network Designer Plan

Goal: create a clean-room drag-and-drop network designer integrated into the Panel dashboard.

Supported network families:

```text
neural_network
quantum_qnn
spiderweb_network
memory_graph
crossmodal_graph
logic_decision_network
custom_network
```

First executable paths:

```text
TorchSurrogate neural network
Spiderweb local propagation model
```

Qiskit lanes must be visible but gated by availability.

Implementation order:

```text
1. graph.py
2. registry.py
3. presets.py
4. validator.py
5. serialization.py
6. spiderweb.py
7. executor.py
8. backend tests
9. ui/network_designer.py
10. ui/network_canvas.py
11. network_canvas.js
12. network_canvas.css
13. panel_app.py integration
14. architecture report
```

Do not start with drag-and-drop JavaScript before the graph contract exists.

---

# CeLeBrUm Integration Boundary

CeLeBrUm must be treated as a private local memory/evidence server, not as the public demo layer.

Public-safe FNP-QNN layer:

```text
FNP-QNN MVP
Panel dashboard
fixture demos
public-safe reports
Network Designer skeleton
sanitized screenshots
```

Private CeLeBrUm layer:

```text
private local corpus
white paper/book material not approved for public release
local evidence memory
.env secrets
token-gated operator API
Datadog metadata-only reports
```

Never expose private CeLeBrUm material through public FNP-QNN docs, public dashboards, Vercel pages, screenshots, or funding decks.

---

# JetBrains Open Source Support Readiness

Do these 10 actions:

```text
1. Add LICENSE at repository root, recommended Apache-2.0.
2. Add EDUCATION.md.
3. Add CONTRIBUTING.md.
4. Replace harsh README contribution warning with maintainer-guided language.
5. Add ROADMAP.md.
6. Add or strengthen at least two recent code/test commits before applying.
7. Add CODE_OF_CONDUCT.md.
8. Add Educational Open Source Use section to README.
9. Request only the number of licenses justified by visible active human contributors; use 1 if only the maintainer is active.
10. Prepare exact application answers: project name, repo URL, license URL, 1 license, non-commercial educational open source description.
```

---

# Institutional Funding and Hosting Plan

Correct institutional frame:

```text
FNP-QNN is a local research control room for building, testing, and visualizing experimental memory-to-network simulation pipelines.
```

French:

```text
FNP-QNN est un cockpit local de recherche pour construire, tester et visualiser des pipelines expérimentaux mémoire → encodage → réseau → évidence.
```

Do not pitch the full private research universe first. Pitch a public-safe educational open source simulator with a local evidence server strategy, a tested Neurobit/FNP-QNN primitive, and a clear path to a visual Network Designer MVP.

Funding should support:

```text
- Panel UI cleanup
- panel-ready asset generation
- Neurobit/FNP-QNN primitive transfer
- Network Designer v0.1
- backend graph contract and presets
- tests and validation gates
- exportable evidence reports
- reproducible demos
- documentation and educational onboarding
- supervised compute/server exploration
```

Avoid:

```text
- clinical rollout
- diagnostic validation
- production healthcare launch
```

---

## Immediate Home Plan For Maintainer

### 1. Pull and inspect

```bash
git checkout FNP_QNN
git pull
```

Check:

```text
AGENTS.md
DESIGN.md
docs/institutional-funding-and-hosting-plan.md
```

### 2. Run local validation

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_alpha_readiness.py
```

### 3. Start the Panel

```bash
panel serve panel_app.py --show --port 5006
```

### 4. Create OSS readiness files

```text
LICENSE
EDUCATION.md
CONTRIBUTING.md
ROADMAP.md
CODE_OF_CONDUCT.md
```

### 5. Create MVP transfer skeleton

Start with:

```text
core/neurobit_gates.py
tests/test_neurobit_gates.py
examples/neurobit_gate_demo.py
```

Do not start with FFeD, quantum tunnel, databases, or heavy integrations.

### 6. Prepare institutional package

Create:

```text
FNP_QNN_INSTITUTIONAL_BRIEF.md
SECURITY_MODEL.md
```

### 7. Make one code/test commit

Do not only add docs. Add one small test or code skeleton, for example:

```text
tests/test_neurobit_gates.py
tests/test_panel_app_build.py
tests/test_design_asset_references.py
core/network_designer/graph.py + tests
```

### 8. Record blocker list locally

Create a local-only note unless public-safe:

```text
BLOCKERS_LOCAL.md
```

Include:

```text
missing dependencies
tests failing
Panel visual problems
asset preparation needed
server requirement estimate
potential professor/CCTT contacts
FNP-QNN transfer blockers
```

Do not commit private names, private contacts, secrets, or non-public research text.

---

# Recommended Commit Plans

## FNP-QNN transfer work

```text
1. Add neurobit gate primitives and tests
2. Add neurobit gate demo
3. Add experiment seed manager and tests
4. Add amplitude/phase feature transforms and tests
5. Add Panel Neurobit preview
6. Add Network Designer NeurobitGate node/preset later
```

## Panel/design work

```text
1. Generate panel-ready assets
2. Refactor Panel layout
3. Add Panel construction tests
4. Update screenshots/reports
```

## Network Designer work

```text
1. Add graph models and registry
2. Add presets and validator
3. Add serialization and executors
4. Add backend tests
5. Add Panel tab
6. Add canvas assets
7. Add drag-and-drop behavior
8. Add architecture report
```

---

# Final Acceptance Rules

A task is not complete until the agent reports:

```text
- files changed
- why they changed
- validation run or why not run
- remaining risks
- next recommended action
```

For code tasks, also report:

```text
- tests added or updated
- command output summary
- whether existing behavior was preserved
```

For docs/design/funding/source-transfer tasks, also report:

```text
- public language boundary preserved
- no clinical claims added
- no copied third-party assets/code
- no private CeLeBrUm material exposed
- no heavyweight dependency creep added
```

---

# Final Direction

Correct direction:

```text
local simulator
clean Panel
prepared assets
tested Neurobit/FNP-QNN primitive
visual Network Designer
strong tests
clear open source eligibility
non-clinical public framing
private CeLeBrUm evidence boundary
institutional hosting plan
```

Wrong direction:

```text
clinical claims
messy raw asset injection
large untested rewrites
copied KNIME implementation
heavy dependency creep
closed-project language
public exposure of private CeLeBrUm material
wholesale import of full private FNP-QNN modules
```

When uncertain, make the smallest safe change and leave a clear note for the maintainer.
