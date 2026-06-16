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

Agents must read this file before modifying code, documentation, assets, README language, reports, UI files, or funding/institutional materials.

Detailed design rules live in:

```text
DESIGN.md
```

Detailed institutional funding and hosting plan lives in:

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

# Panel Repair Rules

Agents working on `panel_app.py`, `assets/`, `assets/generated/`, or future UI files must read `DESIGN.md` first.

Target feeling:

```text
FNP-QNN Research Control Room
```

Not:

```text
asset gallery
medical product
unfinished notebook
random demo board
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

Do not place shirt/mug product assets in the default sidebar.

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

Naming:

```text
*-cut.png
*-framed.png
*-panel.png
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

Panel-ready exports must look centered at:

```text
64px
96px
150px
220px
```

Asset transfer checklist:

```text
[ ] subject is cleanly cut
[ ] no dirty borders
[ ] subject does not touch final boundary
[ ] transparent safety margin exists
[ ] optical centering is corrected
[ ] frame/backplate is coherent with asset family
[ ] readable at 64px to 96px
[ ] readable on light background
[ ] readable on navy/dark background
[ ] filename uses clean panel-ready naming
```

If any item fails, do not use the asset in `panel_app.py` yet.

Priority assets for recut/framing:

```text
1. logo1.png
2. mascoote qbit.png
3. qbits stancil.png
4. vector-01-brain-network.png
5. vector-02-orbit-head.png
6. vector-03-circuit-brain.png
7. vector-04-wave-brain.png
8. vector-05-cube-research.png
9. mural-ui-thumb.png
10. qbit-stencil-avatar-strip.png
11. atom-back-logo-dark.png
```

Product assets are secondary and belong below the operational workflow or inside a collapsed brand section.

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

Recommended file layout:

```text
core/network_designer/
  __init__.py
  graph.py
  registry.py
  presets.py
  validator.py
  serialization.py
  executor.py
  spiderweb.py

ui/
  __init__.py
  network_designer.py
  network_canvas.py

assets/network_designer/
  network_canvas.js
  network_canvas.css

tests/
  test_network_designer_graph.py
  test_network_designer_registry.py
  test_network_designer_presets.py
  test_network_designer_validator.py
  test_network_designer_serialization.py
  test_network_designer_executor.py
  test_spiderweb_network.py

reports/
  fnp_network_designer_architecture.md
```

Core model:

```text
DesignerPort(id, label, kind, data_type)
DesignerNode(id, type, category, label, x, y, config, inputs, outputs)
DesignerEdge(id, source_node, source_port, target_node, target_port)
DesignerGraph(graph_id, name, graph_type, version, nodes, edges, metadata, training)
```

Required presets:

```text
1. Torch Surrogate Neural Network
2. Qiskit Estimator QNN
3. Spiderweb Memory Network
4. Cerebrum Crossmodal Network
5. Blank Custom Network
```

Minimum drag-and-drop behavior:

```text
- user can drag node from palette to canvas
- user can move node on canvas
- selected node is highlighted
- inspector updates when node is selected
- edges redraw when nodes move
- graph JSON updates after moves
```

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

Institutional-host candidate layer:

```text
supervised lab server
course/lab sandbox
university or CCTT demo machine
academic compute allocation
```

Never expose private CeLeBrUm material through public FNP-QNN docs, public dashboards, Vercel pages, screenshots, or funding decks.

---

# JetBrains Open Source Support Readiness

Goal: make the repo clearly eligible as an educational, non-commercial, open source project.

Do these 10 actions:

```text
1. Add LICENSE at repository root, recommended Apache-2.0.
2. Add EDUCATION.md with learning goals, audience, concepts taught, demos, tests, boundary, learning path.
3. Add CONTRIBUTING.md inviting small guided docs/test/repro/demo contributions.
4. Replace harsh README contribution warning with maintainer-guided language.
5. Add ROADMAP.md with Panel cleanup, stable demo, Network Designer contract, drag-and-drop MVP, evidence reports, optional Qiskit validation.
6. Add or strengthen at least two recent code/test commits before applying.
7. Add CODE_OF_CONDUCT.md.
8. Add Educational Open Source Use section to README.
9. Request only the number of licenses justified by visible active human contributors; use 1 if only the maintainer is active.
10. Prepare exact application answers: project name, repo URL, license URL, 1 license, non-commercial educational open source description.
```

