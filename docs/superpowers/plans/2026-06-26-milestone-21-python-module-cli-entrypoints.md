# Milestone 21 Python Module CLI Entrypoints Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `python -m llm_wiki_core` and `python -m llm_wiki_core.cli` as subprocess-verified fallback CLI entrypoints.

**Architecture:** Keep the existing `llm_wiki_core.cli:main` as the single CLI implementation. Module entrypoints only delegate to that function.

**Tech Stack:** Python 3.10+, argparse, pytest subprocess tests, Markdown.

## Global Constraints

- Karpathy LLM Wiki gist is the canonical abstract pattern.
- `claude-obsidian` is a reference implementation, not code to copy.
- `llm-wiki-core` must stay neutral across Codex, Claude, and future local agents.
- Verify artifact-level equivalence, not byte-for-byte LLM-authored prose.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
- Do not perform Git commits unless explicitly requested.

---

### Task 1: Subprocess Tests

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/tests/unit/test_cli_subprocess_entrypoints.py`

**Interfaces:**
- Consumes: Python module execution and CLI output
- Produces: subprocess-level verification

- [ ] **Step 1: Add failing tests**

Assert:

- `python -m llm_wiki_core --version` prints version output;
- `python -m llm_wiki_core.cli --version` prints version output;
- `python -m llm_wiki_core` can run init, detect-transport, ingest, status, continue, query, save, and lint against a temporary vault.

- [ ] **Step 2: Verify red**

Run: `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests/unit/test_cli_subprocess_entrypoints.py -q`

Expected initial failure: package has no `llm_wiki_core.__main__`.

### Task 2: Entrypoint Implementation

**Files:**
- Create: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/__main__.py`
- Modify: `D:/ai/llmWiki/llm-wiki-core/llm_wiki_core/cli.py`

**Interfaces:**
- Consumes: `llm_wiki_core.cli.main`
- Produces: module execution fallback

- [ ] **Step 1: Add package module entrypoint**

Delegate `python -m llm_wiki_core` to `main()`.

- [ ] **Step 2: Add CLI module execution guard**

Delegate `python -m llm_wiki_core.cli` to `main()`.

- [ ] **Step 3: Verify green**

Run the focused subprocess test again.

### Task 3: Docs And Verification

**Files:**
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/user-guide.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/docs/release-readiness-checklist.md`
- Modify: `D:/ai/llmWiki/llm-wiki-core/README.md`
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: verified fallback behavior
- Produces: user-facing documentation and progress record

- [ ] **Step 1: Add documentation coverage**

Update release doc tests to require `python -m llm_wiki_core`.

- [ ] **Step 2: Update docs**

Document module fallback and subprocess verification evidence.

- [ ] **Step 3: Run full verification**

Run:

- `$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest -q`
- `git -C D:\ai\llmWiki\claude-obsidian status --short`
- generated artifact scan
