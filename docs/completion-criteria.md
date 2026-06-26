# Completion Criteria

Date: 2026-06-26

## Status

MVP Local Complete.

This means the local Codex App and Codex CLI practice path is complete for the first implementation tier. Full claude-obsidian parity is not the MVP completion criterion.

## Canonical Boundary

- Karpathy's LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is the claude-obsidian reference implementation for Claude Code + Obsidian.
- `llm-wiki-core` is the neutral local practice implementation.
- The target is artifact-level equivalence: durable Markdown structure, raw source preservation, metadata, wikilinks, index/log/hot updates, status/continue re-entry, and lint results.
- Byte-for-byte equality of LLM-authored prose is not required for an LLM Wiki.

## MVP Local Complete Means

- Codex App users can rely on generated `AGENTS.md` and natural language triggers.
- Codex CLI users can run the same local `llm-wiki` commands.
- If `llm-wiki` is not visible on `PATH`, users can run `python -m llm_wiki_core`.
- Windows users can use native PowerShell without WSL or Git Bash.
- The implemented runtime transport is filesystem.
- Obsidian CLI actual read/write/search is not implemented.
- Obsidian CLI detection may record availability, but it does not become runtime preferred until actual read/write/search exists.
- Raw sources stay under `.raw/` and are preserved.
- Wiki artifacts are maintained under `wiki/`.
- `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md` support cross-session continuity.
- `init`, `detect-transport`, `ingest`, `status`, `continue`, `query`, `save`, and `lint` are implemented and tested.

## Evidence Required For MVP Local Complete

- Core smoke test passes.
- Artifact-level equivalence verification passes.
- Release documentation coverage passes.
- Subprocess CLI entrypoint verification passes.
- Local editable install rehearsal has been documented.
- Codex adapter installer rehearsal has been documented.
- Obsidian CLI boundary rehearsal has been documented.
- `claude-obsidian` remains unmodified.

## Not Included In MVP Completion

- Full claude-obsidian parity is not the MVP completion criterion.
- Actual Obsidian CLI read/write/search.
- Claude Code plugin/hooks/subagent behavior.
- URL ingest.
- batch ingest.
- deep retrieval.
- vector search.
- LLM synthesis mode.
- marketplace publishing.
- automatic global Codex configuration.

## When To Call A Future Tier Complete

Future tiers should define their own completion criteria before implementation. Each tier should state:

- which Karpathy LLM Wiki behavior it strengthens;
- whether it belongs in neutral core, Codex adapter, Claude adapter, or deferred tooling;
- which artifacts prove equivalence;
- which manual verification, if any, is required.
