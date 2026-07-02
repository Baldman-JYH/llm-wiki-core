# Roadmap

Date: 2026-06-26

## Current Tier

MVP local use is complete for Codex App and Codex CLI.

The implemented tier focuses on the Karpathy LLM Wiki loop:

1. humans provide raw sources;
2. the agent maintains durable Markdown Wiki artifacts;
3. index/log/hot preserve continuity;
4. query and save operate on the Wiki;
5. lint keeps the Wiki healthy.

## Near-Term Hardening

- Add more fixtures for broken Wiki states.
- Add more CLI output shape tests.
- Add stricter frontmatter field validation.
- Add clearer error messages for invalid `.raw/` paths.
- Add optional no-color / machine-readable output for CLI automation.

## Transport Roadmap

- Obsidian CLI integration hardening after R2 verified-only runtime selection.
- Transport-level conflict detection.
- Transport capability negotiation.
- Optional MCP transport.
- Optional REST API transport.

The portable baseline remains filesystem. The official `obsidian` CLI is optional and can be selected only after verification succeeds.

## Ingest And Retrieval Roadmap

- URL ingest.
- batch ingest.
- image / vision ingest.
- deep retrieval.
- hybrid retrieval.
- BM25 or vector search.
- LLM synthesis mode with explicit source citation and save policy.

## Adapter Roadmap

Codex adapter packaging readiness is complete for repo-local and documented user-level skill usage.
R4.1 explicit user-level skill installation is complete for local Codex App and Codex CLI use.
R4.2 adapter parity baseline is complete for documentation and guard tests.

Artifact-level Codex / Claude parity is the target; byte-for-byte LLM prose parity is not.

Remaining adapter work:

- Optional marketplace-grade Codex plugin packaging.
- Claude adapter reconstruction remains future adapter work.
- Claude adapter reconstruction remains future adapter implementation work.
- Claude Code commands, hooks, and subagents remain adapter-only behavior.

## Knowledge Organization Roadmap

- Methodology modes.
- LYT / PARA / Zettelkasten templates.
- comparison page workflows.
- DragonScale or log-folding memory extension.
- advanced lint for semantic tiling and stale claims.

## Out-Of-Scope Unless Reapproved

- Automatic global Codex configuration.
- Automatic Git commits.
- Marketplace publishing.
- Remote Codex Web as a primary target.
- Treating generated prose as byte-for-byte golden output.
