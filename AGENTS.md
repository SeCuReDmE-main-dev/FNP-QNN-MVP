# AGENTS.md

## Purpose

This file gives coding agents the full working rules for the FNP-QNN repository.

It consolidates the project decisions already made by the maintainer around:

```text
- alpha-local non-clinical boundaries
- maintainer-safe open source work
- Panel UI repair
- asset cropping/framing rules
- clean-room Network Designer implementation
- JetBrains Open Source Support readiness
- funding/presentation readiness
- validation commands and acceptance gates
```

Agents must read this file before modifying code, documentation, assets, README language, reports, or UI files.

---

## Repository

```text
Repository: SeCuReDmE-main-dev/FNP-QNN-MVP-version-disease-simulator-
Default branch: FNP_QNN
Project name: FNP-QNN Local Research Simulator
Project type: alpha-local, non-clinical, educational/research open source simulator
```

The project is not clinical, diagnostic, therapeutic, emergency, safety-critical, or production-public software.

---

## Highest-Priority Rule

Work as a careful maintainer-safe coding agent.

Do not make broad rewrites. Do not introduce large dependencies casually. Do not copy external code or assets unless the exact file license and attribution requirements are verified.

The preferred workflow is:

```text
1. Inspect actual files.
2. Understand the current architecture.
3. Make the smallest coherent change.
4. Add or update tests.
5. Run or document validation.
6. Record what changed.
```

---

## Core Agent Rules

1. Inspect actual repository files before making claims.
2. Keep changes small, reviewable, and testable.
3. Do not rewrite unrelated files.
4. Do not use destructive Git commands unless explicitly requested by the maintainer.
5. Protect existing user changes.
6. Do not copy KNIME or third-party code/assets unless exact file license and attribution requirements are verified.
7. Prefer local deterministic behavior over heavyweight optional dependencies.
8. Keep public language sober and evidence-based.
9. Preserve the non-clinical boundary in README, docs, UI, reports, examples, and screenshots.
10. Add tests for new behavior whenever possible.
11. Run or document validation commands after changes.
12. Keep upstream/public language maintainer-safe, not speculative.
13. Separate private research framing from public project claims.
14. If validation cannot be run, document the exact command and exact environment limitation.
15. Do not add Java/Eclipse/KNIME runtime, Node/React build chains, or heavyweight UI dependencies unless explicitly approved.

---

## Project Boundary

FNP-QNN is an alpha-local, non-clinical research simulator.

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

## Current Architecture Snapshot

Expected high-level layout:

```text
api/
  main.py
  schemas.py

core/
  cerebrum_adapter.py
  cerebrum_runtime_bridge.py
  life_science_port.py
  phi_framework.py
  qnn_nucleus.py

examples/
  cerebrum_qnn_demo.py
  cerebrum_runtime_demo.py
  cerebrum_runtime_legacy_demo.py
  legacy_unvalidated_demo.py

tests/
  test_*.py

docs/
  alpha-readiness.md

reports/
  *.md

panel_app.py
requirements.txt
pyproject.toml
README.md
DESIGN.md
AGENTS.md
```

The Panel dashboard is currently the local operator panel. It should remain lightweight and compatible with the Python-first architecture.

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

If a command cannot be run because the environment lacks dependencies, record:

