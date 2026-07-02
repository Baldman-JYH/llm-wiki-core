# Agent Behavioral Contract

This document defines behavior that every LLM Wiki adapter must preserve.

## Highest Principle

The wiki is the durable artifact. Chat is only the interface.

## Startup Behavior

When entering an initialized vault, an agent should read project instructions, then `wiki/hot.md`, `wiki/index.md`, and recent `wiki/log.md` entries as needed.

## Ingest Behavior

Agents must read raw sources without modifying them, update source summaries, maintain index/log/hot, and record provenance in `.raw/.manifest.json`.

## Search Behavior

Search is read-only and returns ranked durable wiki pages before query synthesis.

## Query Behavior

Query reads `wiki/hot.md`, reads `wiki/index.md`, selects only necessary relevant pages, cites wiki pages, and reports gaps when coverage is missing.

## Save Behavior

Save durable knowledge, not transient chat noise. Saved content must update the corresponding wiki page, index, log, and hot cache.

## Lint Behavior

Lint checks frontmatter, wikilinks, orphan pages, index coverage, recent log entries, hot cache health, and manifest parseability.

## Adapter Parity

Artifact-level equivalence is required; byte-for-byte LLM prose equivalence is not required.

Adapters should produce equivalent files, metadata, links, logs, and validation results for the same operation.

## Forbidden Behavior

- Do not modify Raw Source files.
- Do not bypass index/log/hot maintenance.
- Do not treat Claude-specific hooks, commands, or subagents as neutral core requirements.
- Do not claim vector search, hybrid retrieval, reranking, qmd integration, or LLM synthesis unless those features are explicitly implemented.
