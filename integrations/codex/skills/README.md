# Codex Skills

The reusable LLM Wiki skill lives in `integrations/codex/skills/llm-wiki`.

## User-Level Installation

Copy the `llm-wiki` skill directory into the Codex user skills directory for your platform.

Use the current Codex documentation for the exact destination path. R4.0 does not automatically mutate global Codex configuration.

## Verification

Verify the skill includes `llm-wiki search`, `llm-wiki ingest-batch`, and `llm-wiki ingest-url`.

Then ask Codex to:

- "check wiki status"
- "continue wiki"
- "search wiki for durable knowledge"
- "what does the wiki know about durable knowledge"
