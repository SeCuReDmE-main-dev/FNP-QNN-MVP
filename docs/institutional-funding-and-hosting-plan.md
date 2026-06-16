# Institutional Funding, Hosting, and FNP-QNN-to-MVP Transfer Plan

## Purpose

This report turns the current FNP-QNN / CeLeBrUm direction into a concrete, public-safe plan for educational open source funding, institutional hosting, university/CCTT outreach, infrastructure readiness, and source-to-MVP migration.

It is intended for maintainers and coding agents preparing the project for:

```text
- school or university funding conversations
- Quebec / Canada educational technology support
- open source support programs
- university lab or CCTT hosting discussions
- supervised access to compute resources
- MVP-hardening funding requests
- disciplined migration from the private/full FNP-QNN project into the public MVP
```

This is not a clinical, diagnostic, therapeutic, safety-critical, emergency, or production-public plan.

---

## Executive Diagnosis

FNP-QNN should not be presented as a finished commercial product or medical system.

The strongest institutional framing is:

```text
FNP-QNN is an educational open source local research simulator for visualizing and validating memory-event-to-network pipelines.
```

The strongest future-facing frame is:

```text
FNP-QNN Network Designer is a planned visual workflow layer for neural, QNN, spiderweb, memory-graph, crossmodal, logic, and custom network experiments.
```

CeLeBrUm must be framed separately:

```text
CeLeBrUm is a private, local evidence/memory server for citation-backed project memory and operator support. It is not the public demo layer.
```

The immediate goal is not to ask institutions to adopt the whole research universe at once. The goal is to package a clean, reproducible, public-safe MVP that a professor, lab, CCTT, or school partner can understand, host, and evaluate.

---

## Public-Safe Project Split

### Public-safe layer

```text
FNP-QNN MVP repository
Panel dashboard
README / EDUCATION / ROADMAP / CONTRIBUTING
unit tests and demo fixtures
public-safe reports
Network Designer skeleton
sanitized screenshots and demo video
```

### Private-lab layer

```text
CeLeBrUm model server
private local corpus
white paper / book material not yet approved for public release
private evidence memory
local .env secrets
token-gated operator API
private Datadog/E2B operational reports
```

### Institution-hosted candidate layer

```text
supervised lab server
course/lab sandbox
university or CCTT demo machine
Calcul Quebec / Alliance resource allocation
local-only CeLeBrUm deployment under supervision
public-safe FNP-QNN demo endpoint if approved
```

Never expose private CeLeBrUm material through public FNP-QNN docs, public dashboards, Vercel pages, screenshots, or funding decks.

---

## What To Present

Use this one-sentence frame:

```text
FNP-QNN is a local research control room for building, testing, and visualizing experimental memory-to-network simulation pipelines.
```

French version:

```text
FNP-QNN est un cockpit local de recherche pour construire, tester et visualiser des pipelines expérimentaux mémoire → encodage → réseau → évidence.
```

Institutional frame:

```text
The project is an educational open source simulator that helps learners inspect structured events, feature-vector encoding, deterministic neural fallback execution, optional QNN candidate lanes, graph-style workflows, and evidence outputs in a reproducible local environment.
```

---

## What Not To Present

Do not present the project as:

```text
- clinical AI
- disease prediction product
- diagnostic simulator
- medical decision support
- treatment recommendation system
- production healthcare platform
- safety-critical software
- validated quantum medical model
```

Avoid phrases like:

```text
clinically proven
medical-grade AI
disease diagnosis
patient-ready
healthcare deployment
```

---

# Required FNP-QNN Source-to-MVP Transfer Map

## Why this section exists

The full/private `FNP-QNN` repository contains broad research material. The MVP must not import the whole project. It must extract only the smallest public-safe, testable, dependency-light pieces that make the MVP feel valid and distinctive.

Agents must treat this as a migration map, not as permission to copy the full private project.

```text
Port small primitives.
Rewrite/sanitize where needed.
Add tests.
Preserve non-clinical language.
Keep optional backends optional.
```

