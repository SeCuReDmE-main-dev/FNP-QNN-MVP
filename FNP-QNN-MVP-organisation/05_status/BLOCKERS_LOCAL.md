# Blockers Local — 2026-06-16T17:26:51-04:00

Repository: `C:\Users\jeans\Desktop\Case study\modele\simulateur de bacterie\FNP-QNN-MVP-version-desise-simulator-`

## Current blockers (maintainer-safe, non-blocking to project continuity)

- Full `panel_app.py` redesign to final `DESIGN.md` control-room hierarchy is complete; the remaining UI follow-up is capture/visual verification only.
- Front-end Network Designer stack (`ui/network_designer.py`, `ui/network_canvas.py`, `network_canvas.js`, `network_canvas.css`) is completed for drag-and-drop bootstrap and palette-driven node rendering; remaining follow-up is optional visual capture.
- No dedicated `*-panel.png` asset review/production workflow has been fully formalized.
- Outreach/demo packaging artifacts (clean screenshot capture bundle, institutional package script, public-safe run demo docs) remain pending.

## Public-safety constraints to preserve

- Keep boundary language non-clinical / non-diagnostic / non-production-public.
- Keep Qiskit optional and gated.
- Do not add heavy dependencies casually.
- Do not include private CeLeBrUm content in public artifacts.

## Immediate next actions

- Complete UI/Panel sequencing from `panel_app.py` layout → Network Designer front-end hooks.
- Finalize and document panel-ready asset set for visible operators.
- Update mission progress log with every completed task + timestamp.
