# Milestone 10 Operation Transport Adoption Design

## Goal

Begin moving core operations onto the neutral transport layer without changing user-facing operation behavior.

This milestone adopts `FilesystemTransport` for `query` and `lint` first because they are read-heavy and lower risk than `ingest` and `save`.

## Context

Milestone 9 added safe filesystem transport primitives. The next step is to prove operations can use that transport contract instead of direct `Path.read_text()` and `Path.rglob()` calls.

This keeps `llm-wiki-core` aligned with the Karpathy LLM Wiki pattern: transport remains a thin file access channel that supports the maintained Markdown Wiki. It does not become a retrieval engine, app framework, or Obsidian dependency.

## Scope

Implement:

- Optional `transport` injection for `query_wiki`.
- Optional `transport` injection for `lint_wiki`.
- Query page discovery and reading through transport.
- Lint required path checks, manifest reads, Markdown page reads, and report writes through transport.
- A small `exists(relative_path)` filesystem transport method if needed by lint.

Keep:

- CLI behavior unchanged.
- Existing result shapes unchanged.
- Existing page ranking semantics unchanged.
- Existing lint finding semantics unchanged.

## Non-Goals

- Do not rewrite `ingest` or `save`.
- Do not introduce Obsidian CLI actual calls.
- Do not add BM25, vector search, hybrid retrieval, or reranking.
- Do not change Raw Source immutability rules.
- Do not change command-line arguments.

## Test Strategy

Add tests that inject spy transports:

- `query_wiki(..., transport=spy)` must read `wiki/hot.md`, `wiki/index.md`, list searchable Markdown roots, and read candidate pages through the spy.
- `lint_wiki(..., transport=spy)` must use transport for existence checks, Markdown listing, page reads, manifest reads, and lint report writes.

Existing tests continue to cover default filesystem behavior.

## Design Decision

The operation functions accept an optional transport object but do not expose transport selection through CLI yet.

This is intentionally conservative:

- Current users see no CLI changes.
- Future adapters can pass a different transport.
- Core operations become easier to test without a physical vault.

