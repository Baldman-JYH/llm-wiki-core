---
name: llm-wiki
description: Maintain a local LLM Wiki vault from Codex App or Codex CLI. Triggers on set up wiki, scaffold vault, check transport, check wiki status, continue wiki, resume wiki context, ingest this source, ingest this folder, ingest this URL, search wiki for, find wiki pages about, query the wiki, what does the wiki know about, save this insight, lint the wiki.
---

# LLM Wiki

Use this skill when the user wants Codex to maintain a local LLM Wiki vault.

The wiki is the durable artifact. Chat is the interface.

## Core Rules

- Treat `.raw/` as immutable source material.
- Maintain `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
- Prefer artifact-level equivalence over byte-for-byte LLM prose matching.
- Use the neutral `llm-wiki` core commands instead of redefining behavior in the adapter.
- Natural-language triggers are required; slash commands are a target UX layer.

## Commands

- `llm-wiki init <vault> --purpose "..."`
- `llm-wiki detect-transport <vault>`
- `llm-wiki status <vault>`
- `llm-wiki continue <vault>`
- `llm-wiki ingest <vault> <source-under-.raw>`
- `llm-wiki ingest-batch <vault> <source-root-under-.raw>`
- `llm-wiki ingest-url <vault> <url>`
- `llm-wiki search <vault> "<query>"`
- `llm-wiki query <vault> "<question>"`
- `llm-wiki save <vault> --title "..." --content "..."`
- `llm-wiki lint <vault>`

## Natural Language Mapping

- "set up wiki" or "scaffold vault" means run init.
- "check transport" means run detect-transport.
- "check wiki status" means run status.
- "continue wiki" or "resume wiki context" means run continue.
- "ingest this source" means run ingest.
- "ingest this folder" means run ingest-batch.
- "ingest this URL" means run ingest-url.
- "search wiki for X" or "find wiki pages about X" means run search.
- "what does the wiki know about X" means run query.
- "save this insight" means run save.
- "lint the wiki" means run lint.

## Search Behavior

Search is read-only. It ranks durable Markdown wiki pages and returns page paths, titles, snippets, matched terms, and scores before query synthesis.

## Boundaries

- Do not modify Raw Source files.
- Do not generate Claude-specific plugin files.
- Do not claim semantic deep retrieval, vector search, hybrid retrieval, reranking, qmd integration, or LLM synthesis.
- Do not treat slash commands as the only entry path.
