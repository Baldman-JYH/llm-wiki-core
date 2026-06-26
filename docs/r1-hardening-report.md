# R1 Hardening Report

Date: 2026-06-26

Status: complete.

R1 is a post-MVP hardening pass. It does not redefine the neutral core, move the `v0.1.0-mvp` tag, or claim full `claude-obsidian` parity. It strengthens the local Codex App and Codex CLI practice loop while preserving the same artifact-level LLM Wiki target: durable Markdown files, raw source preservation, manifest metadata, wikilinks, operation logs, hot context, and lint feedback.

## Completed Scope

- CLI JSON output: every command now supports optional `--json` output for local automation and agent adapters.
- CLI error output: failures return one machine-readable object with `operation`, `status`, `error.type`, and `error.message`.
- Frontmatter lint: lint now reports missing required frontmatter fields through `frontmatter-field` findings.
- Frontmatter delimiters: malformed frontmatter without a closing delimiter is reported as a high-severity finding.
- `.raw/ path errors`: ingest rejects paths outside `.raw/`, rejects `..` traversal before transport access, and reports missing raw files with the `.raw/` boundary in the message.
- Documentation coverage: README, user guide, roadmap schedule, release notes, and this report describe the R1 boundary.

## Contract Notes

The R1 changes remain inside the neutral core contract. They do not add Claude Code hooks, Obsidian CLI runtime behavior, LLM synthesis, URL ingest, batch ingest, or adapter-specific workflow policy.

The JSON output is intentionally optional. Human-readable text remains the default for direct CLI use, while Codex App, Codex CLI, CI, or future adapters can opt into structured output when they need stable parsing.

## Verification

Focused R1 verification includes:

```powershell
python -m pytest tests/unit/test_cli_json_output.py -q
python -m pytest tests/unit/test_lint_operation.py -q
python -m pytest tests/unit/test_ingest_operation.py -q
python -m pytest tests/unit/test_r1_hardening_docs.py -q
```

Before integration, run the full suite:

```powershell
python -m pytest -q
```