```text
- exact command
- exact error
- whether failure is environment-related or code-related
- next validation step for maintainer
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

Optional dependencies belong in `pyproject.toml` under optional groups.

Expected optional groups:

```toml
[project.optional-dependencies]
qiskit = ["qiskit>=0.43.0", "qiskit-machine-learning>=0.8.0"]
legacy-export = ["rethinkdb>=2.4.10"]
analysis = ["scipy>=1.10.0", "matplotlib>=3.6.0", "pandas>=2.0.0"]
observability = ["ddtrace>=2.8.0"]
dev = ["ruff>=0.5.0", "mypy>=1.8.0", "httpx>=0.24.0"]
```

Do not add TensorFlow, Java, Eclipse, KNIME runtime, Node/React build systems, or large UI frameworks unless the maintainer explicitly approves and a decision record explains why.

---

## External Code and License Policy

## Hard rule

Do not copy code from KNIME, old forks, GitHub snippets, StackOverflow, blogs, or other projects unless the exact file license is verified and attribution requirements are implemented.

## KNIME-related decision

The project may implement a clean-room original interface inspired by general workflow concepts:

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

Internal notes may mention KNIME only as high-level design inspiration, never as copied implementation.

---

# Panel Repair and Design Rules

Agents working on `panel_app.py`, `assets/`, `assets/generated/`, or future UI files must read `DESIGN.md` first.

The current Panel exists, but the maintainer has decided it needs redesign.

## Target feeling

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

Desired qualities:

```text
clean
technical
bounded
visual but not noisy
research-forward
operator-friendly
modular
ready for network design
```

---

## Panel hierarchy decision

The Panel should prioritize:

```text
1. Runtime status
2. Payload controls
3. Action workflow
4. Latest run summary
5. Evidence tabs
6. Network Designer
7. Optional brand/gallery section
```

The Panel must not put large brand/product visuals before runtime evidence.

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

---

## Panel action tiles

The Panel should evolve from the current small action set into a workflow grid.

Required action tiles:

```text
1. Encode Features
2. Run Simulation
3. QNN Benchmark
4. Legacy Fixture
5. Network Designer
6. Export Evidence
```

Each tile should include:

```text
small prepared panel asset
short title
one-sentence function
button
```

No tile should contain long explanatory text.

---

## Panel evidence tabs

Recommended tabs:

```text
Events
Pairs
QNN Benchmark
Network Designer
Raw JSON
```

Future tabs:

```text
Graph Config
Validation
Export
Reports
```

The `Network Designer` tab must contain real functionality, not just decorative content.

---

## Panel color tokens

Use these tokens as source of truth:

```css
:root {
  --fnp-navy: #0d183d;
  --fnp-blue: #1e3aba;
  --fnp-cyan: #55d9ff;
  --fnp-green: #36837e;
  --fnp-orange: #fdaa37;
  --fnp-paper: #f2f6fa;
  --fnp-ink: #081225;
}
```

Use color as information:

```text
Blue   -> primary compute / QNN / run
Green  -> encoding / valid / memory stream
Cyan   -> signal / active / input
Orange -> quantum / warning / boundary / legacy
Navy   -> shell / anchor / serious structure
Paper  -> content canvas
```

---

# Asset Cropping, Framing, and Panel Transfer Rules

The maintainer decided that current assets are visually strong but messy for direct UI integration.

Panel code should prefer prepared `*-panel.png` assets over raw source images.

## Official pipeline

Every important visual asset should move through this pipeline:

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

Example:

```text
qbit-stencil-cut.png
qbit-stencil-framed.png
qbit-stencil-panel.png
```

A raw asset is source material. A Panel asset is a prepared UI component.

---

## Three-layer asset model

Every Panel-ready asset must have:

```text
Layer 1: visible subject cut
Layer 2: visible or subtle frame/backplate
Layer 3: invisible transparent safety cut layer
```

### Layer 1 — visible subject cut

Clean the subject:

```text
logo
mascot
qbit stencil
brain vector
orbit head
circuit brain
wave brain
cube research
future spiderweb node
```

Rules:

```text
- remove dirty background
- clean silhouette
- preserve identity
- avoid jagged/accidental edges
- do not crop into the subject
```

### Layer 2 — frame/backplate

Allowed frame families:

```text
soft rounded square
rounded rectangle
vertical lab plate
capsule badge
light card support
soft glow plate
```

### Layer 3 — invisible transparent safety layer

Transparent margin prevents:

```text
subject touching card edge
inconsistent visual weight
random crop feeling
unstable hover/click states
tight collisions with Panel containers
```

---

## Transparent safety margin rules

Recommended transparent margins:

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

---

## Optical centering rules

Center by visual weight, not just pixel geometry.

Panel-ready exports must look centered when displayed at:

```text
64px
96px
150px
220px
```

---

## Export size rules

```text
Tile icons:
  export 512x512 or 640x640
  display 64px to 96px

Hero assets:
  export 1200x900 or 1400x1000
  display 120px to 220px high

