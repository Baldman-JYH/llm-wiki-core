# Milestone 20 Release Readiness / User Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add release-readiness documentation for the local Codex App / CLI MVP and verify that core user-facing instructions remain discoverable.

**Architecture:** Keep implementation unchanged. Add Markdown docs plus a small pytest static coverage test.

**Tech Stack:** Markdown, Python 3.10+, pytest.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Verify artifact-level equivalence, not byte-for-byte LLM-authored prose.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits unless explicitly requested.

---

### Task 1: Documentation Coverage Test

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_release_docs.py`

**Interfaces:**
- Consumes: release docs and README
- Produces: static coverage for key commands and boundaries

- [ ] **Step 1: Add failing test**

Assert that the user guide, release checklist, and README contain:

- local Codex App / CLI positioning;
- `artifact-level equivalence`;
- filesystem transport and Obsidian CLI boundary;
- main `llm-wiki` commands.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests/unit/test_release_docs.py -q`

Expected: fail before the new docs and README links exist.

### Task 2: Release Docs

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/docs/user-guide.md`
- Create: `D:/ai/llmWiki/llm-wiki-core/docs/release-readiness-checklist.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`

**Interfaces:**
- Consumes: current verified MVP behavior
- Produces: user-followable release guidance

- [ ] **Step 1: Write user guide**

Cover prerequisites, install, init, transport detection, raw source placement, ingest, status, continue, query, save, lint, expected artifacts, and troubleshooting.

- [ ] **Step 2: Write release checklist**

State what is ready, what is not ready, and which tests/rehearsals prove the status.

- [ ] **Step 3: Update README**

Move current status to Milestone 20 and link the new docs.

### Task 3: Verification And Progress

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: test results and changed docs
- Produces: user-facing progress update

- [ ] **Step 1: Run focused test**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/unit/test_release_docs.py -q`

- [ ] **Step 2: Run all tests**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`

- [ ] **Step 3: Verify reference repository is untouched**

Run: `git -C D:\ai\llmWiki\claude-obsidian status --short`

Expected: no output.

- [ ] **Step 4: Update progress document**

Append Milestone 20 result under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

- [ ] **Step 5: Clean generated artifacts**

Remove or verify absence of `__pycache__`, `*.egg-info`, and `build`.
