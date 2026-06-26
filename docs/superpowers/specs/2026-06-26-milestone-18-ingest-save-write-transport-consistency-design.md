# Milestone 18 Ingest Save Write Transport Consistency Design

## Goal

Bring `ingest` and `save` into the same runtime transport model already used by `query`, `lint`, `status`, and `continue`.

## Context

Milestone 17 added runtime transport selection so read-oriented/default operations do not blindly trust transport snapshots. `ingest` and `save` still write directly through `Path`, which works for filesystem but leaves their operation boundary inconsistent with the rest of the core.

The Karpathy LLM Wiki pattern cares most about durable Markdown artifacts. This milestone keeps the artifacts unchanged while routing reads/writes through the implemented filesystem transport abstraction.

## Scope

Implement:

- optional `transport=` injection for `ingest_source`;
- optional `transport=` injection for `save_insight`;
- default runtime selector usage for both operations;
- transport-based read/write for source page, manifest, index, log, and hot updates;
- tests proving injected transport is used for write paths.

## Non-Goals

- Do not change CLI arguments.
- Do not change generated Markdown artifact semantics.
- Do not migrate `init` in this milestone.
- Do not implement actual Obsidian CLI write behavior.
- Do not modify global Codex configuration.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Design Decision

`ingest` and `save` should accept a transport for tests and future adapters, but the default path should remain conservative: `select_runtime_transport(vault_root).transport`, which currently resolves to filesystem.

This keeps the current reliable artifact output while making the operation boundary consistent and ready for future implemented transports.

