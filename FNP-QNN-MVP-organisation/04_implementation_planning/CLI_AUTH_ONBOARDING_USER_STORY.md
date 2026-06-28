# CLI Auth Onboarding User Story

Status: superseded by the school-governance provider route.

The current official classroom route supports:

- Codex/OpenAI;
- Antigravity/Gemini.

The simulator must continue to run without any AI account. AI account workflows
are optional support surfaces and must not store raw tokens, cookies, passwords,
or provider secrets.

Unsupported route:

- Ollama Cloud and local uncensored model routes are not official school
  providers for FNP-QNN.

The supported user story is:

1. The student or teacher opens the simulator locally.
2. The base simulator works without provider authentication.
3. If AI-assisted review is needed, the user connects Codex/OpenAI or
   Antigravity/Gemini through the documented school route.
4. The route emits a provider fingerprint and a wake prompt only.
5. The selected external agent remains native; it does not become the
   simulator, and the simulator does not become the agent.
6. All unsupported provider requests return a bounded unsupported-provider
   response.
