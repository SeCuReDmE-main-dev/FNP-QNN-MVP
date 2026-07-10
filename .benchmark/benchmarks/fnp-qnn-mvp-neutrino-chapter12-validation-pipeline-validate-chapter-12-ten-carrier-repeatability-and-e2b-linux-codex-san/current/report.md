# Chapter 12 Ten-Carrier Cross-Platform Benchmark

## Objective

Validate the public-safe ten-carrier calculation, internal repeatability,
sensitivity, fail-closed guardrails, and isolated Linux portability.

## Codebase Context

Synthia performs lexical admission. FNP-QNN computes only after admission and
preserves `I -> I_system^S -> D_f -> dF -> i_fractal`.

## Product / Tool Thesis

The chamber can couple ten explicit carriers reproducibly without claiming a
validated physical model.

## Repo Evidence Map

- `core/neutrino_chapter12_models.py`: pure models;
- `core/neutrino_chapter12_validation.py`: admitted orchestration;
- `scripts/run_chapter12_e2b_worker.py`: lightweight Linux worker;
- lab evidence directory: hashes, matrices, raw outputs, and E2B lifecycle.

## Research Questions

- Are deterministic outputs stable across environments?
- Do all carrier perturbations follow the analytic weight?
- Do all required-carrier ablations and overclaims fail closed?
- Does seeded stochastic behavior replay exactly?

## Benchmark Methodology

Local Windows tests and CLI runs were followed by 32 isolated E2B Linux
sandboxes. The pool executed 128 shards and destroyed every sandbox afterward.

## Market Landscape

No product comparator is claimed. This is an internal cross-platform benchmark,
not a physics-simulator ranking.

## Comparator Profiles

- Windows: maintained repository `.venv`;
- Linux: disposable E2B `codex` sandbox with NumPy only.

## Benchmark Validity Analysis

Valid for software correctness, repeatability, portability, and throughput.
Invalid for experimental or physical validation.

## Comparative Benchmark Matrix

Both environments passed the ten-carrier baseline, deterministic replay,
seeded replay, ablations, perturbations, medium/detector variations, and guards.

## Benchmark Map

See `benchmark-map.md`.

## Recommended First Benchmark Scenario

The canonical baseline uses ten equally weighted carriers, vacuum toy medium,
an explicit 2x2 detector response, 100 deterministic runs, and 100 seeded runs.

## Execution Harness

Local harness: lab `run_chapter12_intensive_validation.py`.
E2B harness: `scripts/run_chapter12_e2b_worker.py`.

## Measured Results

- local full FNP suite: 387 tests passed, 2 skipped;
- E2B workers: 32;
- E2B tasks: 128/128 passed;
- E2B model executions: 5,060,056;
- E2B elapsed wall time: 253.176 seconds;
- E2B lifecycle: no sandboxes remained;
- maximum proof state: `P2_internal_repeatability`;
- physical model validated: false.

## Measurement Plan

Chapters 13 and 14 reuse the frozen lab template and must preserve the reference
fingerprint, proof ceiling, seed policy, and claim matrix.

## Recommended Benchmark Priorities

Prioritize new-variable sensitivity and invariant preservation. Treat raw
throughput as non-gating supporting evidence.

## Risks / Unknowns

The toy medium and detector models are not calibrated against experimental
data. More runs reduce sampling uncertainty but do not change evidence class.

## Sources

Primary evidence is the repository code, unit-test output, CLI output, and E2B
result bundle generated on 2026-07-10.
