# Nidus Idearum II Math Implantation

Date: 2026-06-18

Source: Florentin Smarandache, *Nidus Idearum. Scilogs, II: de rerum consectatione*, 2nd edition, https://fs.unm.edu/NidusIdearum2-ed2.pdf

Boundary: this is an alpha-local educational simulator mapping. It is not a clinical, diagnostic, therapeutic, security, production-public, or validated physical system.

## Three Lessons

1. `T/I/F` is a dynamic triplet, not a binary probability wrapper.
   - Evidence: topics 34-37 introduce `t, i, f components`, included multiple-middle, and dynamic opposition. Topic 17 models regulation, buffer, and non-regulation as a changing triple `r + b + n = 100%`.
   - Simulator mapping: `triplet_quality_profile(T, I, F)` keeps raw `T/I/F`, exposes a normalized readout separately, and returns score, accuracy, certainty, positiveness, negativeness, contradiction load, incomplete load, and overdefined load.

2. Incomplete or conflicting models must preserve indeterminacy.
   - Evidence: topics 71-72 discuss source importance and the independence of `I`. Topic 80 defines indeterminate or incomplete models where intersections may be unknown and missing information should not be forced away.
   - Simulator mapping: `source_weighted_triplet_fusion(sources)` beta-weights source triplets and preserves incomplete/intersection uncertainty as `I_system_component`.

3. Partial membership and nested structures are simulator features.
   - Evidence: topics 84-86 introduce SuperHyperAlgebra / Neutrosophic SuperHyperAlgebra, indeterminate sample size, and sample means with partially belonging individuals, including membership values below and above 1.
   - Simulator mapping: `partial_membership_mean(values, memberships)` computes a local overset/underset-style weighted mean and reports over-membership and under-membership load.

## API Surface

New opt-in endpoints:

- `GET /fnp-qnn/nidus/status`
- `POST /fnp-qnn/nidus/triplet/profile`
- `POST /fnp-qnn/nidus/fusion/profile`
- `POST /fnp-qnn/nidus/partial-membership/mean`

These endpoints do not alter default QNN, NeuroBit, runtime bridge, Panel, or command behavior.

## Implementation Mapping

- `core/nidus_idearum_math.py`
  - `triplet_quality_profile()`
  - `source_weighted_triplet_fusion()`
  - `partial_membership_mean()`
- `api/schemas.py`
  - strict Pydantic contracts for the three POST payloads
- `api/main.py`
  - bounded `/fnp-qnn/nidus/*` routes
- `tests/test_nidus_idearum_math.py`
  - primitive-level invariant tests
- `tests/test_api_qnn_smoke.py`
  - endpoint smoke coverage

## Forbidden Claims

- Do not claim a physical neutrosophic quantum computer.
- Do not claim clinical, diagnostic, therapeutic, emergency, or safety-critical behavior.
- Do not claim production readiness or public deployment readiness.
- Do not claim security, encryption, or protected transport from this math layer.
- Do not collapse `I -> I_system^S -> D_f -> dF -> i_fractal`.
- Do not treat normalized readout values as replacement probabilities for the raw dynamic triplet.

## Acceptance Criteria

- Existing default simulator outputs remain unchanged unless the new Nidus endpoints are called.
- The new primitives accept only finite numeric inputs and reject malformed lists.
- Fusion preserves local indeterminacy from incomplete or indeterminate intersections.
- Partial membership mean supports memberships below 1, equal to 1, and above 1.
- Unit tests and alpha readiness pass locally.
