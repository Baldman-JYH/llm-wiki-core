# Milestone 9 Transport Read Write Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a small neutral filesystem transport that can safely read, write, append, list, and search vault Markdown files.

**Architecture:** Transport remains a thin local I/O layer under core operations. `FilesystemTransport` owns vault-relative path safety and deterministic text operations. Obsidian CLI remains a documented optional transport boundary, not an implementation dependency.

**Tech Stack:** Python 3.10+, standard library only, pytest.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Windows native PowerShell + Python must remain supported.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits because `D:/ai/llmWiki/llm-wiki-core` is not currently a Git repository.

---

### Task 1: Filesystem Transport Contract Tests

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_filesystem_transport.py`
- Modify: none

**Interfaces:**
- Consumes: placeholder module `llm_wiki_core.transport.filesystem`
- Produces: expected API for Task 2:
  - `FilesystemTransport(vault_root: str | Path)`
  - `PathOutsideVaultError`
  - `read_text(relative_path: str | Path) -> str`
  - `write_text(relative_path: str | Path, content: str) -> str`
  - `append_text(relative_path: str | Path, content: str) -> str`
  - `list_markdown(root: str | Path = "wiki") -> list[str]`
  - `search_text(query: str, root: str | Path = "wiki") -> list[SearchResult]`

- [ ] **Step 1: Write failing tests**

Create tests for safe read/write/append, Markdown listing, case-insensitive search, and path traversal rejection.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests\unit\test_filesystem_transport.py -q`

Expected: failures caused by missing `FilesystemTransport` and related symbols.

### Task 2: Filesystem Transport Implementation

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/filesystem.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/transport/__init__.py`
- Test: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_filesystem_transport.py`

**Interfaces:**
- Consumes: tests from Task 1
- Produces:
  - `FilesystemTransport`
  - `SearchResult`
  - `TransportError`
  - `PathOutsideVaultError`

- [ ] **Step 1: Implement minimal transport**

Implement path safety, UTF-8 text I/O, Markdown listing, and deterministic substring search.

- [ ] **Step 2: Run focused tests**

Run: `python -m pytest tests\unit\test_filesystem_transport.py -q`

Expected: all filesystem transport tests pass.

- [ ] **Step 3: Run transport detection regression tests**

Run: `python -m pytest tests\unit\test_transport_detection.py -q`

Expected: existing transport detection behavior remains unchanged.

### Task 3: Documentation And Milestone State

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/transport-contract.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: implemented filesystem transport API
- Produces: documented Milestone 9 state and progress record

- [ ] **Step 1: Update docs**

Document the new filesystem transport operations and the continued Obsidian CLI boundary.

- [ ] **Step 2: Update progress document**

Append a new stage under `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`.

### Task 4: Final Verification

**Files:**
- Read-only checks across the project

**Interfaces:**
- Consumes: all Milestone 9 changes
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