Do not submit JetBrains application until:

```text
[ ] LICENSE exists
[ ] EDUCATION.md exists
[ ] CONTRIBUTING.md exists
[ ] README has educational open source language
[ ] README contribution warning is maintainer-guided
[ ] ROADMAP.md exists
[ ] CODE_OF_CONDUCT.md exists
[ ] at least two recent code/test commits exist after docs/assets work
[ ] tests have been run or exact limitations documented
[ ] requested license count matches visible active human contributors
```

---

# Institutional Funding and Hosting Plan

Detailed plan:

```text
docs/institutional-funding-and-hosting-plan.md
```

Correct institutional frame:

```text
FNP-QNN is a local research control room for building, testing, and visualizing experimental memory-to-network simulation pipelines.
```

French:

```text
FNP-QNN est un cockpit local de recherche pour construire, tester et visualiser des pipelines expérimentaux mémoire → encodage → réseau → évidence.
```

Do not pitch the full private research universe first. Pitch a public-safe educational open source simulator with a local evidence server strategy and a clear path to a visual Network Designer MVP.

Funding should be described as supporting:

```text
- Panel UI cleanup
- panel-ready asset generation
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

When the maintainer returns home, follow this order.

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

If dependencies are missing, capture the exact error.

### 3. Start the Panel

```bash
panel serve panel_app.py --show --port 5006
```

Check whether runtime evidence appears early or whether the Panel still feels like an asset gallery.

### 4. Create OSS readiness files

Priority:

```text
LICENSE
EDUCATION.md
CONTRIBUTING.md
ROADMAP.md
CODE_OF_CONDUCT.md
```

### 5. Prepare institutional package

Create:

```text
FNP_QNN_INSTITUTIONAL_BRIEF.md
SECURITY_MODEL.md
```

### 6. Make one code/test commit

Do not only add docs. Add one small test or code skeleton, for example:

```text
tests/test_panel_app_build.py
tests/test_design_asset_references.py
core/network_designer/graph.py + tests
```

### 7. Record blocker list

Create a local note:

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
```

Do not commit private names, private contacts, secrets, or non-public research text.

---

# Funding / Presentation Guidance

Prepare deck now, but do not pitch as market-ready until:

```text
[ ] Panel cleanup completed
[ ] demo script works in under 3 minutes
[ ] tests pass locally or known limitations are documented
[ ] screenshots are clean and non-clinical boundary is visible
[ ] Network Designer plan is documented
[ ] funding use is framed as MVP hardening, not commercial launch
```

Recommended pitch title:

```text
FNP-QNN: Local Research Control Room for Visual Network Simulation
```

Recommended subtitle:

```text
From memory-event encoding to neural/QNN candidate lanes, with a planned drag-and-drop Network Designer.
```

French:

```text
FNP-QNN : cockpit local de recherche pour simulation visuelle de réseaux
De l’encodage d’événements mémoire aux lanes neural/QNN candidates, avec un Network Designer drag-and-drop en préparation.
```

---

# Recommended Commit Plans

## Panel/design work

```text
1. Add or update DESIGN.md rules
2. Generate panel-ready assets
3. Refactor Panel layout
4. Add Panel construction tests
5. Update screenshots/reports
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

## JetBrains OSS readiness work

```text
1. LICENSE
2. EDUCATION.md
3. CONTRIBUTING.md
4. README wording update
5. ROADMAP.md
6. CODE_OF_CONDUCT.md
7. code/test commits
8. local validation
9. final README review
10. application draft
```

## Institutional package work

```text
1. docs/institutional-funding-and-hosting-plan.md
2. FNP_QNN_INSTITUTIONAL_BRIEF.md
3. SECURITY_MODEL.md
4. 3-minute demo script
5. clean screenshots
6. public-safe evidence report
7. server/compute requirement estimate
8. professor/CCTT outreach draft
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

For docs/design/funding tasks, also report:

```text
- public language boundary preserved
- no clinical claims added
- no copied third-party assets/code
- no private CeLeBrUm material exposed
```

---

# Final Direction

The repository is moving toward a funding-ready, educational open source MVP.

Correct direction:

```text
local simulator
clean Panel
prepared assets
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
```

When uncertain, make the smallest safe change and leave a clear note for the maintainer.
