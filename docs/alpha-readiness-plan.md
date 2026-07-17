# Alpha Readiness Plan

This plan defines the five gates required before calling the FNP-QNN suite a
solid alpha. It keeps the project an alpha-local, non-clinical educational
research simulator. Each action is intentionally small enough to become one
reviewable implementation iteration.

## Five major gates

1. **Education journey and contracts**: students and teachers need explicit,
   supervised paths from fixture to explanation, not only operator controls.
2. **Reproducibility and evidence**: every run needs a stable seed, provenance,
   replayable input, and a human-readable evidence artifact.
3. **Security and governance**: public routes, sessions, adapters, secrets, and
   private evidence need fail-closed boundaries.
4. **Accessible public site and UX**: the landing and local dashboard need
   keyboard navigation, responsive behavior, reduced-motion support, and clear
   claims. WCAG 2.2 treats text alternatives and navigability as core
   requirements: <https://www.w3.org/TR/WCAG22/>.
5. **Operations and observability**: health, readiness, error states, telemetry,
   deployment smoke tests, and rollback evidence must be repeatable. OpenTelemetry
   defines observability around emitted signals such as traces, metrics, and logs:
   <https://opentelemetry.io/docs/concepts/signals/>.

## Twenty-five actions

### 1. Education journey and contracts

- [x] Add student and teacher entry points to the public landing (`1.1`).
- [x] Define a versioned lab manifest with objective, inputs, expected evidence, and boundary text (`1.2`).
- [x] Add a student lab selector that uses only approved fixture-backed activities (`1.3`).
- [x] Add a teacher review view for seed, trace, claims, and export status (`1.4`).
- [x] Add progress states and recovery copy for incomplete or rejected runs (`1.5`).

### 2. Reproducibility and evidence

- [x] Make the run manifest the shared contract across API, Panel, CLI, and exports (`2.1`).
- [x] Add replay tests for every public education fixture (`2.2`).
- [x] Add evidence schema versioning and migration notes (`2.3`).
- [x] Export a redacted JSON plus a concise Markdown review record (`2.4`).
- [ ] Add deterministic comparison output for two runs with the same seed (`2.5`).

### 3. Security and governance

- [ ] Inventory every public route and mark authentication, size, and provider boundaries (`3.1`).
- [ ] Enforce an allowlist for education adapters and simulator commands (`3.2`).
- [ ] Add negative tests for shell execution, oversized payloads, non-finite numbers, and secret leakage (`3.3`).
- [ ] Add session expiry and explicit human-review state to operator actions (`3.4`).
- [ ] Add a release-time secret and private-path scan for public artifacts (`3.5`).

Use OWASP ASVS as the verification vocabulary for web controls and secure
development decisions: <https://owasp.org/www-project-application-security-verification-standard/>.

### 4. Accessible public site and UX

- [ ] Run a repeatable HTML and keyboard contract check for every public page (`4.1`).
- [ ] Add reduced-motion and focus-visible behavior to the landing and Panel handoff (`4.2`).
- [ ] Add mobile layout checks at the supported viewport widths (`4.3`).
- [ ] Add plain-language glossary and bilingual boundary copy (`4.4`).
- [ ] Replace screenshot-only proof with text and JSON evidence links (`4.5`).

### 5. Operations and observability

- [ ] Separate liveness, readiness, and dependency health responses (`5.1`).
- [ ] Emit structured run, validation, and rejection events with correlation IDs (`5.2`).
- [ ] Add dashboard counters for runs, failures, gated providers, and evidence exports (`5.3`).
- [ ] Add static deployment smoke tests for landing assets, headers, and robots policy (`5.4`).
- [ ] Document rollback, incident capture, and alpha release sign-off (`5.5`).

## Iteration rule

One action is implemented per iteration, followed by the full required test
commands. A commit and push happen only after the suite is 100% green. No
alpha claim is promoted from a plan item alone.
