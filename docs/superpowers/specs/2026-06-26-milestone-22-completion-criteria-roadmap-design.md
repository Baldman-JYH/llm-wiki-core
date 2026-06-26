# Milestone 22 Completion Criteria / Roadmap Design

## Goal

Define what "complete" means for the current local Codex MVP and separate it from future full `claude-obsidian` parity work.

## Rationale

After Milestone 21, the local Codex App / Codex CLI path has core operations, transport selection, installer rehearsals, artifact-level equivalence verification, release documentation, and subprocess CLI fallback. Without a completion definition, future work can expand indefinitely into URL ingest, deep retrieval, Obsidian CLI implementation, Claude-specific behavior, or marketplace publishing.

This milestone creates a stable boundary:

- MVP Local Complete is a valid completion tier.
- Full claude-obsidian parity is not the MVP completion criterion.
- Future work remains visible in a roadmap without being treated as unfinished MVP work.

## Scope

- Add completion criteria.
- Add roadmap.
- Update stale Obsidian CLI wording in early planning docs.
- Link completion docs from README.
- Add static tests so old transport preference claims do not return.

## Non-Goals

- Do not implement new operations.
- Do not implement actual Obsidian CLI read/write/search.
- Do not implement URL ingest, batch ingest, deep retrieval, or Claude adapter behavior.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
