# Cerebrum Integration Inspection Handoff

Reviewer: M. Mert Yildiran (`mertyildiran`)

Prepared: 2026-07-15

## Purpose

This is a code-inspection handoff for the implemented Cerebrum-shaped memory,
cross-modal pairing, HippoRAG trace, gateway, and FNP-QNN boundaries. The first
pass is review-only: identify what is technically solid, what is only an
adapter or simulation boundary, and what should be corrected before deeper
integration.

The public implementation is distributed across three repositories. A public
HippoRAG fork is useful as reference material, but it is not the location of
the Cerebrum integration.

## Primary Review Surface: FNP-QNN

Repository: [SeCuReDmE-main-dev/FNP-QNN-MVP](https://github.com/SeCuReDmE-main-dev/FNP-QNN-MVP)

Start here:

- [`core/cerebrum_adapter.py`](../../core/cerebrum_adapter.py): deterministic
  coercion of cross-modal observations into a fixed feature bundle.
- [`core/cerebrum_runtime_bridge.py`](../../core/cerebrum_runtime_bridge.py):
  bounded memory-event ingestion, cross-modal pair construction, legacy
  snapshot compatibility, runtime state, and LVFM-facing output.
- [`api/main.py`](../../api/main.py): public HTTP routes under
  `/cerebrum/*`, including status, encode, ingest, pairs, run, gate history,
  and legacy demo surfaces.
- [`core/qnn_nucleus.py`](../../core/qnn_nucleus.py): candidate QNN boundary
  and deterministic surrogate fallback.
- [`core/ffed_plugin_bridge.py`](../../core/ffed_plugin_bridge.py): optional,
  fail-bounded bridge contract for FFeD plugin signals. Review the boundary,
  not any external plugin-pack implementation.
- [`core/cloud_rag_bridge.py`](../../core/cloud_rag_bridge.py): admitted RAG
  envelope conversion into public-safe runtime payloads.

Examples and evidence:

- [`examples/cerebrum_qnn_demo.py`](../../examples/cerebrum_qnn_demo.py)
- [`examples/cerebrum_runtime_demo.py`](../../examples/cerebrum_runtime_demo.py)
- [`examples/cerebrum_runtime_legacy_demo.py`](../../examples/cerebrum_runtime_legacy_demo.py)
- [`reports/cerebrum_runtime_wiring_report.md`](../../reports/cerebrum_runtime_wiring_report.md)
- [`tests/test_cerebrum_qnn.py`](../../tests/test_cerebrum_qnn.py)
- [`tests/test_cerebrum_runtime_bridge.py`](../../tests/test_cerebrum_runtime_bridge.py)
- [`tests/test_ffed_plugin_bridge.py`](../../tests/test_ffed_plugin_bridge.py)

The runtime currently limits one request to 1,000 events, 20,000 generated
pairs, and a 5 MiB legacy snapshot. The adapter/runtime is a compatibility and
simulation layer; it is not the abandoned Cerebrum server itself.

## Secondary Public Surface: Synthia

Repository: [SeCuReDmE-main-dev/Synthia](https://github.com/SeCuReDmE-main-dev/Synthia)

Review:

- [`synthia_core/hipporag_bridge.py`](https://github.com/SeCuReDmE-main-dev/Synthia/blob/main/synthia_core/hipporag_bridge.py):
  HippoRAG-style memory bits, graph locations, edge traces, selection scores,
  T/I/F provenance, and an optional RethinkDB trace store.
- [`tests/test_hipporag_bridge.py`](https://github.com/SeCuReDmE-main-dev/Synthia/blob/main/tests/test_hipporag_bridge.py):
  preservation, round-trip, edge, and backend-status checks.

Synthia owns lexical/source admission and traceability. It does not perform the
downstream FNP-QNN computation. Preserve the project hierarchy and do not
collapse its stages:

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```

The Synthia-specific lexical chain remains separately defined in that
repository.

## Secondary Public Surface: Gateway

Repository: [SeCuReDmE-main-dev/fnpqnn_gateway_MVP](https://github.com/SeCuReDmE-main-dev/fnpqnn_gateway_MVP)

Review:

- [`docs/INTEGRATION_WITH_FNP_QNN.md`](https://github.com/SeCuReDmE-main-dev/fnpqnn_gateway_MVP/blob/main/docs/INTEGRATION_WITH_FNP_QNN.md):
  external CLI/HTTP integration boundary.
- [`fnpqnn_gateway_mvp/qlc_submit.py`](https://github.com/SeCuReDmE-main-dev/fnpqnn_gateway_MVP/blob/main/fnpqnn_gateway_mvp/qlc_submit.py):
  validation and one-way submission to `/cerebrum/runtime/run`.
- [`fnpqnn_gateway_mvp/obsidian_bridge.py`](https://github.com/SeCuReDmE-main-dev/fnpqnn_gateway_MVP/blob/main/fnpqnn_gateway_mvp/obsidian_bridge.py):
  admitted-note query and LVFM candidate-stream construction.
- [`fnpqnn_gateway_mvp/handoff_envelope.py`](https://github.com/SeCuReDmE-main-dev/fnpqnn_gateway_MVP/blob/main/fnpqnn_gateway_mvp/handoff_envelope.py):
  compact, model-visible handoff contract.

The gateway remains separate from the simulator and must use external CLI or
loopback HTTP boundaries. It rejects raw media, passwords, tokens, secret keys,
and other forbidden fields before submission.

## HippoRAG Reference Repository

Repository: [SeCuReDmE-main-dev/hipporag-case-study](https://github.com/SeCuReDmE-main-dev/hipporag-case-study)

This is a fork of `OSU-NLP-Group/HippoRAG`. Its SecuredMe-specific commit adds
an accessibility/education console. Treat the upstream HippoRAG engine as a
reference dependency. Do not treat this fork as the source of the Cerebrum,
FNP-QNN, Synthia, or shared-memory integration.

## Explicitly Excluded

The following are outside this public handoff:

- private CeLeBrUm operator-server source and local deployment details;
- private memory-backup/archive repositories and unpublished documents;
- local memory corpora, operator notes, raw correspondence, and machine paths;
- credentials, API keys, tokens, environment values, and authentication caches;
- external/private FFeD plugin packs, plugin source, and unpublished FFeD
  architecture;
- claims that a simulator result is physical detection, proof, clinical
  evidence, or production authority.

If a public interface appears to require private evidence, mark it `not
verified from public scope` rather than requesting or reproducing the private
material.

## Reproduction Commands

FNP-QNN focused review:

```powershell
python -m unittest tests.test_cerebrum_qnn tests.test_cerebrum_runtime_bridge tests.test_ffed_plugin_bridge -v
python examples/cerebrum_qnn_demo.py
python examples/cerebrum_runtime_demo.py
python examples/cerebrum_runtime_legacy_demo.py
python scripts/validate_alpha_readiness.py
```

Synthia HippoRAG trace review:

```powershell
python -m pytest -q tests/test_hipporag_bridge.py
python -m synthia_core.cli hipporag backend status --rethinkdb-port 1
```

Gateway boundary review:

```powershell
python -m pytest -q tests/test_gateway_cli.py -k "qlc_submit or obsidian"
```

The optional FFeD plugin-pack test may be skipped when no external plugin-pack
path is configured. That skip must not be reported as validation of private
FFeD behavior.

## Verification Snapshot

The following checks were executed from fresh repository checkouts on
2026-07-15:

- FNP-QNN focused suite: 79 tests passed, with 1 optional external plugin-pack
  test skipped.
- FNP-QNN alpha-readiness validator: passed all required-file, public API,
  claim-boundary, license, import, unit-test, and alpha-local checks.
- Synthia HippoRAG bridge: 5 tests passed.
- Gateway QLC/Obsidian focus: 15 tests passed, with 4 subtests passed.

The complete gateway CLI suite is workspace-sensitive. In a standalone clone,
93 tests passed and 2 were skipped, while 3 suite-auth tests failed because
they expect the canonical 12-repository SecuredMe workspace layout. Those
layout failures did not affect the QLC submission or Obsidian/LVFM bridge
checks listed above.

The current Windows Python 3.10 host also emitted a NumPy 2.x versus compiled
PyTorch compatibility warning. The FNP-QNN tests and readiness gate still
completed successfully, but dependency compatibility should be recorded as a
review concern rather than ignored.

## Requested Reviewer Verdict

Please return a short Markdown report using `confirmed`, `concern`, or `not
verified` for each item:

1. Does `CerebrumAdapter` preserve deterministic modality/value/time handling
   and a stable feature-vector contract?
2. Does `CerebrumRuntimeBridge` construct directional cross-modal pairs and
   reject or bound malformed, oversized, non-finite, or inverted-time input?
3. Are legacy snapshots handled as compatibility data without importing or
   claiming ownership of the abandoned Cerebrum server?
4. Are the QNN candidate and deterministic fallback boundaries technically
   honest and reproducible?
5. Does the Synthia HippoRAG trace preserve graph location, selection method,
   provenance, uncertainty, and the mathematical hierarchy without collapsing
   stages?
6. Does the gateway keep external tools separated from the simulator and reject
   private/raw payload fields before submission?
7. Are any public claims stronger than the tests and code support?
8. What is the smallest concrete correction needed before a deeper
   collaboration pass?

For the first pass, please inspect and report findings. No code rewrite is
required.