---

## P0 — Absolute MVP inclusions from full FNP-QNN

These items should be included before the MVP is presented as a serious FNP-QNN educational simulator.

### 1. Neurobit / neutrosophic gate profile

Source reference:

```text
FNP-QNN/neural_network/quantum_gates_neutrosophic.py
```

Include as a clean MVP module:

```text
core/neurobit_gates.py
```

Required public-safe pieces:

```text
NeutrosophicGateProfile
NeutrosophicGateProfile.normalized()
NeutrosophicGateProfile.metadata
hadamard_gate_matrix()
x_gate_matrix()
y_gate_matrix()
z_gate_matrix()
w_gate_matrix()
gate_matrix()
build_neutrosophic_gate_sequence()
build_gate_parameters()
counts_to_expectation_vector()
```

Why mandatory:

```text
- gives the MVP a distinctive FNP-QNN identity
- is deterministic and bounded
- already has unit-testable math
- does not require Qiskit for core behavior
- maps cleanly into the future Network Designer as a NeurobitGate node
```

Acceptance tests:

```text
- gate matrices are unitary
- W gate matrix matches explicit definition
- profile normalization is bounded and deterministic
- same profile returns same gate sequence
- counts convert to expected vector
```

---

### 2. Optional Qiskit gate trace adapter

Source reference:

```text
apply_gate_sequence_qiskit()
```

Include only behind optional Qiskit availability.

MVP rule:

```text
Qiskit preview is visible but gated.
No base runtime dependency on Qiskit.
If Qiskit is missing, return a clear unavailable message.
```

Use it for:

```text
- QNN candidate lane preview
- Neurobit circuit trace in Panel
- future Network Designer Qiskit node
```

Do not make this path required for tests except optional/skipped tests.

---

### 3. Backend-neutral operation descriptors

Source reference:

```text
to_torchquantum_ops()
```

Include as a backend-neutral descriptor, not as a TorchQuantum dependency.

MVP use:

```text
- show the gate plan as JSON
- support future TorchQuantum lane without requiring TorchQuantum today
- teach how one profile maps to backend operations
```

Acceptance:

```text
- returns list of op descriptors
- does not import torchquantum
- works with empty wires
- deterministic for same profile
```

---

### 4. Neurobit gate demo

Source reference:

```text
FNP-QNN/tools/neurobit_gate_demo.py
```

Include as:

```text
examples/neurobit_gate_demo.py
```

MVP behavior:

```text
python examples/neurobit_gate_demo.py --truth 0.55 --indeterminacy 0.30 --falsity 0.15
```

The demo must print:

```text
- normalized profile
- deterministic gate sequence
- gate parameters
- optional Qiskit trace or clear unavailable message
- backend-neutral op descriptors
```

Do not include FFeD/quanvolution model execution in this MVP demo.

---

### 5. Deterministic experiment seed manager subset

Source reference:

```text
FNP-QNN/neural_network/random_seed_manager.py
```

Include a cleaned subset as:

```text
core/experiment_seed.py
```

Required pieces:

```text
ExperimentSeedManager(base_seed=42)
set_seed(seed)
get_seed()
get_next_seed() using golden ratio
register_experiment(name, seed=None)
get_experiment_seed(name)
get_state_summary()
```

MVP corrections:

```text
- fix typing issues before porting
- do not add secure-random claims to public MVP
- do not write state files unless explicitly requested
- connect to qnn_nucleus deterministic seeding policy later
```

Why mandatory:

```text
- funding/institutional demos need reproducibility
- Network Designer presets need stable run metadata
- educational users need to see seed provenance
```

---

### 6. Amplitude/phase feature encoder

Source reference:

```text
FNP-QNN/neural_network/quantum_neural_bridge.py
```

Only include pure feature transforms.

Include as:

```text
core/quantum_feature_transforms.py
```

Allowed functions:

```text
complex_wavefunction_to_amplitude_phase_features(wavefunction)
structure_vector_to_phi_scaled_state(vector, phi)
```

