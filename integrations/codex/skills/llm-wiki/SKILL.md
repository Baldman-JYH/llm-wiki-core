---
name: llm-wiki
description: Maintain a local LLM Wiki vault from Codex App or Codex CLI. Triggers on set up wiki, scaffold vault, check transport, check wiki status, continue wiki, resume wiki context, ingest this source, query the wiki, what does the wiki know about, save this insight, lint the wiki.
---

# LLM Wiki

Use this skill when the user wants Codex to maintain a local LLM Wiki vault.

The wiki is the durable artifact. Chat is the interface.

## Core Rules

- Treat `.raw/` as immutable source material.
- Maintain `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
- Prefer artifact-level equivalence over byte-for-byte LLM prose matching.
- Use the neutral `llm-wiki` core commands instead of redefining behavior in the adapter.

## Commands

- `llm-wiki init <vault> --purpose "..."`
- `llm-wiki detect-transport <vault>`
- `llm-wiki status <vault>`
- `llm-wiki continue <vault>`
- `llm-wiki ingest <vault> <source-under-.raw>`
- `llm-wiki query <vault> "<question>"`
- `llm-wiki save <vault> --title "..." --content "..."`
- `llm-wiki lint <vault>`

## Natural Language Mapping

- "set up wiki" or "scaffold vault" means run init.
- "check transport" means run detect-transport.
- "check wiki status" means run status.
- "continue wiki" or "resume wiki context" means run continue.
- "ingest this source" means run ingest.
- "what does the wiki know about X" means run query.
- "save this insight" means run save.
- "lint the wiki" means run lint.

## Boundaries

- Do not modify Raw Source files.
- Do not generate Claude-specific plugin files.
- Do not claim semantic deep retrieval; the current MVP query is deterministic local Wiki search.
