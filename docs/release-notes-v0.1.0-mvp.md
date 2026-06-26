# Release Notes: v0.1.0-mvp

Date: 2026-06-26

## Status

`v0.1.0-mvp` marks the MVP Local Complete release for `llm-wiki-core`.

This release is ready for local Codex App and Codex CLI practice use. It implements the neutral LLM Wiki core needed to maintain durable Markdown Wiki artifacts from raw sources, following Karpathy's LLM Wiki pattern and treating `claude-obsidian` as the reference implementation.

## Included

- Neutral Python package and CLI.
- Local editable install.
- `llm-wiki` console script.
- `python -m llm_wiki_core` fallback.
- `python -m llm_wiki_core.cli` fallback.
- Codex App / Codex CLI `AGENTS.md` generation.
- Repo-local Codex adapter assets.
- Windows native PowerShell installer path.
- macOS / Linux shell installer path.
- `filesystem` runtime transport.
- Obsidian CLI availability detection and unimplemented boundary metadata.
- Raw source preservation under `.raw/`.
- Manifest tracking through `.raw/.manifest.json`.
- Wiki scaffold with `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`, and standard folders.
- Single-source ingest.
- Query with wikilink citations and gap reporting.
- Save durable insight to Wiki pages.
- Status and continue commands for cross-session re-entry.
- Lint report generation.
- artifact-level equivalence verification.
- Completion criteria and roadmap docs.

## Not Included

- Obsidian CLI actual read/write/search is not implemented.
- Full claude-obsidian parity is not included.
- Claude Code plugin/hooks/subagent behavior is not included in the neutral core.
- URL ingest is not included.
- Batch ingest is not included.
- Deep retrieval, vector search, and LLM synthesis are not included.
- Marketplace publishing is not included.
- Automatic global Codex configuration is not included.

## Verification

Release verification before local publication:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q
```

Expected result for this release line:

```text
74 passed, 1 skipped
```

The skipped test is the POSIX shell dry-run execution check, which is expected on Windows.

## Release Tag

Local release tag:

```text
v0.1.0-mvp
```

## Archive

The release archive is produced from the local Git tag with `git archive` and documented in `docs/archive-manifest.md`.
