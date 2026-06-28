# CLI Auth Onboarding Evaluation - Superseded

This June 23, 2026 evaluation has been superseded by the school-governance
provider route.

Current official classroom providers:

- Codex/OpenAI;
- Antigravity/Gemini.

Unsupported classroom providers:

- Ollama Cloud;
- local uncensored model routes;
- unknown agent routes.

The accepted design is:

1. Base simulator works without an AI account.
2. Provider readiness is fingerprint-only.
3. Raw tokens, cookies, passwords, and provider secrets are never printed or
   stored as onboarding state.
4. External control is dry-run first.
5. Unsupported provider requests are rejected or marked unsupported.
6. Human review remains required for school-facing interpretation.

This document is retained as historical project memory only. It must not be used
as implementation guidance.