Sidebar guide assets:
  export 700x900
  display 120px to 180px high

Brand gallery assets:
  export 1200x900 minimum
  display 160px to 220px high
```

---

## Asset transfer checklist

An asset is transferable to Panel only if:

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

---

## Priority assets for recut and framing

Treat these first:

```text
1. logo1.png
2. mascoote qbit.png
3. qbits stancil.png
4. vector-01-brain-network.png
5. vector-02-orbit-head.png
6. vector-03-circuit-brain.png
7. vector-04-wave-brain.png
8. vector-05-cube-research.png
```

Then:

```text
9. mural-ui-thumb.png
10. qbit-stencil-avatar-strip.png
11. atom-back-logo-dark.png
```

Product assets are secondary:

```text
mug-blue-ui-thumb.png
shirt-green-ui-thumb.png
```

They should remain below the operational workflow or inside a collapsed brand section.

---

# FNP-QNN Network Designer Plan

## Goal

Create a clean-room drag-and-drop network designer integrated into the Panel dashboard.

The designer should support multiple network families:

```text
neural_network
quantum_qnn
spiderweb_network
memory_graph
crossmodal_graph
logic_decision_network
custom_network
```

The first fully executable paths should be:

```text
TorchSurrogate neural network
Spiderweb local propagation model
```

Qiskit lanes should be visible but gated by availability.

---

## Recommended file layout

Use this structure:

```text
core/
  network_designer/
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

assets/
  network_designer/
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

---

## Network Designer data model

### DesignerPort

```python
from dataclasses import dataclass
from typing import Literal

PortKind = Literal["input", "output"]

@dataclass(frozen=True)
class DesignerPort:
    id: str
    label: str
    kind: PortKind
    data_type: str
```

### DesignerNode

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class DesignerNode:
    id: str
    type: str
    category: str
    label: str
    x: float
    y: float
    config: Dict[str, Any] = field(default_factory=dict)
    inputs: List[DesignerPort] = field(default_factory=list)
    outputs: List[DesignerPort] = field(default_factory=list)
```

### DesignerEdge

```python
from dataclasses import dataclass

@dataclass
class DesignerEdge:
    id: str
    source_node: str
    source_port: str
    target_node: str
    target_port: str
```

### DesignerGraph

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class DesignerGraph:
    graph_id: str
    name: str
    graph_type: str
    version: str
    nodes: List[DesignerNode]
    edges: List[DesignerEdge]
    metadata: Dict[str, Any] = field(default_factory=dict)
    training: Dict[str, Any] = field(default_factory=dict)
```

---

## Node categories

Expected categories:

```text
input
encoder
neural
quantum
spiderweb
memory_graph
logic
output
custom
```

Initial node types:

```text
Input:
- CerebrumEventInput
- FeatureVectorInput
- LegacyFixtureInput
- JSONPayloadInput

Encoder:
- QuantumStyleEncoding
- CompactVector
- Normalize

Neural:
- DenseLayer
- Activation
- Dropout
- TorchSurrogate
- ProbabilityOutput
- BenchmarkOutput

Quantum / QNN:
- ZZFeatureMap
- RealAmplitudesAnsatz
- QiskitEstimatorQNN
- QiskitTorchConnector
- QuantumProbabilityOutput

Spiderweb:
- WebMemoryAnchor
- SpiderHub
- SpiderLeg
- RadialSignal
- WebTension
- SpiderThresholdGate
- SpiderReportOutput

Memory / Crossmodal:
- MemoryEvent
- TemporalOverlap
- CrossmodalPairBuilder
- LVFMGate
- RuntimeBridgeOutput
- ReportOutput
```

---

## Required presets

### Preset 1 — Torch Surrogate Neural Network

```text
CerebrumEventInput
→ QuantumStyleEncoding
→ DenseLayer
→ Activation(tanh)
→ TorchSurrogate
→ ProbabilityOutput
→ BenchmarkOutput
```

### Preset 2 — Qiskit Estimator QNN

```text
FeatureVectorInput
→ CompactVector(target_dim=4)
→ ZZFeatureMap
→ RealAmplitudesAnsatz
→ QiskitEstimatorQNN
→ QuantumProbabilityOutput
```

