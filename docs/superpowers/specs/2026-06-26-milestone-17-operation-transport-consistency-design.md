# Milestone 17 Operation Transport Consistency Design

## Goal

Make core operations consistently choose an implemented runtime transport, even when an existing vault contains an older or overly optimistic transport snapshot.

## Context

Milestone 16 separated transport detection from implementation. New snapshots keep `preferred: filesystem` while Obsidian CLI read/write/search remains unimplemented. Existing vaults may still contain legacy snapshots with `preferred: obsidian-cli`, and future snapshots may contain transports that are detected but not implemented.

The Karpathy LLM Wiki pattern depends on durable Markdown artifacts, not on any specific tool transport. Therefore operations must prefer the transport that can safely maintain those artifacts today.

## Scope

Implement:

- a small runtime transport selector;
- filesystem as the only implemented runtime transport in the MVP;
- graceful fallback when snapshot `preferred` is missing, unavailable, unimplemented, or unsupported;
- use the selector in read-oriented/default-transport operations:
  - `query`;
  - `lint`;
  - `status`;
  - `continue`;
- surface selector warnings in `status` and `continue`.

## Non-Goals

- Do not implement actual Obsidian CLI read/write/search calls.
- Do not migrate `init`, `ingest`, or `save` to an alternate write transport in this milestone.
- Do not modify global Codex configuration.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not add deep retrieval, BM25, vector search, or LLM synthesis.

## Design Decision

`select_runtime_transport(vault_root)` returns a concrete transport that is implemented today. It may read `.vault-meta/transport.json`, but it treats the snapshot as advisory metadata rather than blindly following `preferred`.

For MVP, the selector always returns `FilesystemTransport`, with warnings when a snapshot asks for something unavailable or unimplemented. This is intentionally conservative and keeps current artifacts reliable.

