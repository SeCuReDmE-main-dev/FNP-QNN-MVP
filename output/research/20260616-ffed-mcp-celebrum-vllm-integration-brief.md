## Objective

Determine whether CeLeBrUm can remain private while being exposed through an FFeD-governed MCP/plugin path, with `celebrum-model-server` evolving toward a real vLLM-backed model service and Datadog-observable runtime.

## Environment / Stack Context

- Current workspace: `FNP-QNN-MVP-version-desise-simulator-`
- Related private/local backend substrate: `C:\Users\jeans\Desktop\FfeD`
- Candidate CeLeBrUm serving repo inspected from GitHub: `SeCuReDmE-main-dev/celebrum-model-server`
- Existing local simulator already has optional Docker services for `vllm`, `etcd`, Datadog Agent, and E2B audit.

## Research Questions

1. Can CeLeBrUm stay private if we route capability access through FFeD rather than direct public exposure?
2. Is `celebrum-model-server` already a vLLM service?
3. What is the safest integration path to make it a true model-serving lane later?
4. Where should MCP and Datadog fit?

## Findings

- `confirmed by primary sources`: `celebrum-model-server` is currently a private local FastAPI memory/RAG server, not yet a true vLLM-backed model server. Its own README says v1 is local lexical RAG and that heavy model serving or vLLM/GPU work is deferred to a later phase.
- `confirmed by primary sources`: `celebrum-model-server` already has the right boundary posture for privacy. It is local-only by default, uses a bearer token for non-health endpoints when configured, and explicitly states that private material must not be exposed publicly.
- `confirmed by primary sources`: `celebrum-model-server` already contains integration surfaces (`/integrations/*`) and observability hooks, so it is a valid backend candidate to become a later FFeD-routable model lane.
- `confirmed by primary sources`: FFeD already has a governed Gate 5 adaptive plugin boundary with registration, approval, invocation, proof envelopes, policy scopes, scrubbed subprocess environments, and a Codex/OpenAI adapter extension.
- `confirmed by primary sources`: FFeD documentation explicitly separates third-party OpenAI/Codex-style plugins from FFED-native plugins and requires all such integrations to pass through the Gate 5 adapter/native-bridge path rather than calling kernel/control-plane internals directly.
- `confirmed by primary sources`: FFeD brain-bridge rules say the bridge is a handoff boundary, not the runtime itself. That aligns with using FFeD as the governance and routing layer while keeping CeLeBrUm’s actual data/model process private and local.
- `inferred from multiple secondary sources`: The cleanest privacy-preserving pattern is not "CeLeBrUm as a public MCP server", but "CeLeBrUm as a local private model service behind an FFeD-governed MCP/plugin facade". In practice, MCP becomes the operator-facing contract; CeLeBrUm remains loopback/private.
- `confirmed by primary sources`: vLLM exposes Prometheus metrics on `/metrics`, and Datadog has a first-party `vllm` integration that scrapes that endpoint. This matches the Docker observability lane already added in the simulator workspace.
- `tentative due to conflicting or missing evidence`: The exact repository contract for "MCP FFeD" is not yet visible as a first-class MCP server package in the inspected FFeD surfaces. What is visible today is the Gate 5 plugin/control-plane path, which is sufficient to implement the same governance boundary even if the final operator entrypoint is labeled MCP later.

## Recommended Path

1. Keep `celebrum-model-server` private and local-only.
   It should bind to loopback or private Docker network only and never expose raw CeLeBrUm corpora directly.

2. Turn `celebrum-model-server` into a two-lane backend.
   Lane A: existing local RAG/evidence service.
   Lane B: new optional `vLLM` inference adapter behind internal endpoints such as `/integrations/vllm/status` and `/integrations/vllm/generate`.

3. Put FFeD in front as the governed execution boundary.
   The first implementation should be a Gate 5 plugin or FFED-native plugin registered and approved through the control-plane, not a direct public bridge.

4. Model the plugin capability narrowly.
   Example capability: `celebrum_private_inference.generate`.
   Input: prompt + bounded generation params + corpus lane selector.
   Output: answer + evidence refs + policy tags + audit refs.

5. Keep private corpora inside CeLeBrUm only.
   FFeD should receive only bounded request/response envelopes, proof/audit metadata, and sanitized evidence references.

6. Add Datadog at the vLLM service boundary, not at raw document level.
   Collect latency, throughput, cache, availability, and invocation counts. Never send raw prompts or private source text unless an explicit redaction-safe policy is added.

7. Use E2B only for smoke and isolation validation.
   E2B should test startup, health, bounded query success, and observability, not hold persistent private corpora.

## Alternatives Considered

- Direct public MCP over CeLeBrUm.
  Rejected. It weakens the privacy boundary and makes policy enforcement harder.

- Put vLLM directly inside FFeD kernel/control-plane.
  Rejected. It conflicts with FFeD’s boundary model; model execution should remain an external governed capability.

- Keep `celebrum-model-server` as RAG-only forever.
  Rejected if the goal is a true CeLeBrUm model lane. The repo is already structured to grow into that role.

## Risks / Unknowns

- No inspected evidence yet shows a finished first-class MCP package in FFeD for this exact lane; Gate 5 plugin governance is the confirmed immediate path.
- vLLM compute requirements may exceed the local environment; the architecture is valid even if the first real model is small.
- A privacy-safe evidence schema still needs to be defined so FFeD can reference CeLeBrUm outputs without leaking private content.
- `celebrum-model-server` will need a new internal adapter contract for vLLM before it becomes a true model server rather than a RAG server.

## Sources

- `C:\Users\jeans\AppData\Local\Temp\celebrum-model-server-codex\README.md`
- `C:\Users\jeans\AppData\Local\Temp\celebrum-model-server-codex\src\celebrum_model_server\api.py`
- `C:\Users\jeans\AppData\Local\Temp\celebrum-model-server-codex\src\celebrum_model_server\integrations_api.py`
- `C:\Users\jeans\AppData\Local\Temp\celebrum-model-server-codex\src\celebrum_model_server\config.py`
- `C:\Users\jeans\Desktop\FfeD\README.md`
- `C:\Users\jeans\Desktop\FfeD\ffed-brain-bridge\docs\boundaries\gateway-boundaries.md`
- `C:\Users\jeans\Desktop\FfeD\ffed-control-plane\src\ffed_control_plane\app.py`
- `C:\Users\jeans\Desktop\FfeD\ffed-control-plane\src\ffed_control_plane\gate5_plugin_endpoint.py`
- `C:\Users\jeans\Desktop\FfeD\ffed-ops-docs\docs\architecture\gate5-codex-extension.md`
- [vLLM metrics documentation](https://docs.vllm.ai/en/v0.14.0/usage/metrics/)
- [Datadog vLLM integration](https://docs.datadoghq.com/integrations/vllm/)