If Qiskit is unavailable, show:

```text
Qiskit lane unavailable in this environment.
Install with: pip install ".[qiskit]"
```

### Preset 3 — Spiderweb Memory Network

```text
WebMemoryAnchor
→ SpiderHub
→ SpiderLeg(audio)
→ SpiderLeg(video)
→ SpiderLeg(text)
→ SpiderLeg(stimuli)
→ RadialSignal
→ WebTension
→ SpiderThresholdGate
→ SpiderReportOutput
```

### Preset 4 — Cerebrum Crossmodal Network

```text
CerebrumEventInput
→ TemporalOverlap
→ CrossmodalPairBuilder
→ LVFMGate
→ RuntimeBridgeOutput
→ ReportOutput
```

### Preset 5 — Blank Custom Network

```json
{
  "graph_id": "custom_blank",
  "name": "Blank Custom Network",
  "graph_type": "custom_network",
  "version": "0.1",
  "nodes": [],
  "edges": [],
  "metadata": {
    "boundary": "alpha-local non-clinical research simulator"
  },
  "training": {}
}
```

---

## Network Designer validation rules

Implement:

```python
def validate_designer_graph(graph: DesignerGraph, available_backends: list[str]) -> dict:
    ...
```

Return:

```json
{
  "valid": true,
  "errors": [],
  "warnings": []
}
```

Structural validation:

```text
- graph_id is non-empty
- graph_type is non-empty
- node IDs are unique
- edge IDs are unique
- all node types exist in registry
- all edge source nodes exist
- all edge target nodes exist
- source ports exist on source nodes
- target ports exist on target nodes
- source port data_type is compatible with target port data_type
```

Family-specific validation:

```text
neural_network:
  - at least one input node
  - at least one neural backend or output node
  - at least one output node

quantum_qnn:
  - Qiskit nodes require available qiskit backend
  - num_qubits must be > 0
  - CompactVector is required before QiskitEstimatorQNN

spiderweb_network:
  - at least one SpiderHub
  - at least two SpiderLeg nodes
  - each SpiderLeg should be connected to the hub

memory_graph:
  - CerebrumEventInput is required
  - TemporalOverlap or CrossmodalPairBuilder is required

custom_network:
  - validate structure and ports only
```

---

## Network Designer execution mapping

Implement:

```python
def execute_designer_graph(
    graph: DesignerGraph,
    runtime_payload: dict,
    qnn_nucleus,
    cerebrum_runtime_bridge,
) -> dict:
    ...
```

Execution mapping:

```text
neural_network → qnn_nucleus.fit_surrogate(...)
quantum_qnn → gated Qiskit path
spiderweb_network → execute_spiderweb_graph(...)
memory_graph → existing runtime bridge path
crossmodal_graph → existing runtime bridge path
custom_network → validate/export only
```

For the neural MVP, execute:

```python
qnn_nucleus.fit_surrogate(
    samples=[runtime_payload.get("memories", [])],
    labels=[int(graph.training.get("label", 1))],
    max_epochs=int(graph.training.get("epochs", 12)),
    test_size=float(graph.training.get("test_size", 0.0)),
    return_bundle=True,
)
```

---

## Spiderweb execution model

Implement:

```python
def execute_spiderweb_graph(graph: DesignerGraph, runtime_payload: dict) -> dict:
    ...
```

Suggested local alpha formula:

```text
event_value = value from each memory/event
leg_signal = event_value * leg_weight
hub_signal = hub_weight * mean(leg_signal)
web_tension = variance(leg_signal)
threshold_pass = hub_signal >= threshold
```

Output:

```json
{
  "backend": "spiderweb_local",
  "hub_signal": 0.675,
  "web_tension": 0.082,
  "leg_count": 4,
  "threshold_pass": true,
  "notes": "Local alpha spiderweb propagation model; non-clinical."
}
```

No clinical claims.

---

## Network Designer UI requirements

Create:

```python
def create_network_designer_panel(
    qnn_nucleus,
    cerebrum_runtime_bridge,
) -> pn.Column:
    ...
```

Panel must include:

```text
- Preset selector
- Load preset button
- Node palette
- Canvas
- Inspector
- Validation output
- Generated JSON output
- Execution result output
- Validate button
- Run graph button
- Export JSON button
- Reset button
```

Canvas requirements:

```html
<div class="fnp-network-designer">
  <aside class="fnp-node-palette"></aside>
  <main class="fnp-canvas">
    <svg class="fnp-edge-layer"></svg>
    <div class="fnp-node-layer"></div>
  </main>
  <aside class="fnp-inspector"></aside>
</div>
```

Required JavaScript functions:

```javascript
function initFnpNetworkDesigner(rootId, initialGraph, registry) {}
function renderPalette(registry) {}
function renderCanvas(graph) {}
function renderNode(node) {}
function renderEdges(graph) {}
function selectNode(nodeId) {}
function updateInspector(nodeId) {}
function updateNodeConfig(nodeId, configPatch) {}
function moveNode(nodeId, x, y) {}
function createNode(nodeType, x, y) {}
function deleteNode(nodeId) {}
function connectPorts(sourceNode, sourcePort, targetNode, targetPort) {}
function exportGraph() {}
function importGraph(graph) {}
function loadPreset(graph) {}
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

Do not block MVP on zoom/pan, mini-map, duplicate node, or auto-layout.

---

## Network Designer implementation order

Do not start with drag-and-drop JavaScript before the graph contract exists.

Implement in this order:

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

---

# JetBrains Open Source Support Readiness

Use this section to prepare the repository for a JetBrains Open Source Support application.

The goal is to make the repository clearly eligible as an educational, non-commercial, open source project.

## 10 precise actions agents must complete

### 1. Add an explicit open source license

Create:

```text
LICENSE
```

Recommended license:

```text
Apache-2.0
```

Reason: JetBrains asks for a license URL. A public GitHub repository without a root `LICENSE` file is visible, but not clearly open source.

Acceptance check:

```text
https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP-version-disease-simulator-/blob/FNP_QNN/LICENSE
```

must resolve after the file is committed.

---

### 2. Add `EDUCATION.md`

Create:

```text
EDUCATION.md
```

Required sections:

```text
- Learning goals
- Who this project is for
- Concepts taught
- How to run local demos
- How to inspect tests
- Non-clinical boundary
- Suggested learning path
```

Example concepts:

```text
- structured memory-event pipelines
- feature-vector encoding
- deterministic PyTorch fallback design
- optional QNN candidate lanes
- FastAPI/Pydantic validation
- HoloViz Panel dashboards
- maintainer-safe open source workflows
```

---

### 3. Add `CONTRIBUTING.md`

Create:

```text
CONTRIBUTING.md
```

Required language:

```text
Small documentation, test, reproducibility, and local demo improvements are welcome.
Large architectural changes should be discussed before opening a pull request.
All contributions must preserve the non-clinical research boundary.
```

Do not make the project look closed to all contributors.

---

### 4. Replace harsh README contribution warning with maintainer-guided language

Replace hard blocking language with:

```text
This project is in alpha-local active development.
External contributions are currently maintainer-guided.
Please open a discussion before submitting large pull requests.
Small documentation, test, reproducibility, and demo improvements are welcome.
```

---

### 5. Add `ROADMAP.md`

Create:

```text
ROADMAP.md
```

Required milestones:

```text
M1: Panel cleanup and asset framing
M2: Stable local demo script
M3: Network Designer backend graph contract
M4: Drag-and-drop Network Designer MVP
M5: Exportable evidence reports
M6: Optional Qiskit validation path
```

Keep the roadmap research/education-focused, not clinical or production-focused.

---

### 6. Add or strengthen code/test commits before applying

Before submitting the JetBrains application, add at least two small code/test commits.

Good examples:

```text
- Add tests for Panel app construction
- Add tests for DESIGN.md asset reference consistency
- Add network designer graph dataclasses
- Add tests for network designer registry/presets
- Add spiderweb local propagation test skeleton
```

Avoid relying only on image, design, or README commits as proof of active development.

---

### 7. Add `CODE_OF_CONDUCT.md`

Create:

```text
CODE_OF_CONDUCT.md
```

Purpose:

```text
- signal that contributors can participate safely
- make repository mature enough for OSS support review
- support educational collaboration
```

Keep it simple.

---

### 8. Add a JetBrains-ready project description to README

Add a section:

```text
## Educational Open Source Use

