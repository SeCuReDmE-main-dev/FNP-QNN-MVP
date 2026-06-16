# Institutional Funding and Hosting Plan

## Purpose

This report turns the current FNP-QNN / CeLeBrUm direction into a concrete, public-safe plan for educational open source funding, institutional hosting, university/CCTT outreach, and infrastructure readiness.

This document is intended for maintainers and coding agents preparing the project for:

```text
- school or university funding conversations
- Quebec / Canada educational technology support
- open source support programs
- university lab or CCTT hosting discussions
- supervised access to compute resources
- MVP-hardening funding requests
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

CeLeBrUm should be framed separately:

```text
CeLeBrUm is a private, local evidence/memory server for citation-backed project memory and operator support. It is not the public demo layer.
```

The immediate goal is not to ask institutions to adopt the whole research universe at once. The goal is to package a clean, reproducible, public-safe MVP that a professor, lab, CCTT, or school partner can understand, host, and evaluate.

---

## Public-Safe Project Split

Agents must keep these layers separate.

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

Use this institutional frame:

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

## Funding Readiness Diagnosis

The project is currently suitable for:

```text
- pre-seed educational open source support
- technical mentorship
- university professor outreach
- CCTT / research-applied discussion
- JetBrains Open Source Support preparation
- institutional hosting exploration
- MVP hardening grants or small innovation support
```

The project is not yet suitable for:

```text
- clinical funding claim
- regulated health deployment
- hospital pilot
- large production infrastructure grant without a PI
- unrestricted public CeLeBrUm hosting
```

---

## Institutional Questions To Answer

Before contacting a school, lab, university, or funding body, prepare short answers to these questions.

### What is the educational value?

```text
Students and researchers can inspect a complete local pipeline from memory-like events to feature vectors, candidate network lanes, benchmarks, and evidence reports.
```

### What is the research value?

```text
The simulator provides a reproducible local testbed for comparing deterministic fallback behavior, optional QNN candidate lanes, graph workflows, and evidence capture.
```

### Why does it need hosting or better gear?

```text
The MVP needs a stable local or institutional environment for reproducible demos, longer-running tests, private evidence-server operation, controlled RAG indexing, optional Qiskit experiments, and future GPU/vLLM phases.
```

### Why is it safe to host?

```text
The public FNP-QNN demo is non-clinical and fixture-backed. CeLeBrUm is local-only, token-gated, and private by default. Public demos must use sanitized data only.
```

### What is the first deliverable?

```text
A public-safe 3-minute demo, a cleaned Panel dashboard, passing local tests, an EDUCATION.md learning path, and a short institutional brief.
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

Purpose:

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

Purpose:

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

Frame:

```text
research software engineering, reproducible local simulation, FastAPI/Panel testbed, graph workflow UI
```

### Education technology

Frame:

```text
visual learning tool for event pipelines, encodings, neural/QNN candidates, and evidence inspection
```

### Quantum / HPC

Frame:

```text
optional QNN candidate lane, deterministic fallback, future Qiskit/quantum simulation exercises
```

### CCTT / applied research

Frame:

```text
open source applied prototype that needs UI hardening, reproducibility, and deployment packaging
```

### Research data / RAG / knowledge systems

Frame:

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

### Weeks 7-8 — Network Designer backend

```text
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

When the maintainer returns home, follow this order.

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

Priority:

```text
LICENSE
EDUCATION.md
CONTRIBUTING.md
ROADMAP.md
CODE_OF_CONDUCT.md
```

### Step 5 — Prepare first institutional package

Create:

```text
FNP_QNN_INSTITUTIONAL_BRIEF.md
SECURITY_MODEL.md
```

### Step 6 — Make one code/test commit

Do not only add docs. Add one small test or code skeleton, for example:

```text
tests/test_panel_app_build.py
tests/test_design_asset_references.py
core/network_designer/graph.py + tests
```

### Step 7 — Record blocker list

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
A public-safe educational open source simulator with a local evidence server strategy and a clear path to a visual Network Designer MVP.
```

The strongest next move is:

```text
1. clean the public MVP
2. prepare the institutional package
3. secure one academic/CCTT conversation
4. use that sponsor path to pursue compute/server/funding support
```
