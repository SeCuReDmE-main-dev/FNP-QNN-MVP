# FNP-QNN AI Control MCP

This local plugin exposes an MCP server for authenticated simulator control.

- OpenAI/ChatGPT routes to Codex.
- Google/Gemini routes to Antigravity.
- Ollama Cloud routes to Ollama CLI/cloud models.
- Onboarding writes AGENTS.md, SOUL.md, USER.md, MEMORY.md, and config/user_wiring.json after fingerprint approval.
- Simulator commands are allowlisted and dry-run by default.
- Base simulator functions do not depend on AI providers.
- Raw tokens are not stored by this plugin.
