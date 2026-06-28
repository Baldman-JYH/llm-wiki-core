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

## R4: Adapter Expansion

Window: 2026-08-08 to 2026-08-21

Scope:

- Codex user-level skill packaging.
- Codex plugin packaging decision.
- Claude adapter reconstruction.
- Claude adapter commands, hooks, and subagents as adapter-only behavior.

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
