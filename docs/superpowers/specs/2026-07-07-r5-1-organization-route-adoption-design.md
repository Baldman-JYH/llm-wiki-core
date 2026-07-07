# R5.1 Organization Route Adoption Foundation Design

## Status

Approved for implementation planning based on the project owner's instruction to continue with the scientifically reasonable design.

## Context

R5.0 introduced a neutral `OrganizationDefinition` for the default `generic` organization mode. `init` now creates its scaffold from that definition, and `lint` reads required paths from the organization contract.

That foundation is only partially adopted. Several operation modules still keep generic wiki paths in local constants or helper functions:

- `operations/ingest.py` writes source pages to `wiki/sources`;
- `operations/ingest_batch.py` predicts target source pages with its own `wiki/sources` path;
- `operations/save.py` maps `question` and `concept` to hard-coded folders;
- `operations/search.py` keeps a local `SEARCH_ROOTS` tuple;
- `operations/status.py` keeps a local `REQUIRED_PATHS` list.

This is acceptable for the released R5.0 baseline because only `generic` is supported. It becomes unsafe before future R5.x work adds LYT, PARA, Zettelkasten, comparison workflows, DragonScale, or advanced lint. R5.1 therefore makes the existing organization route contract the single source for core page placement and route discovery while preserving the current `generic` artifacts.

## Problem

The core has two parallel sources of truth:

1. `OrganizationDefinition.page_type_routes` describes where page types belong.
2. Individual operation modules still encode generic folders directly.

That split creates drift risk:

- ingest and batch-ingest conflict detection can disagree if route rules change;
- save can write to a folder that is no longer the organization route;
- search can omit a new collection route or search roots in the wrong order;
- status can report required paths differently from lint;
- future adapters cannot confidently expose organization choices if core consumers bypass the contract.

## Goals

1. Make organization routes the source of truth for source, concept, question, entity, comparison, meta, and overview paths.
2. Preserve the existing `generic` artifact layout, result fields, CLI output shape, and tests.
3. Keep R5.1 dependency-free and adapter-neutral.
4. Add a narrow routing helper layer so operations do not duplicate path decisions.
5. Keep `save` behavior compatible: R5.1 still supports only `question` and `concept` targets.
6. Keep current search scope compatible: searchable roots remain `wiki/sources`, `wiki/concepts`, `wiki/entities`, `wiki/questions`, and `wiki/comparisons` in the existing order.
7. Make unsupported page types or file-only routes fail with clear errors.
8. Add tests that prove operations consume the organization contract instead of local hard-coded route tables.

## Non-Goals

R5.1 does not implement:

- non-generic organization modes;
- vault-level persisted organization metadata;
- migration of existing vaults between modes;
- LYT, PARA, or Zettelkasten templates;
- comparison page workflow commands;
- DragonScale or log-folding memory;
- semantic stale-claim lint;
- vector, hybrid, or LLM-reranked retrieval;
- Claude hooks, subagents, or `.claude-plugin` packaging;
- byte-for-byte LLM prose parity.

## Recommended Approach

Use a route-adoption design:

1. Keep `OrganizationDefinition` as the organization data model.
2. Add small route helper APIs near the vault contract.
3. Change operations to request route information from those helpers.
4. Do not add new runtime modes yet.
5. Protect the compatibility contract with characterization tests.

This is preferable to adding organization modes immediately because route adoption is a prerequisite. It is also preferable to moving to retrieval work first because R5.0 has just opened a new organization boundary, and the safest next step is to close the obvious split between definition and use.

## Architecture

### Organization Definition Extension

Extend `OrganizationDefinition` with an explicit searchable page-type order:

```python
search_page_types: tuple[str, ...] = ()
```

For `generic`, the value should preserve the current `SEARCH_ROOTS` order:

```python
("source", "concept", "entity", "question", "comparison")
```

This avoids deriving search order from mapping insertion order. Search order is user-visible through `SearchWikiResult.searched_roots`, so R5.1 should keep it stable.

### Route Helper Layer

Create a focused helper module, preferably `llm_wiki_core/vault/routes.py`, with dependency-free functions:

```python
def route_for_page_type(page_type: str, organization: str = "generic") -> str:
    ...

def collection_route_for_page_type(page_type: str, organization: str = "generic") -> str:
    ...

def page_path_for_title(page_type: str, title: str, organization: str = "generic") -> str:
    ...

def search_roots_for_organization(organization: str = "generic") -> tuple[str, ...]:
    ...
```

Rules:

- `route_for_page_type` returns the vault-relative route from `OrganizationDefinition.page_type_routes`.
- `collection_route_for_page_type` rejects file routes such as `wiki/overview.md`.
- `page_path_for_title` appends `<title>.md` below a collection route.
- `search_roots_for_organization` resolves `search_page_types` to collection routes in stable order.
- unsupported page types raise `ValueError` or a small `UnsupportedPageType` subclass that lists supported page types.
- routes must remain relative POSIX-style paths and must not contain `..`.

