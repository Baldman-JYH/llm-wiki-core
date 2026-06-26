# Milestone 7 Codex Adapter Design

## Goal

Provide repo-local Codex App and Codex CLI integration assets for the MVP core operations.

## Confirmed Approach

Create local adapter assets under `integrations/codex/`:

- expanded `AGENTS.template.md`
- Codex skill draft at `integrations/codex/skills/llm-wiki/SKILL.md`
- command mapping document
- PowerShell install entrypoint
- macOS/Linux shell install entrypoint

## Scope

The adapter documents and entrypoints cover:

- init
- detect-transport
- ingest
- query
- save
- lint

## Boundaries

- Do not install into global Codex configuration automatically.
- Do not publish or register a marketplace plugin.
- Do not generate Claude-specific files.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Verification

Tests should validate:

- Codex skill draft exists and references core commands
- `AGENTS.template.md` references the MVP workflow
- command mapping exists and covers natural language triggers
- `install.ps1` and `install.sh` exist and call `llm-wiki init`
