# Milestone 6 Lint Design

## Goal

Implement basic Wiki health checks and a stable lint report for the MVP.

## Confirmed Approach

Use Python core API plus CLI subcommand:

- Core API: `lint_wiki(vault_root, write_report=True)`
- CLI: `llm-wiki lint <vault> [--no-report]`

## Checks

The MVP lint checks:

- required files and folders
- manifest JSON parseability and `schema_version`
- required frontmatter on Markdown pages
- dead wikilinks
- orphan pages outside the root meta pages and `_index.md`

## Report

When `write_report=True`, lint writes:

```text
wiki/meta/lint-report-YYYY-MM-DD.md
```

The report is stable enough for tests and future parity checks.

## Boundaries

- Do not auto-fix findings.
- Do not run semantic stale-claim checks.
- Do not run advanced tiling or DragonScale checks.
- Do not modify Raw Source.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.

## Verification

Tests should validate:

- a freshly initialized vault has no blocker findings
- missing/invalid manifest is reported as blocker
- missing frontmatter is reported
- dead wikilinks are reported
- orphan pages are reported
- CLI prints concise summary and writes a report by default
