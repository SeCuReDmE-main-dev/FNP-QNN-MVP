# CLI LLM Support Edge Cases

Date: 2026-06-23

Purpose: make the FNP-QNN CLI easy to support when the selected LLM system is
Gemini/Antigravity, Codex, or Ollama Cloud/OpenClaw.

## Support Entry Point

Use the support report first:

```powershell
fnp-qnn support all
fnp-qnn support provider openai
fnp-qnn support provider google
fnp-qnn support provider ollama
```

The report is safe to paste into an LLM support conversation because it does not
print raw tokens.

## Edge Case Matrix

| Case | Symptom | Expected CLI response | Recovery |
| --- | --- | --- | --- |
| No provider selected | User asks for AI wiring without provider | Ask for `openai`, `google`, or `ollama` | `fnp-qnn agent profile <provider>` |
| Token not approved | Onboarding called without approval | Refuse write | Add `--approve-fingerprint` after confirming account |
| Raw token concern | User asks where token is stored | Fingerprint only | `fnp-qnn auth status` |
| Codex installed but not logged in | OpenAI support report says provider not connected | Show Codex login next step | `fnp-qnn external-ai connect codex --device-auth` |
| Antigravity absent | Google route selected but CLI unavailable | Warn tool missing | Install/expose Antigravity or use fingerprint-only dry-run |
| Google ADC absent | Gemini OAuth expected but no ADC | Warn provider not connected | `fnp-qnn auth web-login google --run-gcloud` |
| Ollama CLI present but cloud not connected | `ollama --version` works but support says not connected | Do not treat CLI presence as cloud auth | Set `OLLAMA_API_KEY` or login-provider ollama |
| OpenClaw config missing | Ollama/OpenClaw support expected but no config | Warn only; Ollama may still work | `fnp-qnn external-ai inspect-openclaw` |
| User expects same plugins everywhere | Provider switches from Codex to Gemini | Wake prompt states native assets differ | `fnp-qnn agent wake-prompt <provider>` |
| Simulator should work without AI | Provider login fails | Base commands still run | `fnp-qnn status`, `fnp-qnn qnn smoke` |
| Accidental execution | User runs control without execute | Dry-run only | Add `--execute` deliberately |
| Delegation too broad | User asks agent to rewire everything | Wake prompt says narrow wiring only | Use onboarding answers and task allowlist |
| Secret leak risk | OpenClaw inspected | Redacted shape only | Never print decrypted credentials |
| Wrong provider token | Fingerprint provider mismatch | Provider status not connected for selected provider | Store matching provider fingerprint |
| Offline/local-only mode | No network or accounts | Use simulator-only commands | Avoid MCP/control execution |

## Good Support Conversation Pattern

1. Ask which provider the user wants:

```text
OpenAI/Codex, Google/Gemini/Antigravity, or Ollama Cloud/OpenClaw?
```

2. Run:

```powershell
fnp-qnn support provider <provider>
```

3. If `support_summary = needs-action`, follow `next_steps`.

4. If ready, run:

```powershell
fnp-qnn onboarding questions
fnp-qnn onboarding apply <provider> --approve-fingerprint
```

5. Preview the agent context:

```powershell
fnp-qnn agent wake-prompt <provider>
```

6. Delegate only if requested:

```powershell
fnp-qnn onboarding apply <provider> --approve-fingerprint --delegate
```

7. Execute only if requested:

```powershell
fnp-qnn onboarding apply <provider> --approve-fingerprint --delegate --execute-delegate
```

## LLM Support Rules

- Do not ask the user to paste raw secrets into chat.
- Do not assume Codex plugins exist inside Gemini or Ollama.
- Do not assume Antigravity tools exist inside Codex.
- Do not treat Ollama CLI installation as Ollama Cloud login.
- Do not turn provider login into simulator dependency.
- Do not rewrite `AGENTS.md`, `SOUL.md`, `USER.md`, or `MEMORY.md` outside the managed onboarding block.
- Use dry-run first.
- Preserve the non-clinical alpha-local boundary.

## Known Good Smoke Commands

```powershell
fnp-qnn status
fnp-qnn doctor --full --no-probe-services
fnp-qnn support all
fnp-qnn mcp manifest
fnp-qnn onboarding questions
fnp-qnn agent wake-prompt openai
fnp-qnn agent wake-prompt google
fnp-qnn agent wake-prompt ollama
```

## Escalation

Escalate to implementation only when:

- the selected provider is connected or intentionally bypassed for dry-run;
- onboarding has been approved;
- the user has stated the simulator utility they want;
- the change can be tested with `.venv`;
- the change keeps base simulator commands AI-independent.
