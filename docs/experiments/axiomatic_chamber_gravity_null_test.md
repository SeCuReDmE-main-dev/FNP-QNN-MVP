# Axiomatic-Chamber Gravity Null-Test

## Purpose

This experiment turns the Vedral/Quantum Foundations video lane into a bounded FNP-QNN proof-of-principle:

1. isolate sources in an axiomatic chamber;
2. simulate an entangled pair `A-B`;
3. add a separable local probe or mass-source candidate `C`;
4. measure whether `B` shows a no-signalling residual;
5. classify any residual through `D_min`, `D_max`, `D_f_hat`, `F_chamber`, and `Adm`;
6. export an E2B micro-VM plus Datadog telemetry review contract.

It does not prove quantum gravity, faster-than-light signalling, or exact graviton mass.

The axiomatic-chamber discipline is grounded in the local final manuscript
`[local maintainer path redacted]`:
Chapter 5 defines `I_fractal` as a conditional carrier authorized by `I_system`
and `Adm`; Chapter 6 builds `GPCN-Set_phi` as a test chamber; Chapter 7 makes
validation depend on existence, membership, boundary, scale, local dimension,
fractal indeterminacy, normalization, and non-universality tests.

## Taxonomy

| Symbol | Meaning | Simulator field |
| --- | --- | --- |
| `A` | remote entangled partner | `roles.A` |
| `B` | local target particle entangled with `A` | `roles.B` |
| `C` | uncorrelated local probe or mass-source candidate | `roles.C` |
| `C_alpha` | entangled-pair room | `chamber.C_alpha` |
| `C_beta` | uncorrelated-probe room | `chamber.C_beta` |
| `Omega` | local observation domain | `chamber.Omega` |
| `d_min`, `d_max` | spatial or chamber separation guard | `chamber.bounds` |
| `D_min`, `D_max` | local fractal carrier bounds | `fractal_carrier` |
| `Delta_NS` | no-signalling residual | `no_signalling.Delta_NS` |
| `F_chamber` | frustration from competing explanatory sources | `frustrated_state.F_chamber` |
| `Adm` | admissibility gate | `admissibility.Adm` |
| `GQ_super_equation` | bounded explanatory simulator score | `gq_super_equation.GQ_super_equation` |

## Core Classifications

- `no_detected_remote_influence`: the `B` marginal residual is below the local chamber threshold.
- `local_coupling_or_shared_noise`: leakage, mass-dispersion coupling, or local noise explains the residual first.
- `frustrated_state_requires_external_validation`: the simulator sees strong internal tension, but does not elevate it to physics proof.
- `anomaly_requires_external_validation`: a non-null residual needs external data, source formulas, and independent physical validation.

## E2B and Datadog Review Lane

The experiment includes `e2b_datadog_review` metadata by default.

E2B role:

- run the null-test in an ephemeral micro-VM;
- verify reproducibility outside the maintainer workstation;
- act as a clean review surface for source-led physics experiments.

Datadog role:

- track experiment residuals across runs;
- expose telemetry for `Delta_NS`, `F_chamber`, `GQ_super_equation`, `local_contamination`, and `entangled_pair_resistance`;
- support monitors that flag non-null residuals, contamination, or loss of resistance.

No Datadog or E2B call runs during the default API call. The payload only returns a secret-safe contract and suggested command.

## Relationship To Penrose/Hameroff And Hydra-EM-GPCN

This null-test is designed as a sister experiment to the existing Penrose/Hameroff and Hydra-EM-GPCN lanes.

Current code already present:

- `core/penrose_hameroff_math.py`
  - `objective_reduction_profile()` computes bounded educational timing metadata from `tau_s = hbar / E_delta`.
  - `orchestration_profile()` compares coherence time against the reduction timescale.
  - `spin_network_admissibility_profile()` checks simple 3-valent spin-network admissibility.
  - `twistor_nonlocality_profile()` carries entanglement, reduction pressure, and gravitational-context metadata.
  - `microtubule_signal_profile()` maps frequency, diffusion, and damping into a bounded microtubule-like signal score.
