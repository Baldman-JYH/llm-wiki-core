# Milestone 9 Transport Read Write Search Design

## Goal

Implement the smallest useful transport layer behind the existing transport detection contract.

This milestone makes filesystem transport usable for local Codex App / CLI workflows while keeping Obsidian CLI optional and non-blocking.

## Context

Karpathy's LLM Wiki pattern depends on durable Markdown artifacts, not on a specific app runtime. `claude-obsidian` demonstrates one successful Claude Code + Obsidian implementation, but `llm-wiki-core` needs a neutral transport layer so Codex and future adapters can read, write, list, and search the same vault artifacts.

## Scope

Implement:

- `TransportError`
- `PathOutsideVaultError`
- `SearchResult`
- `FilesystemTransport`
- `read_text(relative_path)`
- `write_text(relative_path, content)`
- `append_text(relative_path, content)`
- `list_markdown(root="wiki")`
- `search_text(query, root="wiki")`

Update:

- transport package exports
- transport documentation
- README status
- progress document

## Non-Goals

- Do not implement actual Obsidian CLI calls.
- Do not add MCP or REST transport.
- Do not add BM25, vector search, hybrid retrieval, or reranking.
- Do not change ingest, query, save, or lint domain semantics.
- Do not allow transport to bypass the Raw Source immutability rule.

## Path Rules

All public methods accept vault-relative paths.

The transport must reject:

- absolute paths
- `..` traversal
- paths that resolve outside the vault root

Paths may include spaces and non-ASCII characters.

## Search Rules

`search_text` is deterministic local substring search:

- case-insensitive
- Markdown files only
- returns vault-relative paths
- includes 1-based line numbers
- includes the matching line text
- searches under `wiki/` by default

This is a basic transport utility, not retrieval or synthesis.

## Alignment

This milestone supports the LLM Wiki pattern by making the maintained Markdown Wiki easier for agents to operate on. It does not replace the schema, index, log, hot cache, or operation contracts.

Filesystem transport is the required fallback. Obsidian CLI remains a future optional adapter over the same transport contract.

