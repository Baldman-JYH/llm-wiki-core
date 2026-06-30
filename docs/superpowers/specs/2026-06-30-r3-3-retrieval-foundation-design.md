# R3.3 Retrieval Foundation Design

## Status

Approved for design by the user on 2026-06-30.

## Context

The canonical abstraction for this project is Karpathy's LLM Wiki gist:

- `raw/` stores preserved source materials.
- `wiki/` stores durable Markdown knowledge synthesized from those sources.
- `schema/` stores rules, prompts, and behavior constraints.

`AgriciDaniel/claude-obsidian` remains the concrete Claude Code + Obsidian reference implementation of that abstraction. `llm-wiki-core` should generalize the same effect for Codex App, Codex CLI, and future local agents without depending on Claude-specific commands, hooks, or subagents.

R3.1 completed local Markdown batch ingest. R3.2 completed narrow URL ingest with immutable `.raw/url/` snapshots. R3.3 should now improve how agents find relevant existing wiki pages. This must remain a Wiki-centered retrieval layer, not a generic RAG system that bypasses the durable Markdown wiki.

The current `query` implementation reads `wiki/hot.md` and `wiki/index.md`, then ranks candidate pages with a lightweight term-count heuristic. This is useful as an MVP, but it is not yet a stable retrieval foundation that adapters, tests, and users can inspect independently.

## Goals

R3.3 should provide a narrow, testable retrieval foundation:

1. Add a neutral read-only `search` operation.
2. Add a CLI command:

   ```text
   llm-wiki search <vault> "<query>" [--limit N] [--json]
   ```

3. Search durable Markdown wiki pages under `wiki/`.
4. Return ranked results with paths, titles, snippets, matched terms, and scores.
5. Use deterministic lexical retrieval with BM25-style scoring and no runtime dependency.
6. Let `query` reuse the retrieval foundation instead of maintaining its own ranking logic.
7. Preserve current `query` behavior at the artifact level: no mutation, cited pages, explicit gaps.
8. Keep the implementation portable on Windows PowerShell, macOS, and Linux.

## Non-Goals

R3.3 does not implement:

- vector search;
- embeddings;
- hybrid lexical/vector retrieval;
- LLM reranking;
- LLM synthesis beyond the current query placeholder answer;
- public internet search;
- raw source search as the default query path;
- persistent search indexes;
- background indexing daemons;
- Obsidian-only search behavior;
- qmd integration;
- Claude-specific adapter commands;
- marketplace packaging.

These remain possible later extensions, but R3.3 should keep the first retrieval layer small, inspectable, and cross-platform.

## Recommended Approach

Implement a read-only search operation backed by a neutral retrieval module.

The search operation is preferred over only improving `query` internally because it gives Codex, CLI users, tests, and future adapters a visible evidence-selection primitive. Users and agents can inspect what the system found before asking for synthesis or saving an insight. That aligns with the LLM Wiki pattern: the durable wiki remains the source of accumulated knowledge, and retrieval is a tool for navigating that wiki.

The retrieval module should be deterministic and dependency-free. It can implement BM25-style lexical scoring over Markdown pages using the Python standard library:

- tokenize query and document text;
- ignore a small stable stopword set;
- compute document length normalization;
- compute inverse document frequency over the searched page set;
- score pages with a BM25-style formula;
- return stable sorted results by score, path, then title.

This is a retrieval foundation, not a full search engine. It should be good enough to replace the current term-count ranking and to create a stable contract for future BM25, vector, qmd, or hybrid backends.

## Architecture

R3.3 should introduce three layers:

1. Retrieval model dataclasses.
2. A pure retrieval module.
3. A core operation and CLI surface.

Suggested module boundary:

```text
llm_wiki_core/
  retrieval/
    __init__.py
    lexical.py
  operations/
    search.py
    query.py
```

