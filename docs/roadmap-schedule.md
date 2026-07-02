# Roadmap Schedule

Date: 2026-06-26

This schedule turns the roadmap into prioritized follow-up windows. Dates are planning windows, not external publication promises.

## R0: MVP Local Complete

Window: 2026-06-26

Status: complete.

Scope:

- Codex App local path.
- Codex CLI local path.
- Filesystem runtime transport.
- Artifact-level equivalence verification.
- Local release archive and tag.

## R1: Hardening

Window: 2026-06-26

Status: complete.

Scope:

- More broken-vault fixtures.
- More CLI output shape tests.
- Stricter frontmatter validation.
- Better invalid `.raw/` path errors.
- Optional machine-readable CLI output.

Completed outcome:

- Added optional `--json` output for all CLI commands.
- Added structured JSON error output.
- Added stricter missing-field and malformed-frontmatter lint coverage.
- Added clearer `.raw/` ingest path validation and error messages.
- Added R1 documentation coverage.

Exit criteria:

- New fixture coverage is documented.
- Existing MVP artifact-level equivalence remains stable.

## R2: Transport Expansion

Window: 2026-07-04 to 2026-07-17

Status: complete.

Scope:

- actual Obsidian CLI read/write/search design.
- Obsidian CLI command probing.
- Transport capability negotiation.
- Conflict and fallback behavior.

Completed outcome:

- Added official `obsidian` CLI runtime selection boundaries and documentation.
- Preserved legacy `obsidian-cli` detection as metadata only.
- Documented capability probe gating and filesystem fallback behavior.
- Added R2 documentation guard tests.

Exit criteria:

- Obsidian CLI actual read/write/search has a clear contract and automated tests before being considered runtime eligible.

## R3: Ingest And Retrieval Expansion

Window: 2026-07-18 to 2026-08-07

Scope:

- URL ingest.
- batch ingest.
- deep retrieval.
- BM25 or vector-search spike.
- LLM synthesis save policy.

Exit criteria:

- Each new ingest or retrieval mode proves raw source preservation, citation traceability, and lint health.

### R3.1: Batch Ingest

Window: 2026-06-28

Status: complete.

Scope:

- Batch ingest local `.md` files under `.raw/`.
- Reuse the existing single-source ingest path.
- Preserve raw source files, manifest traceability, index/log/hot updates, and lint health.
- Report per-source success, skipped, and failed items.

Non-scope:

- URL ingest.
- HTML cleanup.
- Image ingest.
- Deep retrieval.
- BM25, vector search, hybrid retrieval, or reranking.
- LLM synthesis.

Follow-up:

- URL ingest and retrieval expansion remain future R3 work.
- Full `claude-obsidian` parity is not claimed in R3.1.

### R3.2: URL Ingest

Window: 2026-06-30

Status: complete.

Scope:

- one explicit `http` or `https` URL per command
- immutable `.raw/url/` snapshots
- text-only decoded raw payload preservation
- normalized Markdown source generation for reuse by `ingest`
- manifest provenance for URL sources

Non-scope:

- Full readability
- defuddle
- JavaScript rendering
- authenticated pages
- crawling
- deep retrieval
- BM25, vector search, hybrid retrieval, reranking, or LLM synthesis

Follow-up:

- deeper HTML cleanup remains deferred
- deep retrieval and search layers remain deferred to future R3 work

### R3.3: Retrieval Foundation

Window: 2026-06-30

Status: complete.

Scope:

- Read-only `search` operation.
- CLI command `llm-wiki search <vault> "<query>" [--limit N] [--json]`.
- Dependency-free BM25-style lexical retrieval over durable Markdown wiki pages.
- Query operation reuses the retrieval foundation.

Non-scope:

- Vector search.
- Hybrid retrieval.
- LLM reranking.
- qmd integration.
- Raw-source search by default.
- LLM synthesis save policy.

Follow-up:

- Deep retrieval, hybrid retrieval, vector search, reranking, and LLM synthesis remain deferred.

## R4: Adapter Expansion

Window: 2026-08-08 to 2026-08-21

Status: R4.0 complete; remaining R4.x adapter work deferred.

Scope:

- Codex user-level skill packaging.
- Codex plugin packaging decision.
- Claude adapter reconstruction.
- Claude adapter commands, hooks, and subagents as adapter-only behavior.

### R4.0: Codex Adapter Packaging Readiness

Window: 2026-07-02

Status: complete.

Release: `v0.3.1-mvp`.

Scope:

- Public README cleanup for open-source readability.
- Codex adapter assets covering `search`, `ingest-batch`, and `ingest-url`.
- Codex command contract coverage for batch ingest, URL ingest, and read-only durable-page search.
- Adapter packaging docs for repo-local mode, documented user-level skill mode, and plugin packaging boundaries.
- Guard tests for damaged text, private local paths, stale command mappings, and core/adapter boundary drift.

Non-scope:

- Claude adapter reconstruction.
- Marketplace-grade Codex plugin publication.
- Vector search, hybrid retrieval, reranking, qmd integration, raw-source search by default, or LLM synthesis.

Follow-up:

- Claude adapter reconstruction remains future R4.x work.
- Marketplace-grade plugin packaging remains future R4.x work.

Exit criteria:

- Adapter behavior remains outside neutral core unless it represents a true cross-agent LLM Wiki rule.

## R5: Knowledge Organization

Window: 2026-08-22 to 2026-09-04

Scope:

- Methodology modes.
- LYT / PARA / Zettelkasten templates.
- Comparison page workflows.
- DragonScale or log-folding memory extension.
- Advanced stale-claim and semantic-tiling lint.

Exit criteria:

- Organization modes remain optional and do not become first-use prerequisites.
