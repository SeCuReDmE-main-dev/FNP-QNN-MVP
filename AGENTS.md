# AGENTS.md

## Purpose

This file gives coding agents clear rules for working on the FNP-QNN repository.

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

The project is not clinical, diagnostic, therapeutic, emergency, safety-critical, or production-public software.

---

## Core Agent Rules

1. Inspect actual repository files before making claims.
2. Keep changes small, reviewable, and testable.
3. Do not rewrite unrelated files.
4. Do not copy KNIME or third-party code/assets unless exact file license and attribution requirements are verified.
5. Prefer local deterministic behavior over heavyweight optional dependencies.
6. Keep public language sober and evidence-based.
7. Preserve the non-clinical boundary in README, docs, UI, reports, and examples.
8. Add tests for new behavior whenever possible.
9. Run or document the validation commands after changes.
10. Never use destructive Git commands unless explicitly requested by the maintainer.

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

If a command cannot be run because the environment lacks dependencies, record the exact command and the exact limitation.

---

# JetBrains Open Source Support Readiness

Use this section to prepare the repository for a JetBrains Open Source Support application.

The goal is to make the repository clearly eligible as an educational, non-commercial, open source project.

## 10 precise actions agents must complete

### 1. Add an explicit open source license

Create a root-level license file:

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

It must explain the educational purpose of the project.

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

It must invite small, guided contributions while protecting the alpha state.

Required language:

```text
Small documentation, test, reproducibility, and local demo improvements are welcome.
Large architectural changes should be discussed before opening a pull request.
All contributions must preserve the non-clinical research boundary.
```

Do not make the project look closed to all contributors.

---

### 4. Replace the harsh README contribution warning with maintainer-guided language

If the README says the project is not ready for public contribution, soften it.

Replace hard blocking language with:

```text
This project is in alpha-local active development.
External contributions are currently maintainer-guided.
Please open a discussion before submitting large pull requests.
Small documentation, test, reproducibility, and demo improvements are welcome.
```

Reason: JetBrains Open Source Support is easier to justify if the project is visibly open source and contribution-aware.

---

### 5. Add a `ROADMAP.md`

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

JetBrains states that active development should be visible. Documentation-only or asset-only commits are weaker.

Before submitting the application, add at least two small code/test commits.

Good examples:

```text
- Add tests for Panel app construction
- Add tests for DESIGN.md asset reference consistency
- Add network designer graph dataclasses
- Add tests for network designer registry/presets
- Add spiderweb local propagation test skeleton
```

Avoid relying only on image, design, or README commits as proof of activity.

---

### 7. Add `CODE_OF_CONDUCT.md`

Create:

```text
CODE_OF_CONDUCT.md
```

Use a standard, concise open source code of conduct.

Purpose:

```text
- signal that contributors can participate safely
- make the repository look mature enough for OSS support review
- support educational collaboration
```

Keep it simple and do not overbuild governance.

---

### 8. Add a JetBrains-ready project description to README

Add a short section in `README.md`:

```text
## Educational Open Source Use

FNP-QNN is an educational, non-commercial, alpha-local research simulator for learning and experimenting with structured memory-event pipelines, feature-vector encoding, deterministic neural fallback execution, optional QNN candidate lanes, and local evidence dashboards.

It is not clinical, diagnostic, therapeutic, safety-critical, emergency, or production-public software.
```

Reason: reviewers should not need to infer the educational purpose.

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

If more contributors become active later, increase the request only after their code contributions are visible in GitHub history.

---

### 10. Prepare the exact JetBrains application answers

Before applying, prepare these fields:

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

## JetBrains Application Readiness Checklist

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

## Public Language Rules

Use:

```text
educational open source project
local research simulator
alpha-local
non-clinical
feature-vector encoding
candidate QNN lane
deterministic PyTorch fallback
local evidence dashboard
```

Avoid:

```text
clinical AI
medical diagnosis
disease prediction product
treatment recommendation
safety-critical system
production healthcare platform
```

---

## Final Agent Instruction

For JetBrains Open Source Support readiness, the most important blocker is the missing root `LICENSE` file.

Fix the repository in this order:

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
