# User Guide

Date: 2026-06-26

This guide is for local Codex App and Codex CLI users who want to use `llm-wiki-core` as a neutral LLM Wiki practice implementation.

The canonical abstract idea is Karpathy's LLM Wiki pattern: humans choose sources and ask questions; the LLM maintains a durable Markdown Wiki instead of leaving knowledge trapped in chat history. [`claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian) is a reference implementation for the Claude Code + Obsidian workflow. `llm-wiki-core` keeps the core neutral so Codex and future local agents can produce artifact-level equivalence: the same kind of durable folders, files, metadata, wikilinks, logs, hot context, and lint results, without requiring byte-for-byte equality of LLM-authored prose.

## Prerequisites

- Python 3.10 or newer.
- Local Codex App or Codex CLI.
- Windows users can use native PowerShell. WSL and Git Bash are not required for the MVP.
- Obsidian CLI is optional and not required.

## Install

From the project root:

```powershell
cd <repo>
python -m pip install -e .
llm-wiki --version
```

If the console script is not visible in the current shell, use the Python module fallback from the same environment:

```powershell
python -m llm_wiki_core --version
python -m llm_wiki_core init <vault> --purpose "Research local LLM wiki workflows"
```

For a Codex-oriented install flow:

```powershell
cd <repo>\integrations\codex\install
.\install.ps1 -VaultPath <vault> -Purpose "Research local LLM wiki workflows"
```

Dry run:

```powershell
.\install.ps1 -VaultPath <vault> -Purpose "Research local LLM wiki workflows" -DryRun
```

macOS and Linux shell users can use:

```sh
cd /path/to/llm-wiki-core/integrations/codex/install
./install.sh /path/to/vault "Research local LLM wiki workflows"
./install.sh --dry-run /path/to/vault "Research local LLM wiki workflows"
```

## Create A Vault

```powershell
llm-wiki init <vault> --purpose "Research local LLM wiki workflows"
llm-wiki detect-transport <vault> --force
```

Expected core artifacts:

- `.raw/`
- `.raw/.manifest.json`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/hot.md`
- `wiki/overview.md`
- `wiki/sources/`
- `wiki/entities/`
- `wiki/concepts/`
- `wiki/questions/`
- `wiki/comparisons/`
- `wiki/meta/`
- `AGENTS.md`

The current implemented runtime transport is `filesystem`. A transport snapshot may record whether Obsidian CLI is available, but `filesystem` remains the runtime path until runtime eligibility is verified.

## Optional Obsidian CLI Runtime

Obsidian CLI is not required. The default portable path remains filesystem fallback.

When the official `obsidian` CLI is installed, enabled in Obsidian, and verified against the target vault, `llm-wiki-core` may use it for read/write/append/list/search.

If verification fails, commands continue through filesystem fallback.

The legacy `obsidian-cli` command is not used as an R2 runtime transport.

## Add Raw Sources

Put source material under `.raw/`. The raw source is treated as preserved input. Example:

```powershell
New-Item -ItemType Directory -Force <vault>\.raw\articles
Set-Content -LiteralPath <vault>\.raw\articles\example.md -Encoding UTF8 -Value "# Example Source`n`nDurable knowledge should be organized into Markdown Wiki artifacts."
```

Ingest it:

```powershell
llm-wiki ingest <vault> .raw\articles\example.md
```

Expected result:

- the raw file remains unchanged;
- `.raw/.manifest.json` records source status and fingerprint;
- `wiki/sources/Example.md` or an equivalent title-derived source page is created;
- `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md` are updated.

## Batch Ingest Raw Sources

R3.1 supports local Markdown batch ingest for `.md` files that already live under `.raw/`.

```powershell
llm-wiki ingest-batch <vault> .raw/articles
llm-wiki ingest-batch <vault> .raw/articles --force
llm-wiki ingest-batch <vault> .raw/articles --json
```

Expected result:

- each discovered `.md` source is processed through the same ingest path as `llm-wiki ingest`;
- unchanged sources are counted as skipped unless `--force` is used;
- per-source failures are reported without blocking unrelated sources;
- raw files remain unchanged.

## URL Ingest

R3.2 adds a narrow URL ingest path for one explicit HTTP or HTTPS URL at a time.

```powershell
llm-wiki ingest-url <vault> https://example.com/article
```

Expected snapshot contents under `.raw/url/`:

- decoded raw response text saved as an immutable snapshot payload;
- metadata describing the request/response provenance;
- a normalized Markdown `source.md` file that existing ingest can process.

R3.2 remains text-only. It does not include full readability, defuddle, JavaScript rendering, authenticated pages, or crawling. Binary or non-decodable responses are rejected before wiki pages are updated.

HTML cleanup, image ingest, deep retrieval, vector search, and LLM synthesis remain outside R3.2.
For the historical R3.1 boundary, URL ingest, HTML cleanup, image ingest, deep retrieval, vector search, and LLM synthesis were outside R3.1.

## Re-Enter Context

Use these commands when opening the vault again in Codex App or Codex CLI:

```powershell
llm-wiki status <vault>
llm-wiki continue <vault>
```

`status` summarizes initialization, source count, runtime transport, missing required paths, and lint report hints. `continue` reads `wiki/hot.md`, `wiki/index.md`, and `wiki/log.md` so the agent can recover recent Wiki context without relying on chat history.

## Query And Save

Ask questions against the current Wiki:

```powershell
llm-wiki query <vault> "What does the wiki know about durable LLM knowledge?"
```

Save a durable insight:

```powershell
llm-wiki save <vault> --title "Durable LLM Knowledge" --content "The durable artifact is the Markdown Wiki, not the chat transcript."
```

Saved insights create pages under `wiki/questions/` by default and update `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.

