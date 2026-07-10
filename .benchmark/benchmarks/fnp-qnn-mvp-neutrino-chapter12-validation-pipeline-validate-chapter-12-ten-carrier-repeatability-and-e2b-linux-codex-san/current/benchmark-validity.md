# Benchmark Validity Analysis

## Valid comparison

The benchmark compares the same public-safe chapter-12 mathematical functions
on the maintained Windows environment and isolated E2B Linux sandboxes. Inputs,
formula versions, carrier order, seeds, tolerances, and claim boundaries are
identical. Correctness, repeatability, fail-closed behavior, portability, and
throughput are therefore fair internal comparison dimensions.

## Invalid comparison

This benchmark does not compare FNP-QNN with a neutrino experiment, detector,
physics simulator, or external scientific model. Run count cannot promote
internal repeatability into experimental validation. E2B throughput is also
non-gating because sandbox startup, clone, and package-install latency differ
from the local environment.

## Accepted claims

- the code accepts and validates exactly ten named carriers;
- weighted contributions match the declared analytic formula;
- required-carrier ablations fail closed;
- seeded runs replay identically;
- the tested path executes on Windows and Linux;
- the maximum proof state is `P2_internal_repeatability`.

## Rejected claims

- physical ten-variable model validated;
- MSW behavior measured;
- CP violation measured;
- a real neutrino detected;
- `i_fractal_candidate` is proof.

Validity status: `valid_internal_cross_platform`.
