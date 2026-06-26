# Milestone 18 Ingest Save Write Transport Consistency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `ingest` and `save` use the runtime transport boundary for their default write paths.

**Architecture:** Preserve operation outputs and CLI behavior. Add optional transport injection and move internal reads/writes to transport methods.

**Tech Stack:** Python 3.10+, pytest, Markdown.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Do not implement actual Obsidian CLI write behavior in this milestone.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits unless explicitly requested.

---

### Task 1: Ingest Transport Injection

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_ingest_operation.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/ingest.py`

**Interfaces:**
- Consumes: `select_runtime_transport(vault_root)`
- Produces: `ingest_source(vault_root, source_path, force=False, transport=None)`

- [ ] **Step 1: Write failing test**

Add a spy transport test proving `ingest_source(..., transport=transport)` reads raw source and manifest through transport and writes source page, index, log, hot, and manifest through transport.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests\unit\test_ingest_operation.py::test_ingest_source_uses_transport_for_read_and_write_paths -q`

Expected: failure because `ingest_source` does not accept `transport`.

- [ ] **Step 3: Implement transport usage**

Update `ingest_source` and helper functions to use transport methods for file existence, reads, and writes.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests\unit\test_ingest_operation.py -q`

Expected: all ingest tests pass.

### Task 2: Save Transport Injection

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_query_save_operations.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/save.py`

**Interfaces:**
- Consumes: `select_runtime_transport(vault_root)`
- Produces: `save_insight(vault_root, content, title=None, target_type="question", transport=None)`

- [ ] **Step 1: Write failing test**

Add a spy transport test proving `save_insight(..., transport=transport)` writes page, index, log, and hot through transport.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests\unit\test_query_save_operations.py::test_save_insight_uses_transport_for_write_paths -q`

Expected: failure because `save_insight` does not accept `transport`.

- [ ] **Step 3: Implement transport usage**

Update `save_insight` and helper functions to use transport methods for file existence, reads, and writes.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests\unit\test_query_save_operations.py -q`

Expected: all query/save tests pass.

### Task 3: Docs And Progress

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/transport-contract.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: implemented write-path transport consistency
- Produces: documented Milestone 18 state

- [ ] **Step 1: Update docs**

Document that `ingest` and `save` now use runtime transport selection by default.

- [ ] **Step 2: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

### Task 4: Final Verification

**Files:**
- Read-only checks across the project

**Interfaces:**
- Consumes: all Milestone 18 changes
- Produces: final verification evidence

- [ ] **Step 1: Run all tests**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`

Expected: all tests pass, with the known Windows POSIX shell dry-run skip.

- [ ] **Step 2: Verify reference repository is untouched**

Run: `git -C D:\ai\llmWiki\claude-obsidian status --short`

Expected: no output.

- [ ] **Step 3: Verify generated artifacts are cleaned**

Check no `__pycache__`, `*.egg-info`, or `build` remains after cleanup.