The retrieval module should not know about CLI formatting. It should accept document records and a query string, then return ranked matches. The operation layer should know how to list and read wiki pages through the active transport.

The existing transport contract already provides:

- `list_markdown(root)`;
- `read_text(path)`;
- `search_text(query, root)`.

R3.3 should use `list_markdown` and `read_text` for ranked retrieval. The existing transport-level `search_text` remains useful for simple literal search and capability probing, but it is not enough for BM25-style ranking.

## Search Scope

The default search roots should be the durable knowledge page folders:

- `wiki/sources`
- `wiki/concepts`
- `wiki/entities`
- `wiki/questions`
- `wiki/comparisons`

R3.3 should not search `.raw/` by default. Raw sources are preserved evidence, but the LLM Wiki pattern expects query workflows to navigate the synthesized wiki first. Later work can add an explicit raw-source search mode if needed.

R3.3 should also avoid searching operational meta pages by default:

- `wiki/log.md`
- `wiki/hot.md`
- `wiki/index.md`
- `wiki/meta/`

`query` should still read `wiki/hot.md` and `wiki/index.md` before retrieval, preserving the current re-entry and orientation behavior. However, those coordination pages should not dominate ranked content results unless a later mode explicitly requests them.

## Result Shape

Add a stable result shape similar to existing operation dataclasses. The operation result should avoid reusing the transport-layer `SearchResult` name, because transport search is a literal line-search capability and R3.3 search is ranked wiki retrieval.

```text
SearchWikiResult
  operation: "search"
  status: "success" | "no_results"
  query: str
  limit: int
  results: list[RankedPage]
  searched_roots: list[str]
  searched_pages: int
  warnings: list[str]
```

Each ranked page should contain:

```text
RankedPage
  path: str
  title: str
  score: float
  matched_terms: list[str]
  snippet: str
```

Scores are not part of the user-facing semantic guarantee. They are useful for ordering and debugging, but documentation should say that score magnitude may change as retrieval improves. The stable guarantee is that results are ranked, cited by path, and explain matched terms/snippets.

## CLI Contract

Add:

```text
llm-wiki search <vault> "<query>" [--limit N] [--json]
```

Text output should follow existing CLI style:

```text
search success
query: durable LLM knowledge
searched pages: 12
results:
- wiki/concepts/Durable LLM Knowledge.md | score: 3.42 | [[Durable LLM Knowledge]]
  ...durable Markdown wiki...
```

No-result output:

```text
search no_results
query: unrepresented topic
searched pages: 12
```

JSON output should serialize the dataclass through the existing CLI JSON helper.

Invalid input should follow existing CLI error behavior:

- empty query fails clearly;
- limit must be a positive integer;
- missing or uninitialized vault should surface a clear error.

## Query Integration

`query_wiki` should delegate candidate ranking to the new search operation or a shared retrieval helper.

The current query contract should remain:

- read `wiki/hot.md`;
- read `wiki/index.md`;
- identify relevant wiki pages;
- return an answer grounded in cited wiki pages;
- report gaps when no relevant page exists;
- do not mutate the wiki unless the user explicitly saves.

R3.3 should not attempt full LLM answer synthesis. The current placeholder answer can become slightly more informative by referencing the top retrieved pages and snippets, but it should not claim deeper synthesis than the implementation can perform. LLM synthesis save policy remains future R3 work.

## Snippet Policy

Snippets should be deterministic and short:

- prefer the first line or paragraph that contains a matched query term;
- strip YAML frontmatter from snippet candidates;
- collapse whitespace;
- avoid returning entire documents;
- cap snippet length with a stable character limit.

Snippets are evidence previews, not summaries.

## Tokenization And Ranking

The initial lexical retrieval should be intentionally conservative:

- lowercase ASCII alphanumeric tokens;
- support simple Unicode word tokens if feasible without external dependencies;
- remove a small built-in stopword set;
- ignore one-character tokens unless numeric matching is useful;
- avoid stemming in R3.3;
- avoid phrase search in R3.3;
- keep ranking deterministic across platforms.

