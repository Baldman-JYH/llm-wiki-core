# User Guide

Date: 2026-06-26

This guide is for local Codex App and Codex CLI users who want to use `llm-wiki-core` as a neutral LLM Wiki practice implementation.

The canonical abstract idea is Karpathy's LLM Wiki pattern: humans choose sources and ask questions; the LLM maintains a durable Markdown Wiki instead of leaving knowledge trapped in chat history. `claude-obsidian` is the current Claude Code + Obsidian reference implementation of that idea. `llm-wiki-core` keeps the core neutral so Codex and future local agents can produce artifact-level equivalence: the same kind of durable folders, files, metadata, wikilinks, logs, hot context, and lint results, without requiring byte-for-byte equality of LLM-authored prose.

## Prerequisites

- Python 3.10 or newer.
- Local Codex App or Codex CLI.
- Windows users can use native PowerShell. WSL and Git Bash are not required for the MVP.
- Obsidian CLI is optional. It may be detected, but actual Obsidian CLI read/write/search is not implemented yet.

## Install

From the project root:

```powershell
cd D:\ai\llmWiki\llm-wiki-core
python -m pip install -e .
llm-wiki --version
```

If the console script is not visible in the current shell, use the Python module fallback from the same environment:

```powershell
python -m llm_wiki_core --version
python -m llm_wiki_core init D:\path\to\vault --purpose "Research local LLM wiki workflows"
```

For a Codex-oriented install flow:

```powershell
cd D:\ai\llmWiki\llm-wiki-core\integrations\codex\install
.\install.ps1 -VaultPath D:\path\to\vault -Purpose "Research local LLM wiki workflows"
```

Dry run:

```powershell
.\install.ps1 -VaultPath D:\path\to\vault -Purpose "Research local LLM wiki workflows" -DryRun
```

macOS and Linux shell users can use:

```sh
cd /path/to/llm-wiki-core/integrations/codex/install
./install.sh /path/to/vault "Research local LLM wiki workflows"
./install.sh --dry-run /path/to/vault "Research local LLM wiki workflows"
```

## Create A Vault

```powershell
llm-wiki init D:\path\to\vault --purpose "Research local LLM wiki workflows"
llm-wiki detect-transport D:\path\to\vault --force
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

The current implemented runtime transport is `filesystem`. A transport snapshot may record whether Obsidian CLI is available, but `filesystem` remains the runtime path until Obsidian CLI read/write/search is implemented.

## Add Raw Sources

Put source material under `.raw/`. The raw source is treated as preserved input. Example:

```powershell
New-Item -ItemType Directory -Force D:\path\to\vault\.raw\articles
Set-Content -LiteralPath D:\path\to\vault\.raw\articles\example.md -Encoding UTF8 -Value "# Example Source`n`nDurable knowledge should be organized into Markdown Wiki artifacts."
```

Ingest it:

```powershell
llm-wiki ingest D:\path\to\vault .raw\articles\example.md
```

Expected result:

- the raw file remains unchanged;
- `.raw/.manifest.json` records source status and fingerprint;
- `wiki/sources/Example.md` or an equivalent title-derived source page is created;
- `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md` are updated.

## Re-Enter Context

Use these commands when opening the vault again in Codex App or Codex CLI:

```powershell
llm-wiki status D:\path\to\vault
llm-wiki continue D:\path\to\vault
```

`status` summarizes initialization, source count, runtime transport, missing required paths, and lint report hints. `continue` reads `wiki/hot.md`, `wiki/index.md`, and `wiki/log.md` so the agent can recover recent Wiki context without relying on chat history.

## Query And Save

Ask questions against the current Wiki:

```powershell
llm-wiki query D:\path\to\vault "What does the wiki know about durable LLM knowledge?"
```

Save a durable insight:

```powershell
llm-wiki save D:\path\to\vault --title "Durable LLM Knowledge" --content "The durable artifact is the Markdown Wiki, not the chat transcript."
```

Saved insights create pages under `wiki/questions/` by default and update `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.

## Lint

```powershell
llm-wiki lint D:\path\to\vault
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
- Automated artifact-level equivalence verification for the core local loop.

## Current Boundaries

- Actual Obsidian CLI read/write/search is not implemented.
- Full `claude-obsidian` parity is not claimed.
- Claude Code plugin/hooks/subagent behavior is not implemented in neutral core.
- URL ingest, batch ingest, deep retrieval, vector search, LLM synthesis, and marketplace publishing are outside the MVP.
- Byte-for-byte equality of LLM-authored prose is intentionally not required for an LLM Wiki.

## Troubleshooting

- If `llm-wiki` is not found, rerun `python -m pip install -e .` from `D:\ai\llmWiki\llm-wiki-core`.
- If the shell still cannot find `llm-wiki`, use `python -m llm_wiki_core ...` as the equivalent local fallback.
- If transport detection records Obsidian CLI, remember that the current runtime still uses `filesystem`.
- If lint reports high-severity dead links, inspect the generated `wiki/meta/lint-report-YYYY-MM-DD.md`.
- On Windows, prefer PowerShell commands and UTF-8 text files.