Do not include:

```text
AccessDatabaseManager
brain_structure.accdb
process_brain_structure()
update_brain_structure()
SQL queries
live database updates
```

Why mandatory:

```text
- connects the full FNP-QNN quantum-neural idea to the MVP feature-vector story
- can be tested with numpy only
- supports a future Network Designer encoder node
```

---

## P1 — Include after P0, if kept lightweight

### 7. Small mathematical primitive pack

Source reference:

```text
FNP-QNN/neural_network/ffed_framework.py
```

Do not import the whole file. Extract only tiny pure primitives into:

```text
core/fnp_math_primitives.py
```

Allowed primitives:

```text
FractalGeometry.fractal_dimension()
FibonacciDynamics.next_value()
NeutrosophicLogic.apply()
EigenvalueAnalysis.compute_eigenvalues()
EigenvalueAnalysis.is_stable()
```

Rules:

```text
- no cryptography dependency
- no h2o dependency
- no torchquantum dependency
- no PQC claims
- no encryption claims
- no matplotlib GUI behavior in base runtime
```

Use for:

```text
- educational examples
- Network Designer transform nodes
- public-safe math demos
```

---

### 8. Neurobit signal signature, not secure tunnel

Source reference:

```text
FNP-QNN/neural_network/quantum_tunnel.py
```

Do not port the class name or public claim as-is.

Do not present this as:

```text
secure quantum tunnel
secure data transmission
production encryption
```

If included, rename and restrict to:

```text
core/neurobit_signal_signature.py
```

Allowed behavior:

```text
- deterministic pseudo-counts when Qiskit unavailable
- Fibonacci/phi-inspired signal metadata
- gate trace metadata
- educational signature preview
```

Forbidden behavior in MVP:

```text
- modifying user files
- claiming encryption/security
- returning raw bytes as a security product
- production secure data transfer language
```

Use it as a Panel/Network Designer evidence artifact only.

---

## P2 — Later research lanes, not required for MVP validity

These can be documented as future lanes, but should not block the MVP.

```text
Full quanvolutional neural network execution
Full FFeD framework model
TorchQuantum execution
FossaDataManager / PostgreSQL synchronization
MindsDB/PostgreSQL integration
IIS / Apache Ignite / Mahout / Iceberg scripts
Access database bridge
quantum-circuit-designer submodule
smolagents / swarm manager references
PQC / Kyber / Dilithium claims
```

Reason:

```text
These are too dependency-heavy, not fully bounded, too hard to validate quickly, or too risky for public educational MVP claims.
```

---

## Source-to-MVP implementation order

Use this order after the current Panel/design and OSS readiness basics:

```text
1. core/neurobit_gates.py
2. tests/test_neurobit_gates.py
3. examples/neurobit_gate_demo.py
4. core/experiment_seed.py
5. tests/test_experiment_seed.py
6. core/quantum_feature_transforms.py
7. tests/test_quantum_feature_transforms.py
8. optional qiskit trace test skipped when qiskit unavailable
9. Panel Neurobit preview card
10. Network Designer NeurobitGate preset node
```

---

## Definition of “valid MVP” after transfer

The MVP can be described as a valid public-safe FNP-QNN MVP when it has:

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

## Migration safety rules

Agents must not wholesale-copy full FNP-QNN modules into the MVP.

Use this rule:

```text
copy concept → rewrite minimal primitive → add tests → document boundary → expose only if deterministic and public-safe
```

Before porting any function, check:

```text
[ ] does it require heavy optional dependencies?
[ ] does it make a clinical/security/production claim?
[ ] can it run without private data?
[ ] can it be unit tested with base dependencies?
[ ] does it fit the Panel or Network Designer story?
[ ] can it be described as educational/research-only?
```

---

## Infrastructure Request Strategy

Do not lead with:

```text
I need my own big server.
```

Lead with:

```text
I am seeking a supervised research/education environment to validate a local open source simulator, run reproducible tests, host a private evidence server safely, and prepare a visual Network Designer MVP.
```

