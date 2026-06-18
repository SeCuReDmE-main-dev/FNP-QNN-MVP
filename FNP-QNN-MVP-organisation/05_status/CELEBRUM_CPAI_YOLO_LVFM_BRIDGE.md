# CeLeBrUm CPAI/YOLO vers LVFM

Status: alpha-local, experimental, educational evidence only. This bridge is not clinical, not a security product, and not production validation.

## Why CPAI Is The Mesh Base

CodeProject.AI is used as the local AI routing substrate. It gives CeLeBrUm a stable local HTTP surface for vision tools without importing heavy YOLO dependencies directly into the model server. Datadog can observe the route and latency, MCP can call the route, and FNP-QNN can receive only sanitized observations.

The default CPAI target is:

```text
http://127.0.0.1:32168
```

Port `7476` was checked as available for a future local facade, but the current bridge keeps CeLeBrUm on `8765` and CPAI on `32168`.

## Why YOLO Is A Tool, Not The Brain

YOLO detects visual objects or regions. It does not decide truth, clinical state, security state, or final meaning. CeLeBrUm treats each detection as a local perception event.

Each detection is converted into a bounded observation:

```json
{
  "modality": "vision",
  "value": 0.82,
  "source": "codeproject-ai-yolo",
  "label": "example-object",
  "payload_ref": "sha256-prefix",
  "provenance": {
    "T": 0.82,
    "I_system_component": 0.18,
    "F": 0.18,
    "dF": 0.21,
    "interpretation": "bounded local visual ambiguity; not a replacement for global I"
  }
}
```

This preserves the hierarchy:

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```

## How It Enters LVFM

CeLeBrUm sends the sanitized observations to:

```text
POST /cerebrum/runtime/run
```

The FNP-QNN simulator remains the owner of LVFM. CeLeBrUm does not write directly into the graph. It only submits observations, `cpai_context`, and optional plugin context. The simulator then builds the LVFM snapshot with nodes, edges, register keys, `T/I/dF/F`, CPAI mesh profile, and plugin trace when enabled.

## Datadog And MCP Role

Datadog receives operational metrics only:

```text
celebrum.cpai.status
celebrum.cpai.detect.duration_ms
celebrum.cpai.detect.objects
celebrum.fnp_qnn.lvfm_submit.status
```

MCP exposes local tools:

```text
cpai_status
cpai_vision_detect
fnp_qnn_lvfm_submit
```

Neither surface should log image bytes, raw secrets, `.env` values, or raw private payloads.

## Concrete Example

An image of a simulated bacterium field is sent to CPAI/YOLO. CPAI returns one high-confidence region and one low-confidence region. CeLeBrUm converts the high-confidence region into high `T` and low local ambiguity. The low-confidence region becomes a higher `I_system_component` and contributes more to `dF`. FNP-QNN then places those observations in LVFM, where the graph can show which visual regions increased local tension without claiming that the ambiguity was solved.

## MultiModeLLM Later

`CodeProject.AI-MultiModeLLM` remains phase 2. It should read summaries from YOLO and LVFM, then produce a bounded explanation. It should not be required for the first YOLO bridge, and it should not receive private images by default.