### Operation Consumers

`operations/ingest.py` should call `page_path_for_title("source", title)`.

`operations/ingest_batch.py` should use the same `page_path_for_title("source", title)` for conflict prediction so preflight checks match ingest writes.

`operations/save.py` should keep its existing target allowlist:

```python
{"question", "concept"}
```

After validating the target type, it should call `page_path_for_title(target_type, page_title)`.

`operations/search.py` should replace the local `SEARCH_ROOTS` source of truth with `search_roots_for_organization("generic")`. It can keep an exported compatibility constant only if that constant is computed from the helper at import time and tests prove it matches the generic organization contract.

`operations/status.py` should replace its local required-path list with `required_paths_for_organization("generic")`, matching `lint`.

### Organization Metadata Boundary

R5.1 should not introduce persisted vault organization metadata. Today only `generic` is supported, and all operation calls can safely default to `generic`.

When a later milestone adds a real non-generic mode, it should separately design:

- where the selected organization mode is recorded;
- how existing vaults are migrated or left unchanged;
- how adapters expose organization choices;
- how operations select the vault's active organization.

Keeping that out of R5.1 prevents speculative state design.

## Data Flow

### Ingest

1. User calls `llm-wiki ingest`.
2. Core validates the raw source path.
3. Core derives the source title.
4. Core asks the organization route helper for the `source` page path.
5. Core writes or skips the generated source page.
6. Manifest, index, log, and hot updates continue unchanged.

### Batch Ingest

1. User calls `llm-wiki ingest-batch`.
2. Core discovers raw Markdown sources.
3. Batch preflight predicts each source page through the same source route helper used by ingest.
4. Conflicts are reported before each item is ingested.
5. Per-source success, skipped, and failed accounting remains unchanged.

### Save

1. User calls `llm-wiki save`.
2. Core validates `target_type` as `question` or `concept`.
3. Core asks the organization route helper for the target page path.
4. Core writes the saved page and updates index, log, and hot as before.

### Search

1. User calls `llm-wiki search`.
2. Core asks the organization route helper for searchable generic roots.
3. Core lists Markdown pages in those roots.
4. Existing lexical scoring and output behavior remain unchanged.

### Status

1. User calls `llm-wiki status`.
2. Core asks the organization contract for required generic paths.
3. Core reports missing paths, source count, preferred transport, and recent log entry as before.

## Error Handling

- Unknown organization mode keeps the existing `UnsupportedOrganizationMode` behavior.
- Unknown page type should produce a clear route error that names the unsupported page type and lists supported page types.
- A file route used where a collection route is required should fail clearly, for example when trying to create a page under `overview`.
- Invalid routes in definitions should fail in tests before runtime use.
- R5.1 should not make missing folders fail earlier than today; write operations may still create directories through the active transport as they do now.

## Testing Strategy

R5.1 should use TDD and include:

- unit tests for the route helper APIs;
- tests proving `generic` search roots keep the current order;
- tests proving `overview` is a file route and cannot be used as a collection route;
- ingest tests proving source page paths come from the route helper;
- batch ingest tests proving conflict prediction and ingest use the same source route helper;
- save tests proving question and concept paths come from the route helper while unsupported target types still fail as before;
- search tests proving searched roots come from organization search roots;
- status tests proving required paths come from `required_paths_for_organization("generic")`;
- docs guard tests that R5.1 is route adoption only and does not claim methodology modes are implemented;
- full suite verification before merge.

## Acceptance Criteria

R5.1 is complete when:

- all existing generic file paths produced by ingest, batch ingest, save, search, and status remain compatible;
- route decisions for source, concept, question, entity, comparison, meta, and overview are centralized in the organization contract and route helper layer;
- `SEARCH_ROOTS` and status required paths no longer drift from the generic organization definition;
- no new organization modes are exposed;
- public docs describe R5.1 as route adoption, not methodology implementation;
- focused tests, adjacent docs tests, full suite, whitespace checks, dependency boundary checks, and repo hygiene checks pass.

## Future R5.x Path

After R5.1, the project can safely choose among:

- R5.2 comparison page workflow helpers;
- R5.3 optional LYT template spike;
- R5.4 optional PARA template spike;
- R5.5 optional Zettelkasten template spike;
- R5.6 advanced stale-claim and semantic-tiling lint;
- R5.7 DragonScale or log-folding memory design.

Each future milestone should preserve raw source immutability, durable Markdown artifacts, index/log/hot continuity, flat frontmatter minimums, and artifact-level parity across local adapters.
