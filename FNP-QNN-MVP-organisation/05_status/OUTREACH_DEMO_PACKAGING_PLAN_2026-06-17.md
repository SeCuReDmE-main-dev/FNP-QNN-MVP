# FNP-QNN Outreach and Demo Packaging Plan — 2026-06-17

## Objective
Create a repeatable, public-safe evidence package for AGENTS mission handoff and institutional outreach without introducing heavy dependencies.

## Deliverable set

- Updated README entry points:
  - `EDUCATION.md`, `ROADMAP.md`, `SECURITY_MODEL.md`, `FNP_QNN_INSTITUTIONAL_BRIEF.md`, `AGENTS.md`
- Panel endpoint evidence:
  - command: `curl http://127.0.0.1:<port>/panel_app` -> `200`
  - command: `curl http://127.0.0.1:<port>/` -> `302`
- Smoke artifacts:
  - validation logs from:
    - `python -m unittest discover -s tests -p "test_*.py"`
    - `python scripts/validate_alpha_readiness.py`
    - `python -m py_compile panel_app.py ui/network_designer.py ui/network_canvas.py`
    - `python -m compileall api core examples tests scripts`
- Optional browser capture checklist:
  - run only in an environment with a local browser tool:
    - take screenshot(s) of the panel control-room landing and network-designer tab
    - export raw HTML snapshot (if available) for evidence record

## Evidence bundle structure (public-safe)

1. `reports/mission_smoke_<YYYYMMDD>.md`
   - include command output and timestamps.
2. `docs/outreach/` (new)
   - `README_EVIDENCE.md`
   - screenshot placeholders names

## Guardrails

- No secrets, no private CeLeBrUm corpus.
- Keep non-clinical, non-diagnostic boundary language.
- Never claim Qiskit execution except as optional placeholder when absent.

## Timestamped completion marker

- [x] This evidence packaging plan was formalized at `2026-06-17T10:55:00-04:00`.
