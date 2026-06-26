# Milestone 4 Ingest Design

## Goal

Implement deterministic single-source ingest for local files under `.raw/`.

## Confirmed Approach

Use Python core ingest plus a CLI subcommand:

- Core API: `ingest_source(vault_root, source_path, force=False)`
- CLI: `llm-wiki ingest <vault> <source> [--force]`

This MVP reads one local raw source, creates or updates one source summary page, and updates manifest, index, log, and hot cache.

## Scope

The operation:

- accepts vault-relative paths such as `.raw/articles/example.md`
- rejects sources outside `.raw/`
- preserves raw source content unchanged
- computes `sha256:<hex>` fingerprint
- skips unchanged sources unless `force=True`
- writes `wiki/sources/<Human Title>.md`
- updates `.raw/.manifest.json`
- updates `wiki/index.md`
- prepends to `wiki/log.md`
- overwrites `wiki/hot.md` as a cache

## Boundaries

- Do not implement URL ingest.
- Do not implement image / vision ingest.
- Do not create entity or concept pages automatically in this milestone.
- Do not implement batch ingest.
- Do not use LLM calls.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Summary Strategy

The source summary is deterministic:

- title comes from the source filename stem
- summary comes from the first non-empty source content line
- source page records the raw source path and fingerprint

This is intentionally modest. Later milestones can add richer LLM-authored synthesis while keeping the same artifact contract.

## Verification

Tests should validate:

- source outside `.raw/` is rejected
- ingest creates source page, manifest record, and index/log/hot updates
- raw source content is not modified
- unchanged source is skipped without rewriting source page
- `force=True` re-ingests unchanged source
- CLI command prints concise summary
