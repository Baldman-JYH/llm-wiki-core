---
description: Thin /wiki wrapper for the project-local llm-wiki Claude skill.
---

Read the project-local `llm-wiki` skill.

Map `/wiki` intent to neutral `llm-wiki` commands.

Use `/wiki` on a new vault for `llm-wiki init <vault> --purpose "..."`.

Use `/wiki` on an existing vault for `llm-wiki continue <vault>`.

Use explicit subcommands for transport, status, ingest, ingest-batch, ingest-url, search, query, and lint.

Do not implement hooks, subagents, or Obsidian-specific automation.
