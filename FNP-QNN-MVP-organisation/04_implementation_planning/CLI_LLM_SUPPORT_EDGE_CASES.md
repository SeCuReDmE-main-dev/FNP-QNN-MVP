# CLI LLM Support Edge Cases

Status: current school-governance policy.

Official classroom providers:

- `openai` / Codex;
- `google` / Gemini / Antigravity.

Unsupported providers:

- Ollama Cloud;
- local uncensored model routes;
- unknown agent routes.

Expected edge cases:

| Case | Expected behavior |
| --- | --- |
| No provider selected | Keep simulator local and ask for `openai` or `google` only. |
| Codex not authenticated | Report Codex readiness as missing without storing credentials. |
| Gemini/Antigravity not authenticated | Report Google readiness as missing without storing credentials. |
| Unsupported provider requested | Return an unsupported-provider payload and recommend Codex/OpenAI or Antigravity/Gemini. |
| External agent not available | Keep simulator functional and emit a dry-run plan only. |
| Provider token supplied | Never print raw token; store no raw token by default. |

The external AI layer remains a support boundary. It does not expand formal
simulator authority and does not alter the hierarchy:

```text
I -> I_system^S -> D_f -> dF -> i_fractal
```