BM25-style ranking should account for:

- term frequency in each page;
- number of pages containing the term;
- document length normalization;
- stable tie-breaking by path.

If a query yields no valid terms after stopword filtering, the operation should fail clearly with an invalid query error rather than matching every page.

## Data Flow

1. User runs `llm-wiki search <vault> "<query>"`.
2. Core selects the active runtime transport.
3. Core lists Markdown pages under the configured wiki search roots.
4. Core reads candidate pages through the transport.
5. Retrieval module tokenizes documents and the query.
6. Retrieval module ranks pages with BM25-style lexical scoring.
7. Operation returns ranked result records.
8. CLI prints text or JSON output.

For `query`:

1. User runs `llm-wiki query <vault> "<question>"`.
2. Core reads `wiki/hot.md` and `wiki/index.md`.
3. Core invokes the retrieval foundation.
4. Core returns the existing query result shape with cited pages and gaps.

## Error Handling

R3.3 should fail clearly when:

- the query is empty or has no searchable terms;
- `limit` is less than 1;
- the vault cannot be read;
- transport reads fail unexpectedly.

Missing optional roots should not fail the operation. For example, an empty vault may not yet have user-created concept or entity pages. The operation should search available roots and report no results if there is no matching evidence.

Unreadable individual pages should either fail the operation or be reported as warnings. The first implementation should prefer fail-fast for unexpected read errors, because silent evidence loss is worse than a visible failure.

## Testing Strategy

R3.3 should add focused tests:

- lexical tokenization and stopword behavior;
- BM25-style ranking prefers more relevant pages;
- tie-breaking is deterministic;
- snippets strip frontmatter and stay short;
- `search_wiki` returns ranked path/title/snippet/matched-term records;
- no-results behavior for uncovered topics;
- invalid-query and invalid-limit behavior;
- transport-backed operation reads through `list_markdown` and `read_text`;
- CLI text output;
- CLI `--json` output;
- `query_wiki` reuses retrieval and preserves existing cited-page behavior;
- regression tests for `init`, `ingest`, `ingest-batch`, `ingest-url`, `save`, and `lint` behavior where relevant.

The full test suite should continue to pass on Windows without WSL or Git Bash.

## Documentation Updates

R3.3 should update:

- README command list and current status;
- `docs/user-guide.md`;
- `docs/operation-contract.md`;
- `docs/roadmap-schedule.md`;
- adapter command contract docs if `search` becomes a natural-language trigger;
- completion or capability documents that still describe retrieval as fully deferred.

Documentation must continue explaining:

- Karpathy's gist is the canonical abstraction;
- `AgriciDaniel/claude-obsidian` is the reference implementation;
- `llm-wiki-core` is a neutral practice implementation;
- R3.3 is local Markdown wiki retrieval, not full `claude-obsidian` parity.

## Acceptance Criteria

R3.3 is complete when:

1. `llm-wiki search <vault> "<query>"` returns ranked wiki pages.
2. Search results include paths, titles, snippets, matched terms, and scores.
3. Search is read-only and does not mutate raw sources or wiki artifacts.
4. `--json` returns a stable machine-readable result.
5. `query_wiki` reuses the retrieval foundation and keeps current query semantics.
6. Empty or uncovered queries report clear gaps or no-results status.
7. No runtime dependency is added.
8. Docs describe R3.3 scope and deferred vector/hybrid/rerank/LLM synthesis work.
9. Full tests pass.

## Deferred Follow-Up

Possible follow-up work after R3.3:

- persisted lexical index;
- phrase search;
- raw-source search mode;
- qmd integration;
- vector embeddings;
- hybrid lexical/vector retrieval;
- local reranking;
- deep retrieval mode;
- LLM synthesis save policy;
- adapter-level natural language shortcuts for search.

These should remain separate design nodes.
