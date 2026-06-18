# Contributing

FNP-QNN is a pre-alpha educational research simulator. Contributions are open,
but they are maintainer-reviewed, scope-limited, and public-safe.

This project is not clinical, diagnostic, therapeutic, emergency,
safety-critical, or production-public software.

## Contribution Model

The main contribution lane is an educational pilot.

- Small tested fixes are welcome when they preserve the alpha-local boundary.
- Large rewrites, new heavyweight dependencies, copied third-party assets/code,
  clinical claims, security claims, or production claims may be closed without
  implementation.
- Student school-project proposals are prioritized when they are complete,
  safe, and clearly educational.
- The maintainer may select one eligible grade 10/11 or equivalent pre-college
  school project per month for a guided 3-hour implementation and math teaching
  session.
- If demand becomes too high, selection may become a monthly educational
  challenge instead of an individual selection.

For minors, no private one-on-one unsupervised process is accepted. A
guardian/teacher confirmation and a short pre-session eligibility/scope check
are required before any guided session.

## Valid Issue Requirement

An issue is considered valid only when all 12 numbered sections below are
filled. Incomplete issues may be closed as `needs-complete-template`.

### 1. Title

Clear one-line title.

### 2. Project Type

Choose one:

- student school project
- bug report
- documentation improvement
- test/validation improvement
- educational feature proposal

### 3. Educational Goal

Explain what math, simulation, programming, or evidence concept this teaches.

### 4. Student / Contributor Context

For student proposals, state grade level or equivalent school level. Do not
post private identity documents, addresses, phone numbers, or school records.

### 5. Guardian / Teacher Confirmation Path

For student proposals, explain how eligibility can be confirmed safely before a
guided session. Confirmation must happen outside the public issue when it
contains private personal information.

### 6. Current Behavior

Describe what the simulator, docs, tests, or workflow currently does.

### 7. Proposed Change

Describe the smallest feature, fix, or documentation change requested.

### 8. Public-Safe Inputs And Outputs

List what data enters the simulator and what output should appear. Do not
include secrets, private documents, medical data, or personal student data.

### 9. Non-Clinical Boundary

Confirm that the proposal does not claim diagnosis, treatment, clinical
validation, emergency use, safety-critical behavior, or production readiness.

### 10. Acceptance Criteria

List the concrete conditions that make the issue done.

### 11. Validation Plan

List expected tests, commands, screenshots, or docs checks. Default validation:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\.venv\Scripts\python.exe scripts\validate_alpha_readiness.py
```

### 12. Contributor Checklist

- [ ] I filled all 12 sections.
- [ ] I searched existing issues or PRs for duplicates.
- [ ] I kept the proposal small and educational.
- [ ] I did not include secrets, private documents, or personal student data.
- [ ] I preserved the non-clinical, alpha-local project boundary.

## Pull Request Rules

Open an issue first for non-trivial work. A pull request should be small,
tested, and linked to a valid issue.

Before proposing changes, read:

- `AGENTS.md`
- `DESIGN.md`
- `EDUCATION.md`
- `ROADMAP.md`
- `SECURITY_MODEL.md`

Use the repository-local `.venv` for validation:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\.venv\Scripts\python.exe scripts\validate_alpha_readiness.py
```

