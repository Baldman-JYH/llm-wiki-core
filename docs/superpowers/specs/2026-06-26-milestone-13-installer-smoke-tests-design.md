# Milestone 13 Installer Smoke Tests Design

## Goal

Make Codex adapter installer entrypoints testable without modifying the user's Python environment or vault.

## Context

The repo-local Codex adapter already includes:

- `integrations/codex/install/install.ps1`
- `integrations/codex/install/install.sh`

Both scripts currently execute real installation and initialization steps. Automated tests need a safe way to verify the planned commands without running `pip install -e` or mutating a vault.

## Scope

Implement:

- PowerShell `-DryRun` switch.
- shell `--dry-run` flag.
- dry-run output that lists the planned commands:
  - `python -m pip install -e ...` or `python3 -m pip install -e ...`
  - `llm-wiki init ...`
  - `llm-wiki detect-transport ...`
- post-install next-step hints:
  - `llm-wiki status <vault>`
  - `llm-wiki continue <vault>`
- installer smoke tests that can run dry-run mode when the local shell is available.

## Non-Goals

- Do not run real installation in automated tests.
- Do not create a vault during installer smoke tests.
- Do not modify global Codex configuration.
- Do not publish plugin metadata.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Design Decision

`status` and `continue` are printed as next-step hints, not executed by the installer. This keeps install side effects limited to package installation, scaffold creation, and transport detection while teaching users how to re-enter the Wiki after setup.

