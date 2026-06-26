# Milestone 20 Release Readiness / User Guide Design

## Goal

Turn the verified MVP into a locally usable practice package by documenting the exact path a Codex App / Codex CLI user can follow from install to daily use.

## Canonical Alignment

- Karpathy's LLM Wiki gist remains the canonical abstract idea.
- `D:/ai/llmWiki/claude-obsidian` remains the Claude Code + Obsidian reference implementation.
- `llm-wiki-core` is the neutral practice implementation that should produce artifact-level equivalent Markdown Wiki results for local agents.
- The release docs must describe artifact-level equivalence, not byte-for-byte equality of LLM-authored prose.

## User Path

The user guide must cover:

1. install the editable local package;
2. initialize a vault;
3. detect transport;
4. place source material under `.raw/`;
5. ingest one source;
6. inspect status and continue context;
7. query and save durable knowledge;
8. lint the Wiki.

## Release Readiness Boundary

Ready for MVP local use means:

- the filesystem transport is the implemented runtime path;
- Codex App / CLI users can operate through generated `AGENTS.md`, natural-language triggers, and `llm-wiki` commands;
- artifact-level equivalence is automatically verified;
- Windows native PowerShell is supported without requiring WSL or Git Bash.

It does not mean full `claude-obsidian` parity:

- actual Obsidian CLI read/write/search is not implemented;
- Claude Code plugin/hooks/subagent behavior is not implemented in neutral core;
- URL ingest, batch ingest, deep retrieval, vector search, and LLM synthesis are out of MVP scope.

## Verification

Add a static documentation coverage test so the release guide, checklist, and README cannot silently lose critical commands or boundary language.
