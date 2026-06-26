# Milestone 10 Operation Transport Adoption Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move `query` and `lint` onto the neutral transport interface while preserving existing operation behavior.

**Architecture:** Add optional transport injection to `query_wiki` and `lint_wiki`. Defaults still instantiate `FilesystemTransport(vault_root)`, so CLI behavior remains unchanged. Tests use spy transports to prove operation file access goes through the transport boundary.

**Tech Stack:** Python 3.10+, standard library only, pytest.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Windows native PowerShell + Python must remain supported.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits because `D:/ai/llmWiki/llm-wiki-core` is not currently a Git repository.

---

### Task 1: Query Transport Injection

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_query_save_operations.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/query.py`

**Interfaces:**
- Consumes: `FilesystemTransport` methods `read_text` and `list_markdown`
- Produces: `query_wiki(vault_root, question, depth="standard", transport=None)`

- [ ] **Step 1: Write failing test**

Add a spy transport test proving query reads hot/index, lists searchable roots, and reads candidate pages through the transport.

- [ ] **Step 2: Run focused query tests**

Run: `python -m pytest tests\unit\test_query_save_operations.py -q`

Expected: new test fails because `query_wiki` does not accept `transport`.

- [ ] **Step 3: Implement query transport use**

Update `query_wiki` and helpers to operate on vault-relative page paths.

- [ ] **Step 4: Run focused query tests**

Run: `python -m pytest tests\unit\test_query_save_operations.py -q`

Expected: all query/save tests pass.

### Task 2: Lint Transport Injection

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_lint_operation.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/filesystem.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/operations/lint.py`

**Interfaces:**
- Consumes: `FilesystemTransport`
- Produces:
  - `FilesystemTransport.exists(relative_path) -> bool`
  - `lint_wiki(vault_root, write_report=True, transport=None)`

- [ ] **Step 1: Write failing lint transport test**

Add a spy transport test proving lint uses transport for required path checks, manifest read, page read, Markdown listing, and report writing.

- [ ] **Step 2: Run focused lint tests**

Run: `python -m pytest tests\unit\test_lint_operation.py -q`

Expected: new test fails because `lint_wiki` does not accept `transport`.

- [ ] **Step 3: Implement filesystem `exists`**

Add `exists(relative_path)` to `FilesystemTransport`.

- [ ] **Step 4: Implement lint transport use**

Update lint helpers to use vault-relative paths and transport reads/writes.

- [ ] **Step 5: Run focused lint and filesystem transport tests**

Run: `python -m pytest tests\unit\test_lint_operation.py tests\unit\test_filesystem_transport.py -q`

Expected: tests pass.

### Task 3: Docs And Progress

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/transport-contract.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: implemented operation transport adoption
- Produces: documented Milestone 10 state

- [ ] **Step 1: Update docs**

Document that `query` and `lint` now use transport internally by default.

- [ ] **Step 2: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

### Task 4: Final Verification

**Files:**
- Read-only checks across the project

**Interfaces:**
- Consumes: all Milestone 10 changes
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

