---
name: chamber-formalizer
description: Formalize a FNP-QNN Chamber Lab request into the fixed ten carrier variables before Synthia admission.
---

# Chamber Formalizer

Use this plugin only to make a user's chamber intent reviewable. Preserve the
exact carrier order:

`I_source`, `I_flavor`, `I_mass`, `I_mix`, `I_phase`, `I_medium`,
`I_interaction`, `I_secondary`, `I_detector`, `I_uncertainty`.

Send the resulting wording and supplied roles/source fields to the native
QuaNThoR endpoint `POST /chamber/formalize`. Do not invent carrier values,
calculate `D_f`, `dF`, or `i_fractal`, or describe the proposal as accepted.

Synthia is the sole admission authority. If it is unavailable or rejects the
packet, show the refusal, recommend `fnp-qnn doctor --full` (or TUI
`/doctor`), and keep the chamber disabled. Codex/Gemini may only diagnose or
refine the request before a later Synthia retry.

Always retain `I -> I_system^S -> D_f -> dF -> i_fractal` without collapsing
`dF` into generic `I`.
