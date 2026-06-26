# Milestone 19 Artifact Equivalence Verification Design

## Goal

Verify that the MVP produces artifact-level equivalent LLM Wiki output for local Codex App / CLI usage.

## Scope

This milestone verifies the core user promise:

- a user can initialize a vault;
- preserve raw sources;
- ingest raw source into durable Wiki pages;
- maintain manifest, index, log, and hot cache;
- query with wikilink citations;
- save durable insight;
- continue from recent context;
- lint the final Wiki cleanly.

## Equivalence Definition

Artifact-level equivalence means checking stable Wiki artifacts, not byte-for-byte LLM-authored prose.

The verification compares:

- folder and file structure;
- required Markdown pages;
- YAML frontmatter fields;
- manifest source metadata;
- raw source immutability;
- wikilinks;
- index/log/hot updates;
- query citations;
- saved insight placement;
- status and continue re-entry behavior;
- lint counts and report path.

## Non-Goals

- Do not compare generated prose byte-for-byte against `claude-obsidian`.
- Do not require actual Obsidian CLI.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not install global Codex configuration.
- Do not implement new product behavior.

## Verification Matrix

| Layer | Checks |
|---|---|
| Structure | `.raw`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`, source/concept/entity/question/meta folders, `AGENTS.md` |
| Transport | snapshot exists, filesystem is preferred implemented runtime, Obsidian CLI is not required |
| Ingest | raw source unchanged, source page created, manifest fingerprint recorded, index/log/hot updated |
| Query | answer cites Wiki page, query does not mutate Wiki |
| Save | question page created, frontmatter present, index/log/hot updated |
| Re-entry | status reports initialized/source count/runtime transport, continue reads hot/index/log |
| Lint | blocker/high/medium/low are zero after the full MVP flow |