## Machine-Readable CLI Output

Every command supports optional `--json` output. Use this mode when Codex App, Codex CLI, CI, or a local automation script needs a stable result object instead of human-oriented text.

```powershell
llm-wiki status <vault> --json
llm-wiki ingest <vault> .raw/articles/example.md --json
llm-wiki ingest-batch <vault> .raw/articles --json
llm-wiki ingest-url <vault> https://example.com/article --json
llm-wiki lint <vault> --json
```

Successful results include `operation` and `status`. Failed results return one JSON object with `"status": "error"` and details under `error.type` and `error.message`.

## Lint

```powershell
llm-wiki lint <vault>
```

Lint checks required paths, manifest JSON, frontmatter, dead wikilinks, orphan pages, and writes a stable report under `wiki/meta/`.

## Codex Usage Pattern

After initialization, Codex App and Codex CLI can follow the generated `AGENTS.md`.

Useful natural language triggers include:

- "set up wiki"
- "check wiki status"
- "resume wiki context"
- "ingest this source"
- "query wiki"
- "save this insight"
- "lint wiki"

The adapter assets are repo-local. The MVP does not automatically install global Codex configuration or publish a marketplace plugin.

## What Is Ready

- Local editable install.
- Windows native PowerShell install path.
- Codex App / Codex CLI command discovery through generated `AGENTS.md`.
- Filesystem transport read/write/search.
- `init`, `detect-transport`, `ingest`, `query`, `save`, `status`, `continue`, and `lint`.
- Local `.md` batch ingest under `.raw/`.
- URL ingest with immutable `.raw/url/` snapshots.
- Automated artifact-level equivalence verification for the core local loop.

## Current Boundaries

- Official `obsidian` CLI read/write/append/list/search is used only after vault binding and capability verification; otherwise filesystem fallback remains active.
- Full `claude-obsidian` parity is not claimed.
- Claude Code plugin/hooks/subagent behavior is not implemented in neutral core.
- HTML cleanup, image ingest, deep retrieval, vector search, LLM synthesis, and marketplace publishing are outside R3.2.
- R3.2 URL ingest is text-only and rejects binary or non-decodable responses.
- Byte-for-byte equality of LLM-authored prose is intentionally not required for an LLM Wiki.

## Troubleshooting

- If `llm-wiki` is not found, rerun `python -m pip install -e .` from the project root.
- If the shell still cannot find `llm-wiki`, use `python -m llm_wiki_core ...` as the equivalent local fallback.
- If transport detection records Obsidian CLI, remember that runtime selection still uses filesystem fallback until the official `obsidian` CLI verifies successfully.
- If lint reports high-severity dead links, inspect the generated `wiki/meta/lint-report-YYYY-MM-DD.md`.
- On Windows, prefer PowerShell commands and UTF-8 text files.
