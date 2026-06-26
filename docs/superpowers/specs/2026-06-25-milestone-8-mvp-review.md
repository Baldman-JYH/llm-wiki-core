# Milestone 8 MVP Review

## Goal

Review whether the current MVP reaches the intended core experience: a neutral local LLM Wiki core that can be driven by Codex App / CLI while preserving the practical lessons of `claude-obsidian`.

## Review Standard

The review uses artifact-level equivalence:

- Raw sources are preserved as source material.
- Wiki pages are generated and maintained under a stable Markdown structure.
- Index, log, hot cache, manifest, wikilinks, and lint report are present and verifiable.
- Agent-specific behavior stays in adapters, not in the neutral core.

It does not require byte-for-byte equality of LLM-authored prose.

## Karpathy Pattern Alignment

The MVP aligns with the canonical LLM Wiki pattern by keeping three layers:

- Raw sources in `.raw/`.
- Maintained Wiki pages in `wiki/`.
- Schema and operation contracts in docs and code-level validation.

The resulting artifact is a durable Markdown wiki rather than a chat transcript.

## Reference Implementation Alignment

The MVP preserves the key `claude-obsidian` effects that belong in a neutral core:

- initialize a vault structure
- ingest source material
- update manifest, index, log, and hot cache
- query from maintained wiki pages with citations
- save durable insights back into wiki pages
- lint structure, frontmatter, wikilinks, and orphan pages

Claude-specific commands, hooks, plugin files, and subagent behavior are intentionally outside the core.

## Codex Local Readiness

The current Codex adapter assets cover the local Codex App / CLI path:

- repo-local `AGENTS.template.md`
- command mapping in `integrations/codex/COMMANDS.md`
- Codex skill draft under `integrations/codex/skills/llm-wiki/`
- PowerShell and shell installer entrypoints
- CLI commands for init, detect-transport, ingest, query, save, and lint

The MVP supports Windows native PowerShell + Python. Obsidian CLI remains optional, with filesystem as the required fallback.

## Verification

Milestone 8 adds a smoke test for the core loop:

`init -> detect-transport -> ingest -> query -> save -> lint`

This test proves the MVP can produce the expected artifact structure without requiring global Codex installation or modifications to `claude-obsidian`.

## Verdict

The MVP reaches core-loop equivalence for the local Codex target. It is suitable as a综合实践案例 for the Karpathy LLM Wiki idea, using `claude-obsidian` as the reference implementation rather than as code to copy.

It is not yet full feature parity with `claude-obsidian`.

## Remaining Gaps

- actual Obsidian CLI read / write / search integration beyond detection
- richer LLM-assisted synthesis and stale-claim review
- URL ingest, batch ingest, and image ingest
- Obsidian CLI integration tests against an installed CLI
- marketplace-quality Codex plugin packaging
- Claude adapter extraction from the existing reference implementation
