# CLI Provider MCP Reference

Status: current school-governance provider reference.

These commands are support surfaces around the simulator. They do not change
simulator internals and they do not store provider secrets.

Official provider mapping:

| Provider | School route | Runtime intent |
| --- | --- | --- |
| `openai` | Codex | Codex stays native and receives simulator context. |
| `google` | Gemini/Antigravity | Antigravity/Gemini stays native and receives simulator context. |

Unsupported provider mapping:

| Provider request | Behavior |
| --- | --- |
| Ollama Cloud | Return unsupported-provider response. |
| Local uncensored model route | Return unsupported-provider response. |
| Unknown agent route | Return unsupported-provider response. |

MCP-facing controls must preserve:

- fingerprint-only provider readiness;
- no raw token storage;
- dry-run by default for external control;
- Codex/OpenAI and Antigravity/Gemini as the only official classroom routes;
- the simulator hierarchy:

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```
