# LLM Wiki Claude Project Instructions

Karpathy's LLM Wiki gist is the canonical abstract pattern.

`AgriciDaniel/claude-obsidian` is a reference implementation case, not the canonical abstraction.

Use the project-local Claude `llm-wiki` skill for wiki work.

## Core Rules

- Raw sources under `.raw/` are immutable.
- Generated Markdown wiki pages are durable artifacts.
- Artifact-level parity is required.
- Byte-for-byte prose parity is not required.
- Do not claim full `claude-obsidian` parity.
- Do not modify `.raw/` files.
- Do not edit user-global Claude settings.

## Command Policy

Map wiki work to neutral `llm-wiki` commands:

- setup or new wiki: `llm-wiki init <vault> --purpose "..."`.
- continue: `llm-wiki continue <vault>`.
- transport check: `llm-wiki detect-transport <vault>`.
- status: `llm-wiki status <vault>`.
- ingest one source: `llm-wiki ingest <vault> <source>`.
- ingest folder: `llm-wiki ingest-batch <vault> <source-root>`.
- ingest URL: `llm-wiki ingest-url <vault> <url>`.
- search: `llm-wiki search <vault> "<query>"`.
- query: `llm-wiki query <vault> "<question>"`.
- save: `llm-wiki save <vault> --title "..." --content "..."`.
- lint: `llm-wiki lint <vault>`.

## Deferred Surfaces

Active Claude hooks are deferred.

Claude subagents are deferred.

.claude-plugin packaging is deferred.

Autoresearch is deferred.

Canvas workflows are deferred.

DragonScale memory is deferred.

Methodology modes are deferred.

Automatic Git commits are deferred.
