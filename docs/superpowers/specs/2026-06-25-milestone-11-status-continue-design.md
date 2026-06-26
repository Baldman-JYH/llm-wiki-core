# Milestone 11 Status Continue Design

## Goal

Add minimal `status` and `continue` operations so local Codex App / CLI users can inspect a vault and resume recent LLM Wiki context.

## Context

Karpathy's LLM Wiki pattern treats the Wiki as persistent working memory. `claude-obsidian` reinforces this with `hot.md`, `index.md`, and `log.md` as the re-entry path for future agent sessions. `llm-wiki-core` already creates and maintains these files; Milestone 11 adds read-only operations that expose their current state.

## Scope

Implement:

- `status_wiki(vault_root, transport=None)`
- `continue_wiki(vault_root, transport=None)`
- CLI subcommands:
  - `llm-wiki status <vault>`
  - `llm-wiki continue <vault>`

`status` reports:

- whether required vault files and folders exist
- missing required paths
- manifest source count
- preferred transport from `.vault-meta/transport.json` when present
- recent log headline
- next suggested action

`continue` reports:

- hot cache text
- index text
- recent log entries
- files read
- next suggested action

## Non-Goals

- Do not write or repair Wiki files.
- Do not run lint automatically.
- Do not generate LLM summaries.
- Do not change init/ingest/query/save/lint behavior.
- Do not call Obsidian CLI.

## Transport Use

Both operations should accept optional transport injection and default to `FilesystemTransport(vault_root)`.

This keeps the operations neutral and testable while preserving CLI behavior.

## Status Semantics

Status values:

- `success`: all required paths exist.
- `incomplete`: at least one required path is missing.

`status` must never create missing files.

## Continue Semantics

Status values:

- `success`: at least hot, index, or log content is available.
- `needs_init`: none of the continuation files are available.

`continue` must never create or update files.

