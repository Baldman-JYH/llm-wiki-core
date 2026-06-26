# Milestone 12 Codex Adapter Status Continue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update Codex adapter assets so Codex users can discover and trigger `status` and `continue`.

**Architecture:** Keep core unchanged. Update repo-local adapter documents and tests to include the two read-only commands and their natural language triggers.

**Tech Stack:** Markdown, pytest.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits because `D:/ai/llmWiki/llm-wiki-core` is not currently a Git repository.

---

### Task 1: Adapter Tests

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_codex_adapter_assets.py`

**Interfaces:**
- Consumes: existing Codex adapter assets
- Produces: assertions for `status` and `continue` documentation

- [ ] **Step 1: Write failing tests**

Assert that skill, AGENTS template, and command mapping mention `llm-wiki status`, `llm-wiki continue`, "check wiki status", and "resume wiki context".

- [ ] **Step 2: Run focused tests**

Run: `python -m pytest tests\unit\test_codex_adapter_assets.py -q`

Expected: failures because adapter assets do not yet mention status/continue.

### Task 2: Adapter Assets

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/AGENTS.template.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/COMMANDS.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/integrations/codex/skills/llm-wiki/SKILL.md`

**Interfaces:**
- Consumes: tests from Task 1
- Produces: documented Codex triggers for status/continue

- [ ] **Step 1: Add commands and mappings**

Add `llm-wiki status <vault>` and `llm-wiki continue <vault>` in each adapter surface.

- [ ] **Step 2: Run focused tests**

Run: `python -m pytest tests\unit\test_codex_adapter_assets.py -q`

Expected: tests pass.

### Task 3: Docs And Progress

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: updated adapter assets
- Produces: documented Milestone 12 state

- [ ] **Step 1: Update README**

Add Milestone 12 spec/plan references and note adapter status/continue support.

- [ ] **Step 2: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

### Task 4: Final Verification

**Files:**
- Read-only checks across the project

**Interfaces:**
- Consumes: all Milestone 12 changes
- Produces: final verification evidence

- [ ] **Step 1: Run all tests**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`

Expected: all tests pass.

- [ ] **Step 2: Verify reference repository is untouched**

Run: `git -C D:\ai\llmWiki\claude-obsidian status --short`

Expected: no output.

- [ ] **Step 3: Verify no Python cache directories remain**

Run: `Get-ChildItem -Path 'D:\ai\llmWiki\llm-wiki-core' -Recurse -Directory -Filter '__pycache__'`

Expected: no output after cleanup if cleanup is needed.

