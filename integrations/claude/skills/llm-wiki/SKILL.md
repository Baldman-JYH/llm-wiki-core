---
name: llm-wiki
description: Claude local adapter MVP for maintaining a durable Markdown LLM Wiki through neutral llm-wiki commands.
---

# LLM Wiki Claude Skill

Claude local adapter MVP for `llm-wiki-core`.

Use this skill when the user asks to set up, continue, ingest, search, query, save, or lint an LLM Wiki.

## Source Of Truth

Karpathy's LLM Wiki gist is the canonical abstract pattern.

`AgriciDaniel/claude-obsidian` is a reference implementation case.

## Non-Negotiable Rules

- Do not modify `.raw/` files.
- Do not reimplement neutral core file-writing behavior in prompt text.
- Do not claim full `claude-obsidian` parity.
- Do not enable active hooks.
- Do not use Claude subagents.
- Do not edit user-global Claude settings.

## Command Mapping

- `/wiki` on a new vault: `llm-wiki init <vault> --purpose "..."`.
- `/wiki` on an existing vault: `llm-wiki continue <vault>`.
- `/wiki transport`: `llm-wiki detect-transport <vault>`.
- `/wiki status`: `llm-wiki status <vault>`.
- `/wiki ingest <source>`: `llm-wiki ingest <vault> <source>`.
- `/wiki ingest-batch <source-root>`: `llm-wiki ingest-batch <vault> <source-root>`.
- `/wiki ingest-url <url>`: `llm-wiki ingest-url <vault> <url>`.
- `/wiki search <query>`: `llm-wiki search <vault> "<query>"`.
- `/wiki query <question>`: `llm-wiki query <vault> "<question>"`.
- `/save`: `llm-wiki save <vault> --title "..." --content "..."`.
- `/wiki lint`: `llm-wiki lint <vault>`.

## Deferred In R4.3

Active Claude hooks are deferred.

Claude subagents are deferred.

.claude-plugin packaging is deferred.

Autoresearch is deferred.

Canvas workflows are deferred.

DragonScale memory is deferred.

Methodology modes are deferred.

Automatic Git commits are deferred.
