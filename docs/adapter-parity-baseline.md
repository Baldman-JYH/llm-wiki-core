# Adapter Parity Baseline

Date: 2026-07-02

## Positioning

Karpathy's LLM Wiki gist is the canonical abstract pattern.

https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

`AgriciDaniel/claude-obsidian` is a reference implementation case for Claude Code + Obsidian.

https://github.com/AgriciDaniel/claude-obsidian

`llm-wiki-core` is the neutral implementation layer for local durable Markdown Wiki artifacts. It should absorb the reusable LLM Wiki rules while keeping agent-specific command surfaces in adapters.

## Parity Definition

Artifact-level parity is required.

Byte-for-byte parity is not required.

Codex App, Codex CLI, and a future Claude Code adapter should be considered equivalent when they produce compatible durable outcomes:

- same vault structure;
- same raw-source immutability rule;
- same page categories;
- compatible frontmatter and wikilinks;
- updated `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`;
- equivalent operation logs;
- equivalent lint and health checks;
- equivalent command intent mapping.

The project must not claim full `claude-obsidian` feature parity until those features are implemented and verified in their own milestones.

## Layer Boundaries

### Neutral Core

The neutral core owns durable artifacts and portable operations:

- `init`
- `detect-transport`
- `status`
- `continue`
- `ingest`
- `ingest-batch`
- `ingest-url`
- `search`
- `query`
- `save`
- `lint`

The core owns file formats, raw-source preservation, frontmatter policy, wikilink policy, transport contracts, index maintenance, log maintenance, hot context maintenance, and lint health.

### Codex Adapter

The Codex adapter owns local Codex App and Codex CLI usage:

- Codex skill instructions;
- natural-language trigger mapping;
- `AGENTS.md` template guidance;
- repo-local installation guidance;
- explicit user-level skill installation;
- future optional Codex plugin packaging.

The Codex adapter maps user intent to neutral core commands. It does not reimplement core behavior.

### Claude Adapter

The future Claude adapter should own Claude Code-specific behavior:

- `CLAUDE.md` or equivalent schema guidance;
- slash commands such as `/wiki` and `/save`;
- hook configuration;
- subagent descriptions;
- Claude-specific installation packaging.

Claude Code hooks and subagents are adapter-only behavior. They are not neutral core behavior.

## Command Intent Mapping

| Intent | Codex surface | Claude surface | Neutral command |
|---|---|---|---|
| Set up a wiki | `set up wiki` | `/wiki` | `llm-wiki init <vault> --purpose "..."` |
| Check transport | `check transport` | `/wiki transport` | `llm-wiki detect-transport <vault>` |
| Check status | `check wiki status` | `/wiki status` | `llm-wiki status <vault>` |
| Continue context | `continue wiki` | `/wiki` on existing vault | `llm-wiki continue <vault>` |
| Ingest one source | `ingest this source` | `/wiki ingest <source>` | `llm-wiki ingest <vault> <source>` |
| Ingest a folder | `ingest this folder` | `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` |
| Ingest a URL | `ingest this URL` | `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` |
| Search pages | `search wiki for X` | `/wiki search X` | `llm-wiki search <vault> "X"` |
| Ask a question | `what does the wiki know about X` | `/wiki query X` | `llm-wiki query <vault> "X"` |
| Save insight | `save this insight` | `/save` | `llm-wiki save <vault> --title "..." --content "..."` |
| Lint health | `lint the wiki` | `/wiki lint` | `llm-wiki lint <vault>` |

## Deferred Capabilities

The following capabilities from the `claude-obsidian` reference remain deferred until separate designs approve them:

- `autoresearch`;
- canvas workflows;
- hybrid retrieval and reranking;
- DragonScale or log-folding memory;
- methodology modes such as LYT, PARA, and Zettelkasten;
- multi-agent batch orchestration;
- Obsidian-specific dashboards, bases, plugins, and advanced templates;
- Claude Code hooks that mutate local state;
- Claude Code subagents;
- marketplace-grade Codex plugin packaging;
- automatic Git commits.

## Verification Rule

R4.2 is a documentation and guard-test milestone. It should require no live Claude Code, Obsidian, or Codex App process.
