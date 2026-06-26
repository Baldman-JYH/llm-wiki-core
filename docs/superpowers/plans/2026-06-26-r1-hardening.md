# R1 Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden the local MVP with structured CLI output, stricter lint validation, clearer ingest errors, and updated R1 documentation.

**Architecture:** Preserve existing operation result dataclasses and default CLI text output. Add a CLI JSON serializer and command-level error wrapper. Extend lint with a conservative frontmatter parser. Keep ingest path validation in core so both CLI and future adapters get the same behavior.

**Tech Stack:** Python 3.10+, argparse, dataclasses, pytest, Markdown docs.

## Global Constraints

- Karpathy LLM Wiki gist remains the abstract design source.
- `claude-obsidian` remains the reference implementation, not code to copy.
- `llm-wiki-core` remains neutral across Codex, Claude Code, and future local agents.
- R1 must not move the `v0.1.0-mvp` tag.
- R1 must not implement Obsidian CLI actual read/write/search.
- R1 must not modify `D:/ai/llmWiki/claude-obsidian`.
- Git commit messages must be Chinese.

---

### Task 1: CLI JSON Output

**Files:**
- Modify: `llm_wiki_core/cli.py`
- Create: `tests/unit/test_cli_json_output.py`

**Interfaces:**
- Consumes: existing command result dataclasses.
- Produces: `--json` support on every CLI subcommand.

- [ ] **Step 1: Write failing tests**

Add tests that call `main()` with `--json` for `init`, `status`, and an invalid `ingest`.

- [ ] **Step 2: Verify red**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/unit/test_cli_json_output.py -q
```

Expected: fails because `--json` is not accepted.

- [ ] **Step 3: Implement JSON output**

Add `--json` to each subparser. Serialize dataclass results with `dataclasses.asdict`. Catch command exceptions and return structured error JSON with exit code `1`.

- [ ] **Step 4: Verify green**

Run the focused test again. Expected: pass.

### Task 2: Frontmatter Lint Hardening

**Files:**
- Modify: `llm_wiki_core/operations/lint.py`
- Modify: `tests/unit/test_lint_operation.py`

**Interfaces:**
- Consumes: Markdown pages returned by transport.
- Produces: `frontmatter-field` findings for missing required fields.

- [ ] **Step 1: Write failing tests**

Add tests for missing `title` and malformed closing delimiter.

- [ ] **Step 2: Verify red**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/unit/test_lint_operation.py -q
```

Expected: new tests fail.

- [ ] **Step 3: Implement stricter parser**

Parse the opening and closing delimiters and line-oriented `key: value` fields. Require `type`, `title`, `created`, `updated`, and `status`.

- [ ] **Step 4: Verify green**

Run focused lint tests. Expected: pass.

### Task 3: Raw Source Path Errors

**Files:**
- Modify: `llm_wiki_core/operations/ingest.py`
- Modify: `tests/unit/test_ingest_operation.py`

**Interfaces:**
- Consumes: user-provided source path.
- Produces: actionable `ValueError` / `FileNotFoundError` messages.

- [ ] **Step 1: Write failing tests**

Add tests for `.raw/../outside.md`, `notes/source.md`, and missing `.raw/articles/missing.md`.

- [ ] **Step 2: Verify red**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/unit/test_ingest_operation.py -q
```

Expected: at least traversal or message assertion fails.

- [ ] **Step 3: Implement path validation**

Reject paths whose normalized parts do not start with `.raw`, contain `..`, or resolve outside raw-source policy.

- [ ] **Step 4: Verify green**

Run focused ingest tests. Expected: pass.

### Task 4: R1 Documentation

**Files:**
- Modify: `docs/roadmap-schedule.md`
- Modify: `docs/release-notes-v0.1.0-mvp.md`
- Modify: `README.md`
- Create: `docs/r1-hardening-report.md`
- Create: `tests/unit/test_r1_hardening_docs.py`

**Interfaces:**
- Consumes: completed R1 behavior.
- Produces: documented R1 status.

- [ ] **Step 1: Write failing docs test**

Require R1 completion text, CLI JSON output, stricter frontmatter lint, and raw-source path errors in docs.

- [ ] **Step 2: Verify red**

Run focused docs test. Expected: fails before docs exist.

- [ ] **Step 3: Update docs**

Mark R1 complete and add report.

- [ ] **Step 4: Verify green**

Run focused docs test. Expected: pass.

### Task 5: Final Verification And Commit

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: all R1 results.
- Produces: final progress record and Git commit.

- [ ] **Step 1: Run all tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q
```

- [ ] **Step 2: Check repository boundaries**

```powershell
git -C D:\ai\llmWiki\claude-obsidian status --short
git status --short --branch
```

- [ ] **Step 3: Update progress document**

Append R1 implementation evidence to `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

- [ ] **Step 4: Commit and push**

```powershell
git add .
git commit -m "完成 R1 稳定性加固"
git push origin r1-hardening
```
