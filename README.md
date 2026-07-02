# llm-wiki-core

`llm-wiki-core` is a neutral local LLM Wiki practice implementation. The canonical abstraction is [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): raw materials stay durable, and the agent maintains a Markdown wiki instead of leaving knowledge trapped in chat. [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) is the reference implementation for the Claude Code + Obsidian workflow, while `llm-wiki-core` focuses on a neutral, testable core that does not claim full parity with `claude-obsidian`.

Current release: `v0.2.0-mvp`.
Current status: R3.3 adds local read-only wiki search on top of the R3.2 URL ingest flow.

## Project Positioning

- Karpathy's gist is the canonical abstract idea.
- `AgriciDaniel/claude-obsidian` is the Claude Code + Obsidian reference implementation.
- `llm-wiki-core` is a neutral practice implementation for Codex App, Codex CLI, and future local agents.

## Capabilities

- Initialize a standard local LLM Wiki vault.
- Preserve raw source inputs under `.raw/`.
- Track source metadata and provenance in `.raw/.manifest.json`.
- Ingest one local Markdown source with `ingest`.
- Ingest local Markdown folders with `ingest-batch`.
- Ingest one explicit URL into an immutable `.raw/url/` snapshot with `ingest-url`.
- Search durable Markdown wiki pages with dependency-free BM25-style lexical retrieval.
- Query, save, resume, and lint the wiki.
- Use filesystem transport as the default portable runtime path.
- Treat the official `obsidian` CLI as optional and verified-only.

## Quick Start

### Install

```powershell
git clone https://github.com/Baldman-JYH/llm-wiki-core.git
cd llm-wiki-core
python -m pip install -e .
python -m llm_wiki_core --version
```

### Initialize A Vault

```powershell
llm-wiki init <vault> --purpose "Research local LLM wiki workflows"
llm-wiki detect-transport <vault> --force
```

### Ingest Sources

```powershell
llm-wiki ingest <vault> .raw/articles/example.md
llm-wiki ingest-batch <vault> .raw/articles
llm-wiki ingest-url <vault> https://example.com/article
```

### Search, Query, And Maintain

```powershell
llm-wiki status <vault>
llm-wiki status <vault> --json
llm-wiki continue <vault>
llm-wiki search <vault> "durable wiki knowledge"
llm-wiki query <vault> "What does the wiki know about this source?"
llm-wiki save <vault> --title "Saved Insight" --content "Durable insight text."
llm-wiki lint <vault>
```

## Machine-Readable Output

Operational commands that report status or ingest results support `--json` for machine-readable JSON output. This keeps Codex App, Codex CLI, and future adapters on a stable contract while preserving human-readable defaults.

```powershell
llm-wiki status <vault> --json
llm-wiki ingest-url <vault> https://example.com/article --json
llm-wiki search <vault> "durable wiki knowledge" --limit 5 --json
```

## Command Reference

| Command | Purpose |
|---|---|
| `llm-wiki init <vault> --purpose "..."` | Initialize a local wiki vault. |
| `llm-wiki detect-transport <vault> --force` | Record runtime transport capability metadata. |
| `llm-wiki ingest <vault> <source>` | Ingest one local Markdown source under `.raw/`. |
| `llm-wiki ingest-batch <vault> <source-root>` | Ingest local Markdown files discovered under `.raw/`. |
| `llm-wiki ingest-url <vault> <url>` | Fetch one explicit URL, store an immutable `.raw/url/` snapshot, and ingest the normalized Markdown source. |
| `llm-wiki status <vault>` | Inspect initialization and source status. |
| `llm-wiki continue <vault>` | Re-enter current wiki context. |
| `llm-wiki search <vault> "<query>"` | Search ranked local wiki pages with dependency-free BM25-style lexical retrieval. |
| `llm-wiki query <vault> "<question>"` | Query the wiki using current wiki context and ranked pages. |
| `llm-wiki save <vault> --content "..."` | Save durable insight back into the wiki. |
| `llm-wiki lint <vault>` | Check wiki health and write a lint report. |

## Artifact Layout

```text
<vault>/
  AGENTS.md
  .raw/
    .manifest.json
    url/
  wiki/
    index.md
    log.md
    hot.md
    overview.md
    sources/
    entities/
    concepts/
    questions/
    comparisons/
    meta/
```

- `.raw/` stores preserved raw inputs.
- `.raw/url/` stores immutable URL ingest snapshots.
- `wiki/` stores durable Markdown knowledge artifacts.

## Codex Adapter

The Codex adapter assets live under `integrations/codex/`. Repo-local install scripts initialize a vault and print re-entry commands. User-level skill packaging is being prepared in R4.0.

Codex entry points must call the neutral core commands instead of redefining LLM Wiki behavior. Natural-language triggers are required; slash commands are a target UX layer.

## Current Boundaries

- URL ingest creates immutable `.raw/url/` snapshots.
- R3.2 is text-only. It does not include full readability, defuddle, JavaScript rendering, authenticated pages, or crawling.
- R3.3 search is read-only and searches durable Markdown wiki pages by default.
- R3.3 uses dependency-free BM25-style lexical retrieval.
- R3.3 remains text-first on top of the R3.2 URL ingest foundation.
- Vector search, hybrid retrieval, reranking, raw-source search by default, qmd integration, and LLM synthesis remain deferred.
- Full readability, defuddle, JavaScript rendering, authenticated pages, and crawling remain deferred.
- Binary or non-decodable responses are rejected instead of being archived through the text transport.
- The official `obsidian` CLI remains optional and verified-only; filesystem fallback stays available.

## Documentation

- [User guide](docs/user-guide.md)
- [Operation contract](docs/operation-contract.md)
- [Completion criteria](docs/completion-criteria.md)
- [Roadmap](docs/roadmap.md)
- [Roadmap schedule](docs/roadmap-schedule.md)
- [Release readiness checklist](docs/release-readiness-checklist.md)
- [v0.1.0 MVP release notes](docs/release-notes-v0.1.0-mvp.md)
- [Archive manifest](docs/archive-manifest.md)

## Roadmap

- R1: hardening.
- R2: verified optional runtime transport for the official `obsidian` CLI.
- R3: ingest and retrieval expansion, including local Markdown batch ingest, URL ingest, and local wiki search.
- R4: adapter expansion.
- R5: knowledge-organization extensions.

See [docs/roadmap-schedule.md](docs/roadmap-schedule.md) for the prioritized schedule.

## Development

```powershell
python -m pip install -e .
python -m pytest
```

## License

The repository does not yet ship a final `LICENSE` file.
