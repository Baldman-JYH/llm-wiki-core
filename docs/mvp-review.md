# MVP Review

`llm-wiki-core` currently satisfies the MVP core-loop requirement for local Codex App / CLI usage.

## Conclusion

The project is aligned with Karpathy's LLM Wiki idea as the canonical abstraction, and uses `claude-obsidian` as a reference implementation for practical behavior. The MVP produces a durable Markdown Wiki with raw source preservation, generated source pages, manifest records, index/log/hot updates, query citations, saved insights, and lint reports.

The equivalence target is artifact-level equivalence, not byte-for-byte equality of generated prose.

## What Is Equivalent

- Vault scaffold and stable folder layout.
- Raw source preservation under `.raw/`.
- Source ingest into `wiki/sources/`.
- Manifest, index, log, and hot cache maintenance.
- Query answers grounded in wiki pages with wikilink citations.
- Save operation for durable question/concept pages.
- Lint checks for required structure, frontmatter, dead wikilinks, orphan pages, and manifest shape.
- Local Codex-facing instructions, command mapping, skill draft, and installer entrypoints.

## What Remains Adapter-Specific

- Codex App / CLI instructions and install entrypoints stay under `integrations/codex/`.
- Claude Code plugin, commands, hooks, and subagent behavior remain outside the neutral core.
- Obsidian CLI is a detected future integration boundary; filesystem remains the current preferred implemented runtime transport.

## Current Non-Goals

- Full `claude-obsidian` feature parity.
- Byte-for-byte generated Markdown prose equality.
- Codex Web / Remote support.
- Global Codex configuration mutation.
- Marketplace plugin publishing.
- URL, batch, image, autoresearch, canvas, hybrid retrieval, or DragonScale workflows.

## Next Recommended Work

1. Keep operation transport usage consistent so all MVP operations rely on implemented transport semantics.
2. Implement actual Obsidian CLI read / write / search integration behind the current detection contract when it can be tested safely.
3. Begin extracting a Claude adapter plan without modifying the upstream `claude-obsidian` repository.