### Phase 0 — Maintainer local machine

```text
repo cleanup
license/docs/tests
demo script
Panel screenshots
public-safe evidence report
```

### Phase 1 — small lab workstation or hosted sandbox

Recommended target:

```text
12-24 CPU cores
64-128 GB RAM
2-4 TB NVMe
NVIDIA GPU with 16-24 GB VRAM if available
Linux preferred for repeatable hosting
Docker/Podman optional
separate backup storage
```

Purpose:

```text
FNP-QNN demos
CeLeBrUm private local memory server
Panel dashboard
RAG indexing/eval
small Torch/Qiskit experiments
Network Designer development
```

### Phase 2 — academic compute / cloud allocation

```text
larger benchmarks
course notebooks
shared research sandboxes
Qiskit / quantum simulation experiments
isolated E2B-like validation
```

### Phase 3 — GPU/vLLM optional phase

Only pursue after:

```text
CeLeBrUm v1 smoke is stable
public-safe FNP-QNN demo is stable
security model is documented
PI or institutional sponsor exists
```

---

## Programs And Institutional Routes To Verify

Agents should verify current rules before applying or contacting anyone.

### JetBrains Open Source Support

Use for:

```text
development tools for open source work
```

Prerequisites:

```text
LICENSE
EDUCATION.md
CONTRIBUTING.md
ROADMAP.md
CODE_OF_CONDUCT.md
visible code/test activity
1 license if only one active human maintainer
```

### Calcul Quebec / Alliance compute resources

Use for:

```text
supervised academic compute access
Jupyter/course experiments
HPC/cloud exploration
quantum service exploration
```

Likely requirement:

```text
academic affiliation or professor / PI / supervisor
```

### Mitacs-style project

Use for:

```text
4-6 month applied research internship or MVP hardening project
```

Likely requirement:

```text
academic supervisor
partner organization
student/intern role
clear milestones
budget
```

### CCTT / college applied research route

Use for:

```text
educational technology prototype
applied research collaboration
technical validation
course/lab integration
```

Good angle:

```text
visual simulator for teaching reproducible AI/QNN/network workflows
```

### University professor / lab route

Use for:

```text
PI sponsorship
server hosting conversation
research ethics/security supervision
course/lab adoption
compute allocation support
```

Good angle:

```text
open source research software engineering + local reproducible simulator + evidence dashboard
```

---

## Candidate Institutional Angles

### Computer science / software engineering

```text
research software engineering, reproducible local simulation, FastAPI/Panel testbed, graph workflow UI
```

### Education technology

```text
visual learning tool for event pipelines, encodings, neural/QNN candidates, and evidence inspection
```

### Quantum / HPC

```text
optional QNN candidate lane, deterministic fallback, future Qiskit/quantum simulation exercises
```

### CCTT / applied research

```text
open source applied prototype that needs UI hardening, reproducibility, and deployment packaging
```

### Research data / RAG / knowledge systems

```text
CeLeBrUm as a private local evidence server with source-cited project memory and strict public/private separation
```

---

## 12-Week Institutional Readiness Plan

### Weeks 1-2 — Open source readiness

```text
LICENSE
EDUCATION.md
CONTRIBUTING.md
ROADMAP.md
CODE_OF_CONDUCT.md
README contribution warning rewrite
README educational use section
```

### Weeks 3-4 — Panel and assets

```text
apply DESIGN.md rules
create panel-ready assets
refactor Panel into research control room
add boundary card
move brand/product assets below evidence
prepare clean screenshots
```

### Weeks 5-6 — tests and evidence

```text
run unit/API tests
run alpha readiness gate
create public-safe evidence report
create demo payload
create 3-minute demo script
```

### Weeks 7-8 — FNP-QNN transfer and Network Designer backend

```text
core/neurobit_gates.py
examples/neurobit_gate_demo.py
core/experiment_seed.py
core/quantum_feature_transforms.py
core/network_designer/graph.py
registry.py
presets.py
validator.py
serialization.py
spiderweb.py
executor.py
backend tests
```

