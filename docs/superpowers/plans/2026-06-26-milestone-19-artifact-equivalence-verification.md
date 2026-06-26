# Milestone 19 Artifact Equivalence Verification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add and execute an automated artifact-level equivalence verification for the MVP Wiki flow.

**Architecture:** Use pytest to run the full core flow in a temporary vault and assert stable artifacts. Record a human-readable verification report after tests pass.

**Tech Stack:** Python 3.10+, pytest, Markdown.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Verify artifact-level equivalence, not byte-for-byte LLM-authored prose.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits unless explicitly requested.

---

### Task 1: Automated Artifact Verification

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_artifact_equivalence_verification.py`

**Interfaces:**
- Consumes: public operations and CLI-equivalent core behavior
- Produces: automated artifact-level verification

- [ ] **Step 1: Add verification test**

Create one full-flow test that performs:

1. init;
2. detect-transport;
3. create raw source;
4. ingest;
5. query;
6. save;
7. status;
8. continue;
9. lint.

- [ ] **Step 2: Run focused test**

Run: `python -m pytest tests\unit\test_artifact_equivalence_verification.py -q`

Expected: pass if MVP artifact equivalence is already satisfied.

### Task 2: Verification Report

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/docs/artifact-equivalence-verification.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`

**Interfaces:**
- Consumes: test result and verification matrix
- Produces: documented verification result

- [ ] **Step 1: Write report**

Record the verification matrix, commands run, result, and residual non-goals.

- [ ] **Step 2: Update README**

Move current status to Milestone 19 and link the verification report.

### Task 3: Progress And Final Verification

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: all verification results
- Produces: user-facing progress update

- [ ] **Step 1: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

- [ ] **Step 2: Run all tests**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`

Expected: all tests pass, with the known Windows POSIX shell dry-run skip.

- [ ] **Step 3: Verify reference repository is untouched**

Run: `git -C D:\ai\llmWiki\claude-obsidian status --short`

Expected: no output.

- [ ] **Step 4: Verify generated artifacts are cleaned**

Check no `__pycache__`, `*.egg-info`, or `build` remains after cleanup.