FNP-QNN is an educational, non-commercial, alpha-local research simulator for learning and experimenting with structured memory-event pipelines, feature-vector encoding, deterministic neural fallback execution, optional QNN candidate lanes, and local evidence dashboards.

It is not clinical, diagnostic, therapeutic, safety-critical, emergency, or production-public software.
```

---

### 9. Request only the number of JetBrains licenses justified by visible contributors

If only one active human maintainer is visible, request:

```text
1 license
```

Do not request licenses for:

```text
- bots
- agents
- future contributors
- inactive accounts
```

---

### 10. Prepare exact JetBrains application answers

```text
Project name:
FNP-QNN Local Research Simulator

Repository URL:
https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP-version-disease-simulator-

License URL:
https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP-version-disease-simulator-/blob/FNP_QNN/LICENSE

Number of licenses:
1
```

Suggested description:

```text
FNP-QNN is an alpha-local, non-clinical open source research simulator for learning and experimenting with structured memory-event pipelines, deterministic crossmodal pair construction, feature-vector encoding, and candidate neural/QNN backend lanes.

The project demonstrates a reproducible local simulation stack using FastAPI, Pydantic validation, HoloViz Panel, PyTorch fallback execution, optional Qiskit candidate paths, unit tests, and architecture reports.

The requested JetBrains license will be used only for non-commercial open source development, testing, documentation, and maintainer-guided educational work. The project is not clinical, diagnostic, therapeutic, safety-critical, emergency, or production-public software.
```

---

## JetBrains readiness checklist

Do not submit the JetBrains application until these are true:

```text
[ ] LICENSE exists at repository root
[ ] EDUCATION.md exists
[ ] CONTRIBUTING.md exists
[ ] README has educational open source language
[ ] README contribution warning is maintainer-guided, not fully closed
[ ] ROADMAP.md exists
[ ] CODE_OF_CONDUCT.md exists
[ ] at least two recent code/test commits exist after docs/assets work
[ ] unit tests have been run locally or exact environment limitation is documented
[ ] requested license count matches visible active human contributors
```

---

# Funding and MVP Presentation Guidance

Agents preparing public presentation materials must use the correct angle.

## Correct funding angle

Present the project as:

```text
FNP-QNN is a local research control room for building, testing, and visualizing experimental memory-to-network simulation pipelines.
```

French version:

```text
FNP-QNN est un cockpit local de recherche pour construire, tester et visualiser des pipelines expérimentaux mémoire → encodage → réseau → évidence.
```

Do not present it as a clinical product.

---

## Recommended pitch title

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
```

Subtitle:

```text
De l’encodage d’événements mémoire aux lanes neural/QNN candidates, avec un Network Designer drag-and-drop en préparation.
```

---

## Presentation readiness gates

Prepare the deck now, but do not pitch it as market-ready until these are true:

```text
[ ] Panel cleanup completed
[ ] Demo script works in under 3 minutes
[ ] tests pass locally or known limitations are documented
[ ] screenshots are clean and non-clinical boundary is visible
[ ] Network Designer plan is documented
[ ] funding use is framed as MVP hardening, not commercial launch
```

---

## Funding use categories

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
```

Avoid:

```text
- clinical rollout
- diagnostic validation
- production healthcare launch
```

---

# Recommended Commit Plan for Agents

Prefer small, meaningful commits.

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

For docs/design tasks, also report:

```text
- public language boundary preserved
- no clinical claims added
- no copied third-party assets/code
```

---

# Final Agent Instruction

The repository is moving toward a funding-ready, educational open source MVP.

The correct direction is:

```text
local simulator
clean Panel
prepared assets
visual Network Designer
strong tests
clear open source eligibility
non-clinical public framing
```

The wrong direction is:

```text
clinical claims
messy raw asset injection
large untested rewrites
copied KNIME implementation
heavy dependency creep
closed-project language
```

When uncertain, make the smallest safe change and leave a clear note for the maintainer.
