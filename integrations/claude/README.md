# Claude Adapter

Claude Code adapter work is future adapter work.

It should reconstruct Claude-specific surfaces from the `AgriciDaniel/claude-obsidian` reference implementation without moving those surfaces into neutral core.

## Role

The Claude adapter should map Claude Code interaction patterns to the same neutral `llm-wiki-core` operations used by the Codex adapter.

The neutral core owns durable Markdown Wiki artifacts. The Claude adapter owns Claude Code ergonomics.

## Command Mapping Baseline

| Claude surface | Neutral target |
|---|---|
| `/wiki` | `llm-wiki init`, `llm-wiki continue`, or a specific `/wiki` subcommand depending on vault state |
| `/wiki transport` | `llm-wiki detect-transport <vault>` |
| `/wiki status` | `llm-wiki status <vault>` |
| `/wiki ingest <source>` | `llm-wiki ingest <vault> <source>` |
| `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` |
| `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` |
| `/wiki search <query>` | `llm-wiki search <vault> "<query>"` |
| `/wiki query <question>` | `llm-wiki query <vault> "<question>"` |
| `/wiki lint` | `llm-wiki lint <vault>` |
| `/save` | `llm-wiki save <vault> --title "..." --content "..."` |

## Adapter-Only Behavior

Claude Code hooks are adapter-only.

Claude Code subagents are adapter-only.

Claude slash commands are adapter-only.

No `.claude-plugin` package is generated in R4.2.

No Claude hook or subagent file is generated in R4.2.

## Deferred Reference Features

The following `AgriciDaniel/claude-obsidian` reference features remain deferred until separate designs approve them:

- `autoresearch`;
- canvas workflows;
- hybrid retrieval and reranking;
- DragonScale or log-folding memory;
- methodology modes;
- Obsidian-specific dashboards, bases, plugins, and advanced templates;
- automatic Git commits.

## Parity Rule

Claude and Codex should target artifact-level parity: compatible vault structure, raw-source rules, metadata, wikilinks, index, log, hot context, query behavior, save behavior, and lint health.

Byte-for-byte LLM prose parity is not required.
