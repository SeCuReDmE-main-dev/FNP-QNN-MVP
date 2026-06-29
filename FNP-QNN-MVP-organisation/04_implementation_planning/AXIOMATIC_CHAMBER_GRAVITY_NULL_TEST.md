# Axiomatic-Chamber Gravity Null-Test Implementation

Status: implemented on branch `experiment/axiomatic-chamber-gravity-null-test`.

## Objective

Build a source-led proof-of-principle simulator for the Vedral-inspired quantum-gravity null-test idea without claiming physical proof. The simulator isolates three roles:

- `A`: remote entangled partner.
- `B`: local target particle entangled with `A`.
- `C`: local uncorrelated probe/source near `B`, not entangled with `A-B`.

The result is a bounded experiment profile, not a theorem of nature. It measures residuals and classifies them as no detected remote influence, local coupling/shared noise, suspended, or externally validated anomaly/frustration candidate.

## Source Boundary

Primary source ledger: `docs/source_ledger/quantum_gravity_video_ledger.md`.

Verified source anchors:

- Vedral video 1 official page: "Testing Quantum Gravity & Reality with Prof. Vlatko Vedral", Quantum Foundations Podcast with Dr. Maria Violaris, published February 3, 2025.
- Vedral video 2 official page: "This Quantum Gravity Experiment Will Rewrite Physics", Quantum Foundations Podcast with Dr. Maria Violaris, published July 9, 2025.
- Oxford profile: Prof. Vlatko Vedral is listed as Professor of Quantum Information Science.
- SeQUeNCe GitHub and arXiv paper are optional export targets, not runtime dependencies.
- Local book source: `[local maintainer path redacted]`.

The local PDF confirms the chamber discipline used here:

- Chapter 5 defines `I_fractal` as admissible only through `I_system` and `Adm`; `D_f_hat` is a carrier, not universal `I`.
- Chapter 6 defines `GPCN-Set_phi` as an axiomatic chamber with domain, scale, method, membership, local fractal dimension, `I_system`, and `Adm`.
- Chapter 7 validates by testing existence, membership, boundary, scale, local dimension, fractal indeterminacy, normalization, and non-universality axioms.

## Code Anchors

- `core/axiomatic_chamber.py`: chamber context, bounds, source-role taxonomy, and admissibility rules.
- `core/gravity_null_test.py`: Bell-state reference taxonomy, deterministic seeded simulation functions, residual scoring, frustration scoring, SeQUeNCe export, Qiskit preview, E2B/Datadog review metadata, and graviton-constraint placeholder.
- `api/schemas.py`: `GravityNullTestRequest` and optional QNN smoke fields.
- `api/main.py`: `GET /fnp-qnn/gravity-null-test/status`, `POST /fnp-qnn/gravity-null-test/run`, and QNN smoke integration.
- `core/qnn_nucleus.py`: attaches gravity-null-test features and profile metadata when explicitly enabled.
- `core/network_designer/presets.py`: `gravity_null_test` Network Designer preset.

## Bell State Is Not The Chamber

The implementation now includes a specific test lane for the distinction the maintainer requested:

- `bell_state_reference_profile()` returns the Bell state reference. It is an `A-B` state/correlation profile only. It excludes `C`, `Adm`, `D_min/D_max`, chamber residuals, and graviton constraints.
- `bell_vs_gravity_chamber_taxonomy()` returns executable invariants showing that the gravity/null-test chamber is a different object. The chamber wraps the Bell input with `C`, bounds, no-signalling residuals, frustration scoring, `Adm`, telemetry, and constraint-only graviton metadata.

This matters because a Bell pair answers "are `A` and `B` correlated?" The graviton-node/null-test chamber asks "after we isolate sources in an axiomatic room, is any residual on `B` still present, and how should it be classified?" The second question uses the first object as an input, but it is not the same object.

## E2B And Datadog Review Lane

The experiment treats E2B as an optional ephemeral micro-VM reviewer and Datadog as the telemetry review surface.

Default simulator output includes an `e2b_datadog_review` profile with:

- a suggested micro-VM audit command using `scripts/e2b_datadog_audit/audit_e2b.py`;
- secret-safe readiness booleans, never raw API keys;
- Datadog metric names for `Delta_NS`, `F_chamber`, `GQ_super_equation`, local contamination, and entangled-pair resistance;
- monitor-query templates that can flag high residuals, local contamination, or reduced pair resistance.

This makes E2B and Datadog part of the scientific review loop: the micro-VM reruns the same profile independently, while Datadog makes drift, leakage, and resistance residuals visible over repeated runs.

## Penrose/Hameroff Relationship

This null-test is a sister lane to the existing Penrose/Hameroff and Hydra-EM-GPCN work:

- `core/penrose_hameroff_math.py` already implements bounded objective-reduction timing, spin-network admissibility, twistor/nonlocality metadata, and microtubule signal metadata.
- `core/hydra_em_gpcn_math.py` already implements a `GPCN-Set_phi` axiomatic chamber for microtubule-like proxy objects, quasicrystal-style neighborhoods, cubic neutrosophic `T/I/F`, and computational damping sweeps.

The relation is methodological, not proof-based. The gravity null-test asks whether an entangled-pair residual survives source isolation. The Hydra microtubule lane asks whether proxy microtubule states communicate, decohere, suspend, or reject inside `GPCN-Set_phi`. Both enforce the same discipline:

`measure -> normalize -> classify source -> apply Adm -> admit/suspend/reject`.

## Acceptance Criteria

- Null case: `Delta_NS` below threshold, classification `no_detected_remote_influence`.
- Leakage case: classification `local_coupling_or_shared_noise`.
- Frustrated case: high `F_chamber`, no physical proof claim.
- Invalid bounds: rejected.
- Graviton lane: `constraint_profile_pending_external_data` unless an external sourced bound is supplied; exact graviton mass remains `None`.
- Public payloads preserve the boundary text and hierarchy `I -> I_system^S -> D_f -> dF -> i_fractal`.

## Validation Commands

```powershell
python -m unittest tests.test_gravity_null_test
python -m unittest tests.test_api_qnn_smoke
python -m unittest tests.test_network_designer_executor
python -m unittest discover -s tests -p "test_*.py"
```
