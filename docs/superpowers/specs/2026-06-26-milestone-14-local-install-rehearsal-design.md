# Milestone 14 Local Install Rehearsal Design

## Goal

Verify that a local Codex App / CLI user can install `llm-wiki-core` from this repository and run the MVP Wiki loop through the real `llm-wiki` console entrypoint.

## Context

Milestone 13 added installer dry-run coverage. That proves the installer scripts can safely describe their command plan, but it does not prove the installed command line interface works from an actual editable install.

Milestone 14 closes that gap with one manual-style local rehearsal:

- install the package with `python -m pip install -e .`;
- run `llm-wiki` through the generated console script;
- create a temporary vault;
- execute the MVP loop from the installed CLI.

## Scope

Run and record:

- `python -m pip install -e .`
- `llm-wiki --version`
- `llm-wiki init <vault> --purpose "..."`
- `llm-wiki detect-transport <vault> --force`
- create one local raw source under `.raw/articles/`;
- `llm-wiki status <vault>`
- `llm-wiki continue <vault>`
- `llm-wiki ingest <vault> .raw/articles/rehearsal.md`
- `llm-wiki query <vault> "rehearsal wiki"`
- `llm-wiki save <vault> --title "Rehearsal Insight" --content "..."`
- `llm-wiki lint <vault>`

## Non-Goals

- Do not add real installation to default automated tests.
- Do not require Obsidian CLI to be installed.
- Do not require WSL, Git Bash, or non-native Windows shells.
- Do not mutate global Codex configuration.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not publish packages or plugins.

## Design Decision

The rehearsal is documented evidence, not a permanent pytest case. Editable installation mutates the local Python environment and can create generated metadata, so it should remain an explicit local verification step rather than a test that runs on every contributor machine.

This stays aligned with the Karpathy LLM Wiki pattern because the verification focuses on the durable Wiki artifact loop: raw source intake, Wiki page creation, index/log/hot updates, query with citations, saved insight, and lint validation.