### Weeks 9-10 — institutional package

```text
FNP_QNN_INSTITUTIONAL_BRIEF.md
SECURITY_MODEL.md
server requirements
architecture diagram
funding ask
public-safe demo video
```

### Weeks 11-12 — outreach

```text
identify 10 professors/labs/CCTTs
send 5 concise outreach emails
request 3 meetings
seek 1 letter of interest
identify potential PI / academic sponsor
identify best funding route
```

---

## Immediate Home Plan For Maintainer

### Step 1 — Pull and inspect

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

### Step 2 — Run current local validation

```bash
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_alpha_readiness.py
```

If dependencies are missing, capture the exact error.

### Step 3 — Start the Panel

```bash
panel serve panel_app.py --show --port 5006
```

Check whether the Panel still feels like an asset gallery or whether runtime evidence is visible early.

### Step 4 — Create OSS readiness files

```text
LICENSE
EDUCATION.md
CONTRIBUTING.md
ROADMAP.md
CODE_OF_CONDUCT.md
```

### Step 5 — Create MVP transfer skeleton

Start with:

```text
core/neurobit_gates.py
tests/test_neurobit_gates.py
examples/neurobit_gate_demo.py
```

Do not start with FFeD, quantum tunnel, databases, or heavy integrations.

### Step 6 — Prepare first institutional package

Create:

```text
FNP_QNN_INSTITUTIONAL_BRIEF.md
SECURITY_MODEL.md
```

### Step 7 — Make one code/test commit

Do not only add docs. Add one small test or code skeleton, for example:

```text
tests/test_neurobit_gates.py
tests/test_panel_app_build.py
tests/test_design_asset_references.py
core/network_designer/graph.py + tests
```

### Step 8 — Record blocker list

Create a short local note:

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

Do not commit private names or contact details unless they are public-safe.

---

## Outreach Email Draft

Subject:

```text
Educational open source simulator for visual AI/QNN network workflows
```

Body:

```text
Bonjour,

Je développe FNP-QNN, un simulateur open source alpha-local et non clinique pour visualiser des pipelines expérimentaux événements-mémoire → encodage → réseau → évidence.

Le prototype inclut une API FastAPI, un dashboard Panel local, un fallback PyTorch déterministe, des lanes QNN optionnelles, des tests et des rapports d’évidence. Je prépare aussi un Network Designer drag-and-drop pour des workflows neural, QNN, spiderweb, memory graph et custom.

Je cherche un encadrement ou une collaboration institutionnelle pour transformer ce prototype en outil éducatif/recherche reproductible, avec un environnement de test contrôlé et une stratégie de financement adaptée.

Seriez-vous ouvert à une courte rencontre de 20 minutes pour évaluer l’adéquation avec votre laboratoire/cours/centre?

Merci,
Jean-Sébastien Beaulieu
```

---

## Success Criteria

The project is ready for a first institutional conversation when:

```text
[ ] README is public-safe and educational
[ ] LICENSE exists
[ ] EDUCATION.md exists
[ ] CONTRIBUTING.md exists
[ ] ROADMAP.md exists
[ ] SECURITY_MODEL.md exists
[ ] Neurobit gate primitive is transferred and tested
[ ] Panel runs locally
[ ] tests are run or blockers documented
[ ] demo script exists
[ ] screenshots are clean
[ ] CeLeBrUm private/public boundary is explicit
[ ] funding ask is MVP hardening, not clinical rollout
```

---

## Final Recommendation

Do not pitch the full private research universe first.

Pitch this:

```text
A public-safe educational open source simulator with a local evidence server strategy, a tested Neurobit/FNP-QNN primitive, and a clear path to a visual Network Designer MVP.
```

The strongest next move is:

```text
1. clean the public MVP
2. transfer the minimal tested FNP-QNN Neurobit primitive
3. prepare the institutional package
4. secure one academic/CCTT conversation
5. use that sponsor path to pursue compute/server/funding support
```
