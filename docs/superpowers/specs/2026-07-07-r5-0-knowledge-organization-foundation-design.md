# R5.0 Knowledge Organization Foundation Design

## Status

Approved for implementation planning.

## Context

The project has completed the local MVP for Codex App, Codex CLI, and a project-local Claude adapter MVP. The remaining roadmap now moves from adapter parity toward knowledge organization.

The canonical abstraction remains Karpathy's LLM Wiki pattern: humans provide raw sources, the agent maintains a durable Markdown wiki, and the wiki keeps index, log, hot context, schema, links, and lintable health. `AgriciDaniel/claude-obsidian` remains a reference implementation case, not the source of every core requirement.

The current MVP only supports `generic` organization mode. That was intentional: first prove the raw source / wiki / schema loop, then add optional organization methods. R5.0 is the transition point where the core gains a neutral organization contract without making LYT, PARA, Zettelkasten, DragonScale, or any other method a first-use prerequisite.

## Problem

`init` currently owns the generic scaffold directly. This worked for MVP, but it leaves no explicit boundary for future organization modes:

- `generic` scaffold behavior is embedded in `operations/init.py`;
- `vault/scaffold.py` and `schema/frontmatter.py` are placeholders;
- docs already mention LYT / PARA / Zettelkasten as future work, but the code has no neutral place to represent them;
- adding method-specific folders directly to `init` would blur core rules with optional methodology preferences.

R5.0 must create a foundation for organization modes while preserving the completed MVP behavior.

## Goals

1. Keep `generic` as the default mode and preserve current artifact-level behavior.
2. Introduce a neutral organization model that can describe scaffold directories, seed pages, page routing, and lint expectations.
3. Keep organization modes optional; users should not need to choose a methodology to initialize a useful LLM Wiki.
4. Define LYT, PARA, and Zettelkasten as future optional templates, not as R5.0 runtime behavior unless a later implementation plan explicitly adds a narrow mode.
5. Prepare comparison page workflows and advanced lint as future extensions without implementing semantic lint or DragonScale in R5.0.
6. Keep adapters thin: Codex and Claude should expose organization choices, but core owns artifact semantics.

## Non-Goals

R5.0 does not implement:

- full LYT, PARA, or Zettelkasten migration;
- automatic conversion of existing vaults between modes;
- DragonScale or log-folding memory;
- semantic stale-claim detection;
- vector or hybrid retrieval;
- Obsidian Dataview, Bases, canvas, or plugin-specific dashboards;
- byte-for-byte prose parity across agents;
- Claude hooks, subagents, or `.claude-plugin` packaging.

## Recommended Approach

Use a foundation-first design:

1. Extract the current generic scaffold into a small organization definition layer.
2. Let `init` request an organization definition by name, defaulting to `generic`.
3. Keep the generated generic files and directories equivalent to the current MVP.
4. Add documentation and guard tests that future optional modes must not alter raw source immutability, index/log/hot roles, frontmatter minimums, or artifact-level equivalence.

This is preferable to directly implementing multiple modes now because methodology choices are high-level workflow preferences. Adding them before the contract is explicit would make the core harder to reason about and harder for adapters to expose consistently.

## Architecture

### Organization Definition

Create an internal model that describes an organization mode without binding it to any agent:

- `name`: stable mode identifier, such as `generic`;
- `description`: short human-readable purpose;
- `required_directories`: vault-relative directories to create;
- `seed_pages`: vault-relative pages and content factories;
- `page_type_routes`: mapping from page type to default folder;
- `lint_exemptions`: mode-specific page exemptions where needed;
- `adapter_notes`: optional text adapters can show without changing core behavior.

The first implementation should only ship `generic`. Future modes can add definitions after separate design review.

### Scaffold Boundary

Move scaffold construction out of `operations/init.py` and into `vault/scaffold.py`. `init_vault` should orchestrate:

1. resolve organization mode;
2. create required directories;
3. write `.raw/.manifest.json` if missing;
4. write seed pages if missing;
5. write adapter entry files when requested.

The behavior must remain conservative: never overwrite existing files during `init`.

