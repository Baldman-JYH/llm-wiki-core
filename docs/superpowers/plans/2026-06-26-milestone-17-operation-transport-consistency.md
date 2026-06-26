# Milestone 17 Operation Transport Consistency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure default core operations consistently use an implemented runtime transport.

**Architecture:** Add a transport runtime selector that reads snapshot metadata as advisory state and returns `FilesystemTransport` for the MVP. Adopt it in operations that already support default transport injection.

**Tech Stack:** Python 3.10+, pytest, Markdown.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Do not implement actual Obsidian CLI read/write/search in this milestone.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits unless explicitly requested.

---

### Task 1: Runtime Transport Selector

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_runtime_transport_selection.py`
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/runtime.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/__init__.py`

**Interfaces:**
- Produces: `select_runtime_transport(vault_root)`
- Produces: `RuntimeTransportSelection(name, transport, warnings, snapshot_preferred)`

- [ ] **Step 1: Write failing tests**

Test missing snapshot, legacy `preferred: obsidian-cli`, current unimplemented Obsidian CLI snapshot, and invalid snapshot JSON.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests\unit\test_runtime_transport_selection.py -q`

Expected: import failure because runtime selector does not exist.

- [ ] **Step 3: Implement selector**

Create `RuntimeTransportSelection` and `select_runtime_transport`. Return filesystem in all MVP cases, adding warnings for invalid snapshots or unimplemented preferred transport.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests\unit\test_runtime_transport_selection.py -q`

Expected: all selector tests pass.

### Task 2: Operation Adoption

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/query.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/lint.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/status.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/continue_.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_status_continue_operations.py`

**Interfaces:**
- Consumes: `select_runtime_transport(vault_root)`
- Produces: consistent default transport behavior in query/lint/status/continue

- [ ] **Step 1: Write failing status test**

Add a test that writes a legacy snapshot with `preferred: obsidian-cli`; `status_wiki` should report `preferred_transport == "filesystem"` and include a warning.

- [ ] **Step 2: Verify red**

Run: `python -m pytest tests\unit\test_status_continue_operations.py::test_status_wiki_falls_back_from_legacy_unimplemented_transport_snapshot -q`

Expected: failure because status currently reports the snapshot preferred value directly.

- [ ] **Step 3: Adopt selector**

Use `select_runtime_transport` when no explicit test/adapter transport is injected. Preserve explicit `transport=` behavior.

- [ ] **Step 4: Verify green**

Run: `python -m pytest tests\unit\test_status_continue_operations.py tests\unit\test_query_save_operations.py tests\unit\test_lint_operation.py -q`

Expected: all affected operation tests pass.

### Task 3: Docs And Progress

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/transport-contract.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: implemented selector and operation adoption
- Produces: documented Milestone 17 state

- [ ] **Step 1: Update docs**

Document runtime selection as a separate step from detection.

- [ ] **Step 2: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

### Task 4: Final Verification

**Files:**
- Read-only checks across the project

**Interfaces:**
- Consumes: all Milestone 17 changes
- Produces: final verification evidence

- [ ] **Step 1: Run all tests**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`

Expected: all tests pass, with the known Windows POSIX shell dry-run skip.

- [ ] **Step 2: Verify reference repository is untouched**

Run: `git -C D:\ai\llmWiki\claude-obsidian status --short`

Expected: no output.

- [ ] **Step 3: Verify generated artifacts are cleaned**

Check no `__pycache__`, `*.egg-info`, `build`, or temporary rehearsal vault remains after cleanup.