- `core/hydra_em_gpcn_math.py`
  - `gpcn_set_phi_profile()` creates the same kind of axiomatic chamber used by this gravity null-test.
  - `quasicrystal_gpcn_projection_profile()` creates deterministic proxy neighborhoods.
  - `microtubule_proxy_phi_profile()` maps each proxy into cubic T/I/F, contradiction, and `Adm`.
  - `hydra_em_gpcn_orch_profile()` returns a bounded verdict: `communicates`, `decoheres`, `suspended`, or `rejected`.

The two projects share the same discipline:

- define the chamber before interpreting the signal;
- keep `D_f_hat` as a local carrier, not as global `I`;
- treat contradiction/frustration as evidence classification, not physical proof;
- use E2B and Datadog as optional review/telemetry surfaces.

Conceptual bridge:

- Gravity null-test: asks whether an entangled-pair residual survives source isolation.
- Hydra-EM-GPCN microtubule simulation: asks whether proxy microtubule states communicate, decohere, suspend, or reject inside `GPCN-Set_phi`.
- Both can be reviewed by the same Datadog-style metrics: residual, contradiction, damping, admissibility, and resistance/stability across repeated runs.

## Bell State Vs Graviton-Node Chamber

The implementation deliberately separates the Bell entangled state from the
gravity/null-test chamber. They are two different objects:

| Axis | Bell entangled state | Graviton-node / gravity null-test chamber |
| --- | --- | --- |
| Object type | Two-particle state/correlation reference | Axiomatic measurement and classification room |
| Roles | `A` and `B` only | `A`, `B`, and uncorrelated local probe/source `C` |
| Question | Are `A` and `B` correlated as an entangled pair? | Does `B` show a residual after source isolation? |
| Outputs | Correlation and separability metadata | `Delta_NS`, `F_chamber`, `D_f_hat`, `Adm`, `GQ_super_equation`, telemetry |
| Forbidden inference | Does not imply gravity or signalling | Does not infer exact graviton mass or physical quantum-gravity proof |

Code anchors:

- `bell_state_reference_profile()` returns the Bell-state reference. It has
  roles `A-B`, excludes `C`, and has no `Adm`, `D_min/D_max`, chamber, or
  graviton-constraint metadata.
- `bell_vs_gravity_chamber_taxonomy()` returns executable invariants proving
  that the chamber wraps the Bell input with `C`, bounds, residual tests,
  admissibility, and constraint-only graviton metadata.
- `run_gravity_null_test()` embeds this taxonomy under
  `bell_vs_chamber_taxonomy` so API and QNN smoke responses keep the distinction
  visible.

## API

Status:

```http
GET /fnp-qnn/gravity-null-test/status
```

Run:

```http
POST /fnp-qnn/gravity-null-test/run
```

Example:

```json
{
  "shots": 512,
  "local_noise": 0.02,
  "leakage": 0.0,
  "mass_dispersion": 0.0,
  "include_sequence_export": true,
  "include_qiskit_preview": true,
  "include_e2b_datadog_review": true
}
```

## QNN Integration

`POST /qnn/smoke` accepts:

```json
{
  "gravity_null_test_enabled": true,
  "gravity_null_test_shots": 512,
  "gravity_null_test_local_noise": 0.02,
  "gravity_null_test_leakage": 0.0,
  "gravity_null_test_mass_dispersion": 0.0
}
```

The experiment feature vector is appended only when explicitly enabled. Existing QNN behavior remains unchanged by default.

## Boundaries

- The simulator explores a chamber-isolation principle.
- `GQ_super_equation` is a bounded score, not a physical law.
- `graviton_constraint_profile` is a placeholder until external peer-reviewed data and formulas are supplied.
- The project must preserve `I -> I_system^S -> D_f -> dF -> i_fractal`.
