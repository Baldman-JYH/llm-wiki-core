# R2.1 Documentation Consistency Design

Date: 2026-06-28

## Goal

Bring the public documentation in line with the current R2 implementation.

R2 completed a conservative official `obsidian` CLI runtime path. That path is eligible only after vault binding and read/write/append/list/search capability probes pass. All missing, stale, copied, legacy, or unverified transport states continue to use filesystem fallback.

R2.1 is a documentation consistency pass. It should remove stale pre-R2 wording without changing runtime behavior.

## Background

The project follows Karpathy's LLM Wiki gist as the abstract source of the workflow: humans choose sources and questions, while local agents maintain durable Markdown Wiki artifacts.

`claude-obsidian` remains a reference implementation for the Claude Code + Obsidian setting, not a code source to copy. `llm-wiki-core` remains the neutral core for Codex App, Codex CLI, Claude Code adapters, and future local agents.

After R2, `docs/r2-obsidian-cli-transport-report.md`, `docs/transport-contract.md`, and `docs/user-guide.md` describe the official `obsidian` runtime boundary correctly. Some public overview documents still contain older statements that were true during the MVP, such as saying actual Obsidian CLI read/write/search is not implemented.

Those statements now mislead users reading the repository front page.

## Scope

R2.1 updates public-facing documentation only.

Primary candidates:

- `README.md`
- `docs/roadmap.md`
- `docs/completion-criteria.md`
- `docs/release-readiness-checklist.md`
- `docs/artifact-equivalence-verification.md`
- `docs/obsidian-cli-transport-boundary-rehearsal.md`
- `docs/reference-implementation-alignment.md`

The implementation plan should inspect these files and update only stale R2-preimplementation wording. Historical specs and implementation plans under `docs/superpowers/` may remain historical unless they are linked as current public guidance.

## Non-Goals

- Do not change runtime, detection, transport, CLI, or operation code.
- Do not add URL ingest, batch ingest, deep retrieval, BM25, vector search, or LLM synthesis.
- Do not change `claude-obsidian`.
- Do not move `v0.1.0-mvp`.
- Do not rewrite old milestone plans as if they were current docs.
- Do not claim Obsidian CLI is required.
- Do not claim Obsidian CLI is the default runtime.

## Documentation Rules

Public docs should use this R2 wording model:

- Official `obsidian` CLI is optional.
- Filesystem remains the portable fallback.
- The official `obsidian` CLI can be selected only after vault binding and read/write/append/list/search capability probes pass.
- Legacy `obsidian-cli` is detected as metadata only and is not used as an R2 runtime.
- Users do not need Obsidian installed to use the core filesystem path.
- If verification fails, commands continue through filesystem fallback where runtime selection applies.

README should not say:

- actual Obsidian CLI read/write/search is not implemented;
- Obsidian CLI is only detected and never runtime eligible;
- filesystem is always the only implemented runtime transport.

README may say:

- the implemented safe baseline is filesystem;
- official `obsidian` is an optional verified runtime path;
- R3 will focus on ingest and retrieval expansion.

## Test Strategy

Add or extend documentation guard tests.

Suggested test file:

- `tests/unit/test_r2_obsidian_cli_docs.py`

The tests should check that public docs:

- do not contain stale phrases such as `Actual Obsidian CLI read/write/search is not implemented`;
- describe official `obsidian` as optional and verified-only;
- mention filesystem fallback;
- keep legacy `obsidian-cli` metadata-only wording where relevant;
- do not contain local absolute paths in public docs.

If broader README hygiene tests already exist, the implementation plan may add assertions there instead of duplicating checks.

## Validation

Minimum validation:

```powershell
python -m pytest tests/unit/test_r2_obsidian_cli_docs.py tests/unit/test_readme_hygiene.py -q
```

Completion validation:

```powershell
python -m pytest -q
```

Expected full-suite result should preserve the existing Windows POSIX shell dry-run skip.

## Git And Release Handling

Work should happen on branch `r2-1-doc-consistency`.

Commit messages must be Chinese.

After implementation and verification, merge back to `main` with a fast-forward merge and push `origin/main` only if tests pass.

This pass does not create or move tags.

## Progress Record

After completion, update:

- `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

The progress record should say R2.1 is a documentation consistency pass, not a new runtime feature.