### Frontmatter Boundary

Move frontmatter generation into `schema/frontmatter.py` so seed pages and future organization templates share one canonical minimum:

```yaml
---
type: concept
title: "Page Title"
created: 2026-07-07
updated: 2026-07-07T00:00:00+08:00
status: seed
---
```

R5.0 should keep the parser simple and dependency-free. It should not introduce a YAML dependency.

### CLI Boundary

The CLI may add `llm-wiki init <vault> --purpose "..." --organization generic` as an explicit spelling while keeping the current command valid. The default remains `generic`.

Unsupported organization values should fail clearly before writing scaffold files.

### Adapter Boundary

Codex and Claude adapter documents can mention that `generic` is the default organization mode. They should not claim LYT, PARA, Zettelkasten, DragonScale, semantic stale-claim lint, or advanced comparison workflows until those capabilities are implemented and tested.

### Documentation Boundary

Create a public knowledge organization document that explains:

- why generic is default;
- how optional organization modes should preserve the LLM Wiki loop;
- which R5 capabilities are foundation-only;
- what later R5.x milestones may add.

## Data Flow

### Init

1. User or adapter calls `llm-wiki init`.
2. CLI passes `organization="generic"` unless another supported value is explicitly provided.
3. Core resolves the organization definition.
4. Core creates required raw and wiki directories.
5. Core writes manifest and seed pages if missing.
6. Core writes the adapter entry file when requested.
7. Result reports created and skipped files.

### Save And Ingest

Save and ingest should continue to use page-type routing. In R5.0 the routing table should come from the organization definition, but for `generic` it must match current folders:

- `source` -> `wiki/sources/`
- `entity` -> `wiki/entities/`
- `concept` -> `wiki/concepts/`
- `question` -> `wiki/questions/`
- `comparison` -> `wiki/comparisons/`
- `meta` -> `wiki/meta/` or special root pages
- `overview` -> `wiki/overview.md`

No save or ingest behavior should become methodology-specific in R5.0.

### Lint

Lint should keep the current checks:

- required paths;
- manifest JSON and source record checks;
- frontmatter minimum fields;
- dead wikilinks;
- orphan pages.

R5.0 may centralize required paths through the organization definition. It should not add semantic stale-claim checks yet.

## Error Handling

- Unknown organization mode: raise a clear `ValueError` or equivalent CLI error naming the unsupported mode and listing supported modes.
- Existing files: skip rather than overwrite, preserving the current `init` contract.
- Invalid page route: fail during definition validation before any files are written.
- Missing generic definition: fail loudly in tests; this is a core invariant.

## Testing Strategy

R5.0 implementation should use TDD and include:

- unit tests that `generic` definition matches the current scaffold;
- unit tests that `init_vault(..., organization="generic")` creates the same required files as before;
- CLI tests for default organization behavior and explicit `--organization generic`;
- CLI tests for unsupported organization failure and JSON error output;
- lint tests proving required paths still match the generic organization definition;
- docs guard tests preventing claims that LYT, PARA, Zettelkasten, DragonScale, or semantic stale-claim lint are complete in R5.0;
- full suite verification before merge.

## Acceptance Criteria

R5.0 is complete when:

- existing `llm-wiki init <vault> --purpose "..."` behavior remains compatible;
- `generic` organization is represented by an explicit core definition;
- future organization modes have a documented extension point;
- no first-use workflow requires selecting LYT, PARA, or Zettelkasten;
- public docs distinguish foundation support from completed methodology mode support;
- all existing tests pass;
- new guard tests cover organization boundaries.

## Future R5.x Path

After R5.0, later milestones can be designed independently:

- R5.1: optional comparison page workflow helpers;
- R5.2: optional LYT template spike;
- R5.3: optional PARA template spike;
- R5.4: optional Zettelkasten template spike;
- R5.5: advanced lint for stale claims and semantic tiling;
- R5.6: DragonScale or log-folding memory design.

Each future milestone must prove that it preserves raw source immutability, durable Markdown artifacts, index/log/hot continuity, and artifact-level equivalence.
