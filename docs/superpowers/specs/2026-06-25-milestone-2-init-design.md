# Milestone 2 Init Design

## Goal

Implement the MVP `init` operation for `llm-wiki-core` so a local Codex App or Codex CLI workflow can scaffold a minimal LLM Wiki vault.

## Confirmed Approach

Use a Python core API plus a CLI subcommand:

- Core API: `init_vault(vault_root, purpose, adapter="codex")`
- CLI: `llm-wiki init <vault> --purpose "..."`

This keeps the domain behavior in the neutral core while giving Codex CLI and Codex App workflows a concrete local entrypoint.

## Scope

`init` creates:

- `.raw/.manifest.json`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/hot.md`
- `wiki/overview.md`
- `wiki/sources/`
- `wiki/entities/_index.md`
- `wiki/concepts/_index.md`
- `wiki/questions/`
- `wiki/comparisons/`
- `wiki/meta/`
- `AGENTS.md` for Codex-facing vault instructions

## Boundaries

- Do not implement ingest, query, lint, save, or transport detection.
- Do not generate Claude-specific files.
- Do not overwrite existing user files.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Result Shape

The operation returns a small result object containing:

- operation name
- status
- files created
- files skipped
- warnings
- next suggested action

## Verification

Tests should use `tmp_path` and validate:

- required files and folders are created
- manifest JSON is valid and has empty `sources`
- required seed pages contain frontmatter
- `AGENTS.md` is created from the Codex template semantics
- rerunning `init` does not overwrite an existing file
- CLI `init` returns success and prints a concise summary
