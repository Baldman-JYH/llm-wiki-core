# Milestone 12 Codex Adapter Status Continue Design

## Goal

Expose the new read-only `status` and `continue` operations through the repo-local Codex adapter assets.

## Context

Milestone 11 added:

- `llm-wiki status <vault>`
- `llm-wiki continue <vault>`

Codex users should be able to discover and trigger these operations from the adapter instructions, command mapping, and skill draft.

## Scope

Update:

- `integrations/codex/AGENTS.template.md`
- `integrations/codex/COMMANDS.md`
- `integrations/codex/skills/llm-wiki/SKILL.md`
- adapter asset tests

## Natural Language Triggers

Add mappings for:

- "check wiki status" -> `status`
- "continue wiki" -> `continue`
- "resume wiki context" -> `continue`

## Non-Goals

- Do not change core operation behavior.
- Do not change CLI arguments.
- Do not publish or install a global Codex plugin.
- Do not add Claude-specific files.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Design Decision

`status` and `continue` are read-only workflow entrypoints. They should be presented before mutating workflows because they help Codex inspect the vault and recover context before ingest/query/save/lint.

