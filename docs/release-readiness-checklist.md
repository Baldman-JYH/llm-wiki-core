# Release Readiness Checklist

Date: 2026-06-26

Status: Ready for MVP local use; not ready for full claude-obsidian parity.

## Canonical Alignment

- [x] Karpathy's LLM Wiki gist is documented as the canonical abstract pattern.
- [x] `claude-obsidian` is documented as the reference implementation, not a directory to copy or modify.
- [x] `llm-wiki-core` is documented as the neutral practice implementation for Codex App, Codex CLI, and future local agents.
- [x] artifact-level equivalence is documented as the target.
- [x] Byte-for-byte equality of LLM-authored prose is explicitly out of scope.
- [x] Completion criteria and roadmap are documented.

## Local Codex MVP

- [x] Local editable package install is documented.
- [x] Python module fallback is documented for shells where `llm-wiki` is not on `PATH`.
- [x] Windows native PowerShell path is documented.
- [x] WSL and Git Bash are not required for Windows MVP usage.
- [x] Codex App and Codex CLI command discovery are documented through generated `AGENTS.md`.
- [x] Repo-local Codex adapter assets exist.
- [x] Global Codex configuration is not modified automatically.

## Core Commands

- [x] `llm-wiki init`
- [x] `llm-wiki detect-transport`
- [x] `llm-wiki ingest`
- [x] `llm-wiki status`
- [x] `llm-wiki continue`
- [x] `llm-wiki query`
- [x] `llm-wiki save`
- [x] `llm-wiki lint`
- [x] `python -m llm_wiki_core`

## Transport

- [x] `filesystem` is the implemented runtime transport.
- [x] Obsidian CLI detection records availability separately from implementation.
- [x] Obsidian CLI is not required for the MVP.
- [x] Obsidian CLI actual read/write/search is not implemented and is documented as a boundary.

## Artifact Verification

- [x] Raw source preservation is covered.
- [x] `.raw/.manifest.json` metadata is covered.
- [x] Source page generation is covered.
- [x] `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md` updates are covered.
- [x] Query wikilink citation behavior is covered.
- [x] Save-to-Wiki behavior is covered.
- [x] Status and continue re-entry behavior are covered.
- [x] Lint report generation is covered.

## Evidence

- [x] MVP smoke test exists.
- [x] Local editable install rehearsal exists.
- [x] Codex adapter installer rehearsal exists.
- [x] Obsidian CLI transport boundary rehearsal exists.
- [x] Runtime transport consistency tests exist.
- [x] Ingest/save transport consistency tests exist.
- [x] Artifact-level equivalence verification exists.
- [x] Release documentation coverage test exists.
- [x] Subprocess CLI entrypoint verification exists.
- [x] Completion readiness documentation test exists.

## Not Ready Yet

- [ ] Full `claude-obsidian` feature parity.
- [ ] Actual Obsidian CLI read/write/search.
- [ ] Claude Code plugin/hooks/subagent behavior inside the neutral core.
- [ ] URL ingest.
- [ ] Batch ingest.
- [ ] Deep semantic retrieval or vector search.
- [ ] LLM synthesis mode.
- [ ] Marketplace plugin publishing.
- [ ] Automatic global Codex configuration.
