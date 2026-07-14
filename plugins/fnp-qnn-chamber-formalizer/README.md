# FNP-QNN Chamber Formalizer

This local Codex plugin turns a chamber idea into the fixed ten-carrier
vocabulary used by the FNP-QNN Chamber Lab. It delegates semantic
formalization to QuaNThoR's native `POST /chamber/formalize` endpoint.

It does not create a scene, infer numerical values, or grant admission.
Only Synthia may admit the complete packet before FNP-QNN renders a chamber.

Required carrier names:

`I_source`, `I_flavor`, `I_mass`, `I_mix`, `I_phase`, `I_medium`,
`I_interaction`, `I_secondary`, `I_detector`, `I_uncertainty`.

The hierarchy remains `I -> I_system^S -> D_f -> dF -> i_fractal`.
